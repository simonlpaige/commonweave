# Agent System

Commonweave is maintained by 6 automated agents that run on a weekly cycle and feed back to each other. The feedback loop is the point - each agent's output shapes the next agent's behavior.

---

## The Agents

### Cartographer (Sun 01:00 CT)
**What it does:** Coverage intelligence. Scans the DB for thin regions (by country and framework area), detects taxonomy fragmentation, flags suspect non-org entries.

**What it produces:** `agents/reports/cartographer-latest.json`
- List of countries with fewer than 15 organizations (with severity scores)
- Taxonomy fragmentation report
- Recommended data sources per region
- Suspect org count

**Who reads it:** Scout (target regions for outreach), Curator (what's thin, what to quarantine), Synthesizer (where framework evidence is weak)

---

### Curator (Daily 03:00 CT)
**What it does:** Data quality. Runs every day, not just weekly.

**Priority order:**
1. Quarantine suspect non-orgs (roads, Reddit posts, Wikipedia articles)
2. Geocode 50 ungeocoded orgs per run via Nominatim (free, ~1 min)
3. Fix taxonomy fragmentation (normalize `democratic sovereignty` → `democratic_sovereignty` etc.)

**What it produces:** `agents/reports/curator-latest.json`
- Before/after geocoding stats
- Quarantine count
- Taxonomy fix count

**Who reads it:** Publisher (quality gate), Coordinator (data quality trend)

**Note on geocoding pace:** 50 orgs/day = ~1 minute runtime. Nominatim (OpenStreetMap) allows 1 request/second. At 50/day, it will take ~300 days to reach 70% geocoding from 19%. The batch size can be increased if faster progress is needed - the rate limit is the constraint, not the script.

---

### Scout (Mon/Wed/Fri 09:00 CT)
**What it does:** Outreach intelligence. Finds aligned projects in thin-coverage regions and generates contribution-first draft messages.

**What it does NOT do:** Send anything. Ever. All drafts go to `data/outreach-queue.json` and wait for Simon's approval.

**Approach (learned from first-round failures):**
- Lead with **contribution** ("I can add organizations from your network to the directory") not invitation ("join our framework")
- Target projects in regions where our coverage is thin - they have something to offer us, not the other way around
- Find projects that *need* a directory, not flagship projects that already have one

**What it produces:**
- `agents/reports/scout-latest.json`
- `data/outreach-queue.json` (append-only, Simon approves each item)
- Telegram notification when queue has pending items

**Approving outreach:** Set `status: "approved"` on items in `outreach-queue.json`. A separate send script (to be built) handles the actual posting.

---

### Synthesizer (Sat 02:00 CT)
**What it does:** Framework quality. Checks whether the framework docs make claims the directory data can actually support.

**Rules:**
- Areas with fewer than 50 orgs get a "needs data" flag - don't make strong claims
- Areas with 500+ orgs can make confident claims
- Areas in between get hedges added to proposals
- Never writes to framework docs directly - only proposes

**What it produces:**
- `agents/reports/synthesizer-latest.json`
- `data/trim_audit/proposals-YYYY-MM-DD.md` (Simon reviews)

---

### Publisher (Sun 08:00 CT)
**What it does:** Weekly communications drafts. Has a quality gate.

**Quality gate - holds drafts if:**
- Curator quarantined >100 orgs with no geocoding gain (bad data week)
- Synthesizer found >3 high-priority framework issues (docs need work)

**Always sends:** Telegram heartbeat with weekly stats + gate status.

**What it produces (when gate passes):**
- README update (geocoding %, country count, map link)
- Newsletter blurb (2-3 paragraphs, Simon edits and sends)
- `agents/reports/publisher-latest.json`

---

### Coordinator (Sun 10:00 CT)
**What it does:** Cross-agent synthesis. Reads all 5 reports, produces `coordinator-synthesis.json` that every agent reads before its next run. Uses gemma4:26b local (free) with DeepSeek flash as fallback.

**The feedback loop:** `coordinator-synthesis.json` → agents call `loadPriorityContext()` → each agent adjusts its targets/focus for the next cycle.

**Surfaces one thing to Simon per week** via Telegram: the single item only a human can decide (e.g., "approve outreach drafts in queue").

**What it produces:** `agents/reports/coordinator-latest.json`
- Global priorities for next cycle
- Per-agent guidance (target regions, focus areas)
- Quality score (0-100)
- Cross-agent patterns
- Contradictions

---

## The Feedback Loop Diagram

```
Sun 01:00  Cartographer  → gaps, taxonomy, suspects
           ↓
Daily      Curator       ← reads Cartographer
           ↓             → geocodes, quarantines, normalizes

Mon/Wed/Fri Scout        ← reads Cartographer (target regions)
           ↓             → queues outreach drafts

Sat 02:00  Synthesizer   ← reads Cartographer (weak areas)
           ↓             → proposes framework updates

Sun 08:00  Publisher     ← reads Curator + Synthesizer + Scout
           ↓             → drafts (if quality gate passes)
           ↓             → Telegram heartbeat (always)

Sun 10:00  Coordinator   ← reads ALL reports
           ↓             → coordinator-synthesis.json
           ↓             → Telegram: ONE Simon decision item
           
Next cycle: all agents read coordinator-synthesis.json first
```

---

## File Locations

| File | Purpose |
|------|---------|
| `agents/cartographer.js` | Cartographer agent |
| `agents/curator.js` | Curator agent |
| `agents/scout.js` | Scout agent |
| `agents/synthesizer.js` | Synthesizer agent |
| `agents/publisher.js` | Publisher agent |
| `agents/coordinator.js` | Coordinator agent |
| `agents/shared/db-utils.js` | Shared DB helpers |
| `agents/shared/report-writer.js` | Read/write agent reports |
| `agents/shared/priority-context.js` | Load coordinator guidance |
| `agents/reports/` | Latest + archived reports |
| `data/outreach-queue.json` | Scout draft queue (Simon approves) |
| `data/trim_audit/proposals-*.md` | Synthesizer proposals (Simon reviews) |
