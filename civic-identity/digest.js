// civic-identity/digest.js
// Weekly email digest for a neighborhood leader.
//
// Rendered in plain markdown (works in any mail client, easy to copy into a
// newsletter). Delivered via SMTP using nodemailer. No external tracking
// pixels, no HTML wrappers, no "view online" links: it is a civic tool, not
// a marketing channel.
//
// Content sections:
//   - This week (date range)
//   - Overdue commitments (who promised what, when it was due)
//   - New legislative matters affecting us (from legistar_matters)
//   - Open proposals needing attention
//   - Top resident issues filed in the last week
//   - Top social topics (if the connector is populated)
//   - Connector health snapshot
//
// Usage:
//   node civic-identity/digest.js --render        # print markdown to stdout
//   node civic-identity/digest.js --send          # send via SMTP
//   node civic-identity/digest.js --send --to you@example.com
//
// SMTP env:
//   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, DIGEST_TO

import nodemailer from 'nodemailer';
import { openDB } from './identity.js';
import { loadConfig } from './config.js';

export function renderDigest(db, { days = 7, now = new Date() } = {}) {
  const since = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
  const sinceIso = since.toISOString();
  const cfg = loadConfig();

  const sections = [];
  const fmtDate = d => (d ? d.slice(0, 10) : '');

  sections.push(`# ${cfg.name || cfg.slug} - weekly digest`);
  sections.push(`Window: ${fmtDate(sinceIso)} through ${fmtDate(now.toISOString())}\n`);

  // Overdue commitments
  const overdue = safeAll(db, `
    SELECT id, description, committed_by, due_date, status
    FROM legistar_commitments
    WHERE status = 'open' AND due_date IS NOT NULL AND due_date < date('now')
    ORDER BY due_date ASC LIMIT 25
  `);
  sections.push(`## Overdue commitments (${overdue.length})`);
  if (!overdue.length) sections.push('_No overdue commitments. Nice._\n');
  else {
    sections.push('');
    for (const c of overdue) {
      const who = c.committed_by || 'unknown';
      sections.push(`- ${c.description} - promised by ${who}, due ${c.due_date}`);
    }
    sections.push('');
  }

  // Resident issues
  const recentIssues = safeAll(db, `
    SELECT id, category, title, status, created_at
    FROM resident_issues
    WHERE created_at > ?
    ORDER BY created_at DESC LIMIT 25
  `, [sinceIso]);
  sections.push(`## Resident issues filed this week (${recentIssues.length})`);
  if (!recentIssues.length) sections.push('_No new issues filed._\n');
  else {
    sections.push('');
    for (const i of recentIssues) {
      sections.push(`- [${i.category}] ${i.title} (${i.status})`);
    }
    sections.push('');
  }

  // Open proposals
  const openProps = safeAll(db, `
    SELECT p.id, p.title, p.category, p.vote_method, p.closes_at, u.handle as author
    FROM proposals p LEFT JOIN users u ON p.author_id = u.id
    WHERE p.status = 'open'
    ORDER BY COALESCE(p.closes_at, '9999') ASC LIMIT 15
  `);
  sections.push(`## Open proposals (${openProps.length})`);
  if (!openProps.length) sections.push('_No open proposals._\n');
  else {
    sections.push('');
    for (const p of openProps) {
      const closes = p.closes_at ? ` (closes ${fmtDate(p.closes_at)})` : '';
      sections.push(`- ${p.title} - ${p.vote_method}${closes}, by ${p.author || '?'}`);
    }
    sections.push('');
  }

  // Legistar matters
  const recentMatters = safeAll(db, `
    SELECT id, title, status, intro_date FROM legistar_matters
    WHERE intro_date > ? ORDER BY intro_date DESC LIMIT 10
  `, [sinceIso]);
  sections.push(`## New legislative matters (${recentMatters.length})`);
  if (!recentMatters.length) sections.push('_No new matters indexed this week._\n');
  else {
    sections.push('');
    for (const m of recentMatters) {
      sections.push(`- ${m.title} - ${m.status} (introduced ${fmtDate(m.intro_date)})`);
    }
    sections.push('');
  }

  // Social topics
  const topics = safeAll(db, `
    SELECT topic_tags, COUNT(*) as cnt FROM social_posts
    WHERE posted_at > ? AND topic_tags IS NOT NULL
    GROUP BY topic_tags ORDER BY cnt DESC LIMIT 5
  `, [sinceIso]);
  if (topics.length) {
    sections.push(`## Top social topics`);
    sections.push('');
    for (const t of topics) sections.push(`- ${t.topic_tags}: ${t.cnt} mentions`);
    sections.push('');
  }

  // Connector status
  const connStatus = safeAll(db, `SELECT connector_key, status, detail, last_checked FROM connector_status`);
  if (connStatus.length) {
    sections.push(`## Connector health`);
    sections.push('');
    for (const c of connStatus) sections.push(`- ${c.connector_key}: ${c.status} (${c.detail || '-'})`);
    sections.push('');
  }

  sections.push(`---\n_Generated ${now.toISOString()}. Source: ${cfg._source}._`);
  return sections.join('\n');
}

export async function sendDigest(db, { to, days = 7 } = {}) {
  const cfg = loadConfig();
  const markdown = renderDigest(db, { days });

  const host = process.env.SMTP_HOST;
  const port = parseInt(process.env.SMTP_PORT || '587');
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  const from = process.env.SMTP_FROM || user;
  const target = to || process.env.DIGEST_TO || cfg.contactEmail;

  if (!host) throw new Error('SMTP_HOST not set');
  if (!target) throw new Error('No recipient: set --to, DIGEST_TO env, or config.contactEmail');

  const transporter = nodemailer.createTransport({
    host, port,
    secure: port === 465,
    auth: user && pass ? { user, pass } : undefined
  });

  const subject = `[${cfg.slug}] Weekly digest - ${new Date().toISOString().slice(0, 10)}`;
  const info = await transporter.sendMail({
    from, to: target, subject, text: markdown
  });
  return { messageId: info.messageId, accepted: info.accepted, to: target };
}

function safeAll(db, sql, params = []) {
  try { return db.prepare(sql).all(...params); }
  catch { return []; }
}

// ----------------------------------------------------------------
// CLI
// ----------------------------------------------------------------

const isMain = import.meta.url === `file://${process.argv[1]?.replace(/\\/g, '/')}`
            || import.meta.url.endsWith(process.argv[1]?.replace(/\\/g, '/'));

if (isMain) {
  const args = process.argv.slice(2);
  const DB_PATH = process.env.DB_PATH || './civic-identity.db';
  const daysIdx = args.indexOf('--days');
  const days = daysIdx > -1 ? parseInt(args[daysIdx + 1]) : 7;
  const toIdx = args.indexOf('--to');
  const to = toIdx > -1 ? args[toIdx + 1] : null;

  const db = openDB(DB_PATH);
  try {
    if (args.includes('--send')) {
      const result = await sendDigest(db, { to, days });
      console.log(`Sent to ${result.to} (messageId ${result.messageId})`);
    } else {
      console.log(renderDigest(db, { days }));
    }
  } finally {
    db.close();
  }
}
