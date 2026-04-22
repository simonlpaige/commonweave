// civic-identity/ballot-pdf.js
// Paper-ballot generator (review recommendation #20).
//
// Many residents will not vote online. A neighborhood association running
// their first federated proposal needs to hand out paper. This module
// generates a one-page ballot PDF with:
//   - Proposal title, category, and body (truncated to fit)
//   - The vote method and instructions
//   - The options or a yes/no/abstain box for binary
//   - A QR code encoding proposal id + body hash so the coordinator entering
//     the vote can scan-verify they are entering it against the right
//     proposal and it has not been edited.
//
// The coordinator's flow: residents mark paper at the table, coordinator
// scans the QR (which lands them on /proposals/<id>) and types the votes
// back in. This module does not do ballot harvesting or electronic scan;
// that is a bigger surface area and not in scope.

import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import QRCode from 'qrcode';
import { getProposal } from './voting.js';

// Width/height in points (72pt = 1in). Letter size.
const PAGE_W = 612;
const PAGE_H = 792;
const MARGIN = 54; // 0.75in

export async function renderBallotPdf(db, proposalId, { baseUrl = null } = {}) {
  const proposal = getProposal(db, proposalId);
  if (!proposal) throw new Error('Proposal not found');
  if (!['open', 'draft'].includes(proposal.status)) {
    throw new Error(`Cannot issue ballot for a ${proposal.status} proposal`);
  }

  const options = db.prepare(
    `SELECT * FROM vote_options WHERE proposal_id = ? ORDER BY sort_order`
  ).all(proposalId);

  const pdf = await PDFDocument.create();
  const page = pdf.addPage([PAGE_W, PAGE_H]);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const bold = await pdf.embedFont(StandardFonts.HelveticaBold);

  let y = PAGE_H - MARGIN;

  // Header
  drawText(page, 'Neighborhood Ballot', { font: bold, size: 20, x: MARGIN, y });
  y -= 28;
  drawText(page, `Proposal: ${proposal.title}`, {
    font: bold, size: 13, x: MARGIN, y, maxWidth: PAGE_W - 2 * MARGIN
  });
  y -= 20;
  drawText(page, `Category: ${proposal.category}   Method: ${proposal.vote_method}   Min trust: ${proposal.min_trust}`, {
    font, size: 10, x: MARGIN, y, color: rgb(0.3, 0.3, 0.3)
  });
  y -= 18;

  // Body (wrapped, truncated if too long)
  y = drawWrapped(page, font, 10, proposal.body, MARGIN, y, PAGE_W - 2 * MARGIN, 14, 10);
  y -= 12;

  // Divider
  page.drawLine({
    start: { x: MARGIN, y },
    end:   { x: PAGE_W - MARGIN, y },
    thickness: 0.5, color: rgb(0.6, 0.6, 0.6)
  });
  y -= 22;

  // Instructions + options
  drawText(page, 'Mark your choice clearly. Only one mark per box.', { font: bold, size: 11, x: MARGIN, y });
  y -= 20;

  if (proposal.vote_method === 'binary' || proposal.vote_method === 'liquid') {
    y = drawCheckboxRow(page, font, ['Yes', 'No', 'Abstain'], MARGIN, y);
  } else if (options.length) {
    // Approval / ranked / score: one box per option plus a writable rank/score line.
    for (const opt of options) {
      const labelLine = proposal.vote_method === 'ranked'
        ? `Rank ____    ${opt.label}`
        : proposal.vote_method === 'score'
          ? `Score 0-10 ____    ${opt.label}`
          : `[  ]    ${opt.label}`;
      drawText(page, labelLine, { font, size: 11, x: MARGIN, y, maxWidth: PAGE_W - 2 * MARGIN - 100 });
      if (opt.description) {
        y -= 14;
        drawText(page, opt.description, {
          font, size: 9, x: MARGIN + 12, y, color: rgb(0.35, 0.35, 0.35),
          maxWidth: PAGE_W - 2 * MARGIN - 120
        });
      }
      y -= 18;
    }
  } else {
    drawText(page, '(No options configured. Contact your coordinator.)', { font, size: 10, x: MARGIN, y });
    y -= 16;
  }

  // Signature line for residents who want to self-certify they voted once.
  // The coordinator is still the one keying it in.
  y -= 20;
  page.drawLine({ start: { x: MARGIN, y }, end: { x: MARGIN + 240, y }, thickness: 0.5 });
  drawText(page, 'Signature (optional)', { font, size: 8, x: MARGIN, y: y - 10, color: rgb(0.4, 0.4, 0.4) });

  // QR code bottom-right: encode a URL so a smartphone scan lands on the
  // proposal detail page. Body_hash prefix is embedded so the coordinator
  // can spot-check they have the right proposal on the right day.
  const bodyHashPrefix = (proposal.body_hash || '').split(':')[0].slice(0, 12);
  const qrPayload = baseUrl
    ? `${baseUrl.replace(/\/$/, '')}/proposals/${proposal.id}#h=${bodyHashPrefix}`
    : `proposal:${proposal.id}#h=${bodyHashPrefix}`;
  const qrPng = await QRCode.toBuffer(qrPayload, { margin: 1, width: 180 });
  const qrImg = await pdf.embedPng(qrPng);
  const qrSize = 120;
  page.drawImage(qrImg, {
    x: PAGE_W - MARGIN - qrSize,
    y: MARGIN,
    width: qrSize, height: qrSize
  });
  drawText(page, 'Scan to verify', {
    font, size: 8, x: PAGE_W - MARGIN - qrSize, y: MARGIN - 10, color: rgb(0.3, 0.3, 0.3)
  });

  // Footer with proposal id + hash so a coordinator can correlate paper to DB
  drawText(page, `Proposal id: ${proposal.id}`, {
    font, size: 7, x: MARGIN, y: MARGIN - 10, color: rgb(0.4, 0.4, 0.4)
  });
  drawText(page, `Body hash prefix: ${bodyHashPrefix}`, {
    font, size: 7, x: MARGIN, y: MARGIN - 20, color: rgb(0.4, 0.4, 0.4)
  });

  return pdf.save();
}

// ----------------------------------------------------------------
// helpers
// ----------------------------------------------------------------

function drawText(page, text, { font, size = 10, x, y, color = rgb(0, 0, 0), maxWidth = null }) {
  const t = maxWidth ? truncateToWidth(text, font, size, maxWidth) : text;
  page.drawText(sanitize(t), { font, size, x, y, color });
}

function drawCheckboxRow(page, font, labels, x, y) {
  const boxSize = 14;
  let cx = x;
  for (const label of labels) {
    page.drawRectangle({
      x: cx, y: y - 2, width: boxSize, height: boxSize,
      borderColor: rgb(0, 0, 0), borderWidth: 1
    });
    page.drawText(label, { font, size: 11, x: cx + boxSize + 6, y });
    cx += boxSize + 6 + font.widthOfTextAtSize(label, 11) + 36;
  }
  return y - 28;
}

function drawWrapped(page, font, size, text, x, startY, maxWidth, lineHeight, maxLines) {
  const words = sanitize(text).split(/\s+/);
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (font.widthOfTextAtSize(test, size) > maxWidth) {
      if (line) lines.push(line);
      line = w;
    } else {
      line = test;
    }
    if (lines.length >= maxLines) break;
  }
  if (line && lines.length < maxLines) lines.push(line);
  let y = startY;
  for (const l of lines) {
    page.drawText(l, { font, size, x, y });
    y -= lineHeight;
  }
  if (words.length > lines.reduce((n, l) => n + l.split(/\s+/).length, 0)) {
    page.drawText('(continues, see full text online)', { font, size: size - 1, x, y, color: rgb(0.4, 0.4, 0.4) });
    y -= lineHeight;
  }
  return y;
}

function truncateToWidth(text, font, size, maxWidth) {
  let t = sanitize(text);
  if (font.widthOfTextAtSize(t, size) <= maxWidth) return t;
  while (t.length > 4 && font.widthOfTextAtSize(t + '…', size) > maxWidth) t = t.slice(0, -1);
  return t + '…';
}

// pdf-lib's standard fonts are WinAnsi-only. Replace characters outside
// that set so we do not crash on smart quotes, em dashes, etc.
function sanitize(s) {
  return String(s ?? '')
    .replace(/[\u2018\u2019\u02BC]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2026/g, '...')
    .replace(/[\u2013\u2014]/g, '-')
    .replace(/[^\x00-\x7F]/g, '?');
}
