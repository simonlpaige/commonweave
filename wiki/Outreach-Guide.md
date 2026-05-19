# Outreach Guide

How Commonweave reaches out to allied projects, what we learned from early failures, and how the Scout agent does it now.

---

## What We Learned from Round 1

In April 2026 we sent GitHub issues to Decidim, Open Food Network, ElectionGuard, and Open Source Ecology. Results:

- Decidim: issue closed, 0 comments
- ElectionGuard: open, 0 comments
- Open Source Ecology: open, 0 comments
- Open Food Network: closed with 6 comments (the only one that got a response)

**The diagnosis:** The messages were pitch-shaped. The titles said "Invitation to collaborate" - which translates to "come be part of our thing." These are mature projects with long contributor queues. An invitation from a tiny new project is noise.

Open Food Network responded because the message offered something concrete: a specific question about their work, an offer to correct our representation of it, and genuine curiosity about their deployment experience. That's what worked.

---

## The New Approach: Contribution-First

Every outreach starts with what we can offer, not what we want.

**The offer is always specific:**
- "We can add organizations from your network to an open global directory, with attribution to your project as the source"
- "Is anything in our coverage of your region wrong or missing?"
- "We'd like to correct our summary of your work - here's what we have, tell us what's off"

**We never ask:**
- "Would you like to collaborate?"
- "Would you be interested in our framework?"
- "Can we integrate with your project?"

These are invitation-shaped questions and they go nowhere.

---

## Who We Target (and Why)

The Scout agent reads the Cartographer's coverage gap report before finding targets. This matters:

**Good targets:**
- Regional cooperative federations in countries where we have <15 orgs (they have data we need)
- Small mutual aid networks that aren't in any formal registry (they benefit from being findable)
- Organizations that maintain their own lists of allied orgs (we can offer to consolidate/link)

**Bad targets (what Round 1 got wrong):**
- Flagship open-source projects (Decidim, OpenMRS, etc.) - they're already well-documented and don't need our directory
- Projects with no connection to a specific geographic region (they can't fill our regional gaps)

---

## The Scout Agent

The Scout runs Mon/Wed/Fri and searches GitHub for aligned repositories in thin-coverage regions. It generates draft messages and puts them in `data/outreach-queue.json` with `status: "pending_approval"`.

**Nothing sends automatically.** Simon reviews the queue and approves each draft.

**The queue file:**
```json
{
  "to": "org/repo-name",
  "platform": "github",
  "channel": "issues",
  "subject": "...",
  "body": "...",
  "target_region": "africa",
  "status": "pending_approval",
  "queued_at": "2026-05-19T..."
}
```

To approve: change `status` to `"approved"`. (A send script will be built to handle the actual posting.)

---

## Outreach Principles (from OUTREACH.md)

1. **Lead with respect.** These projects have been doing this work for years. We're newcomers.
2. **Be specific.** Not "collaboration" - exactly what we can offer and what we want to learn.
3. **Be transparent.** Commonweave is open-source, small, and has no funding. Say this upfront.
4. **No pressure.** Silence is a valid response.
5. **Credit everything.** When integrating ideas from other projects, cite them prominently.

---

## Tracking Responses

All outreach history is in `outreach-ledger.json` (machine-readable) with a generated view at `outreach-log.md`.

States:
- `pending_approval` - draft in queue, not sent
- `sent` - sent, awaiting response
- `responded_positive` - they replied, something to follow up on
- `responded_closed` - they replied, conversation complete
- `closed_no_response` - no response after 2 weeks + one follow-up
- `declined` - they passed, noted with thanks

---

## What Success Looks Like

Not "they joined our framework." 

Success is:
- They told us something was wrong with our coverage and we fixed it
- They let us add their network's organizations with attribution
- They asked a question about the directory that shows it's useful to them
- A contributor from their community showed up in our repo

The directory succeeds when it becomes useful to the people in it, not when the framework gets famous.
