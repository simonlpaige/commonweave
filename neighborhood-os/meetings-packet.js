// neighborhood-os/meetings-packet.js
// Assemble a single PDF "packet" for a given Legistar event: a cover page
// with meeting metadata, followed by the agenda PDF and the minutes PDF
// (whichever Legistar already hosts).
//
// Why: "there is no printable report" was one of the usability drifts
// flagged in the deep-dive review. A neighborhood board wants to print ONE
// document for tonight's meeting, not hunt through URLs.

import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import { fetchJson } from './connectors/_fetch.js';

const PAGE_W = 612;
const PAGE_H = 792;
const MARGIN = 54;

export async function buildMeetingPacket(db, eventId) {
  const event = db.prepare(`SELECT * FROM legistar_events WHERE id = ?`).get(eventId);
  if (!event) throw new Error(`Event ${eventId} not found in local DB. Run sync first.`);

  const agendaUrl = event.agenda_url;
  const minutesUrl = event.minutes_url;

  const packet = await PDFDocument.create();

  // Cover page
  const cover = packet.addPage([PAGE_W, PAGE_H]);
  const bold = await packet.embedFont(StandardFonts.HelveticaBold);
  const font = await packet.embedFont(StandardFonts.Helvetica);
  let y = PAGE_H - MARGIN;
  cover.drawText('Meeting Packet', { font: bold, size: 22, x: MARGIN, y });
  y -= 32;
  cover.drawText(sanitize(event.body_name || 'Unknown body'), { font: bold, size: 14, x: MARGIN, y });
  y -= 22;
  cover.drawText(`Date:     ${event.event_date || 'TBD'}`, { font, size: 11, x: MARGIN, y }); y -= 16;
  cover.drawText(`Location: ${sanitize(event.location || '(location TBD)')}`, { font, size: 11, x: MARGIN, y }); y -= 24;

  const blockWidth = PAGE_W - 2 * MARGIN;
  cover.drawText('Contents (in order):', { font: bold, size: 12, x: MARGIN, y }); y -= 18;
  cover.drawText(`  1. This cover page`, { font, size: 11, x: MARGIN, y }); y -= 14;

  let idx = 2;
  const sources = [];
  if (agendaUrl) {
    sources.push({ label: 'Agenda', url: agendaUrl });
    cover.drawText(`  ${idx}. Agenda (from Legistar)`, { font, size: 11, x: MARGIN, y }); y -= 14; idx++;
  }
  if (minutesUrl) {
    sources.push({ label: 'Minutes', url: minutesUrl });
    cover.drawText(`  ${idx}. Minutes (from Legistar)`, { font, size: 11, x: MARGIN, y }); y -= 14; idx++;
  }
  if (!sources.length) {
    cover.drawText(`  (No agenda or minutes document hosted for this event yet.)`, {
      font, size: 11, x: MARGIN, y, color: rgb(0.5, 0.2, 0.2)
    });
    y -= 14;
  }
  y -= 10;
  cover.drawText('Source: KC Legistar. Printed for neighborhood distribution.', {
    font, size: 9, x: MARGIN, y, color: rgb(0.35, 0.35, 0.35)
  });
  cover.drawText(`Event id: ${event.id}`, {
    font, size: 8, x: MARGIN, y: MARGIN, color: rgb(0.4, 0.4, 0.4)
  });

  const warnings = [];

  for (const src of sources) {
    try {
      const bytes = await fetchPdfBytes(src.url);
      const doc = await PDFDocument.load(bytes, { ignoreEncryption: true });
      const pages = await packet.copyPages(doc, doc.getPageIndices());
      for (const p of pages) packet.addPage(p);
    } catch (err) {
      // If a remote PDF fails to load, stamp a note page in place of it so
      // the printed packet makes clear what is missing.
      warnings.push(`${src.label}: ${err.message}`);
      const page = packet.addPage([PAGE_W, PAGE_H]);
      page.drawText(`${src.label} document could not be loaded.`, {
        font: bold, size: 14, x: MARGIN, y: PAGE_H / 2 + 20, color: rgb(0.5, 0.15, 0.15)
      });
      page.drawText(sanitize(err.message), {
        font, size: 10, x: MARGIN, y: PAGE_H / 2 - 10, maxWidth: PAGE_W - 2 * MARGIN
      });
      page.drawText(`Source URL: ${sanitize(src.url)}`, {
        font, size: 9, x: MARGIN, y: PAGE_H / 2 - 30, color: rgb(0.3, 0.3, 0.3)
      });
    }
  }

  const bytes = await packet.save();
  return { bytes, warnings, pages: packet.getPageCount() };
}

async function fetchPdfBytes(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30_000);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const ab = await res.arrayBuffer();
    if (ab.byteLength > 25 * 1024 * 1024) {
      throw new Error('document larger than 25MB cap');
    }
    return new Uint8Array(ab);
  } finally {
    clearTimeout(timer);
  }
}

function sanitize(s) {
  return String(s ?? '')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2026/g, '...')
    .replace(/[\u2013\u2014]/g, '-')
    .replace(/[^\x00-\x7F]/g, '?');
}
