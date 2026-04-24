# Brief: "A Field Guide to Labor-for-Housing Cooperatives"

You are Claude Code. This brief is the source of truth. Read it once, then execute.

## Mission

Write a **20-40 page companion guide** to `pipeline.pdf`, titled **"A Field Guide to Labor-for-Housing Cooperatives."** Same Feynman voice, same design language, same rendering pipeline (Markdown → PDF with diagrams).

Audience: unions considering a housing program, CLTs considering a labor-intake program, displaced workers looking for real options, journalists, policy folks. Plain language. Someone with no background should finish it and understand both the mechanics and the history.

This is the document that turns Commonweave from a directory into a field manual.

## Why this document

AI displacement is accelerating. Housing shortages are worsening. Labor unions, community land trusts, and sweat-equity programs each solve a piece. Stitched together, they form a vertical pipeline: people work for unions or CLTs, contribute labor to build and repair housing, and earn homes in exchange. This pattern exists in fragments in ~40 countries. No one has documented the full playbook. We will.

## Hard rules

1. **Don't start unless the land-ingest commits are in both repos.** Check with `git log --oneline -5`. If the land ingest isn't done, STOP and announce: `openclaw system event --text "guide blocked - land ingest not committed" --mode now`.
2. **Cite the directory.** Every claim of "this pattern exists" must link to at least one real org in the Commonweave directory (which you just ingested in the previous two runs). Query the DB if needed: `sqlite3 commonweave/data/commonweave_directory.db`.
3. **Feynman voice.** No em dashes. No "leverage," "unlock," "empower." Kitchen-table language.
4. **Honest document, not marketing.** Include failure modes and dark history prominently.
5. **~20-40 pages, not more.** If it's getting longer, cut.

## What to read first

- `commonweave/PIPELINE.md` and `commonweave/pipeline.pdf` (for style/voice reference)
- `commonweave/BLUEPRINT.md`
- `commonweave/THEORY-OF-CHANGE.md`
- `commonweave/RESEARCH.md`
- `commonweave/DEEP-DIVE.md` (skim)
- `modules/commonweave/CONTEXT.md`
- `commonweave/GOVERNANCE.md`
- `commonweave/CRITIQUE.md` (important — understand existing self-critique)
- A sampling of the newly-ingested orgs (query the DB for 10-20 in each category)

## Structure (suggested; deviate if better structure emerges)

### Cover page
Title, subtitle ("How to stitch labor, land, and housing into one democratic pipeline"), date.

### Part 1: The problem, honestly stated (2-3 pages)
- The unemployment trend and why AI displacement changes the math
- The housing shortage in plain numbers
- Why these two problems sit next to each other and don't solve each other by default
- One-sentence thesis: democratic ownership of land, combined with organized labor, can convert surplus hours into permanent housing

### Part 2: The three legs of the stool (4-6 pages)
One short chapter each. For each leg: what it is, who does it now (with 2-3 named examples from the Commonweave directory), how it's funded, where it breaks.
- **Community Land Trusts**: permanent affordability through detached land ownership. Examples: Dudley Street (Boston), Champlain Housing Trust (Vermont), and pick 1-2 international.
- **Labor unions (construction trades especially)**: organized skill. Examples: a US carpenters' local, IG Metall's housing programs if they exist, Mondragon's construction co-ops.
- **Sweat-equity programs**: Habitat for Humanity is the canonical example. Also less-famous variants.

### Part 3: The pipeline, diagrammed (3-4 pages)
- One full-page diagram showing the flow: member joins union → union has labor-sharing agreement with CLT → CLT owns land → member contributes N hours → member gets lease at permanent affordability → member continues contributing on neighborhood repair crew.
- Walk through the diagram in text afterward.
- Use Mermaid or Graphviz (same pipeline as `pipeline.pdf`).

### Part 4: The legal scaffolding (3-4 pages)
Plain-language explanation of the legal structures that make it work.
- 501(c)(3) CLT (US) / equivalent in other countries
- Housing cooperative vs. condo vs. CLT (the differences matter)
- Worker cooperative legal structures
- How labor hours are credited (escrow accounts, sweat-equity notes, informal tracking)
- Liability and insurance (the boring stuff that kills projects)

### Part 5: The math (2-3 pages)
- How many labor hours to build a home? (Habitat's number: ~400 hours including the homeowner's contribution)
- How CLTs price "affordable"? (median household income formulas, resale restrictions)
- How unions could pay union wages for non-pipeline work and contribute hours for pipeline work
- Rough budget for a 10-home pilot

### Part 6: How to start one (4-5 pages)
Numbered steps, ordered by who's already organized.
- If you're a union local: how to approach a CLT, what partnership looks like
- If you're a CLT: how to approach a union, what the skill-matching problem looks like
- If you're neither: who to find, in what order
- Minimum viable pilot: 3-5 homes, 18-month timeline, named partnerships

### Part 7: Failure modes and dark history (3-4 pages)
**This section is critical — don't soften it.**
- Company towns and the history of housing-for-labor coercion in the US
- Habitat for Humanity's paternalism critiques (theological framing, homeowner debt, gentrification effects)
- CLT gentrification-resistance failures (some CLTs have become de facto gentrification agents in hot markets)
- Sweat-equity and disability access (not everyone can swing a hammer)
- Union corruption and closed-shop exclusion (trades have ugly racial histories to reckon with)
- Where AI/agent coordination could make it worse (opacity, data extraction, reinforcing existing exclusions)
- **The firewall**: democratic ownership of the land, by the residents, with resale restrictions. Without that, it's extraction dressed up.

### Part 8: What Commonweave does and doesn't do (2 pages)
- What Commonweave is: a directory of orgs already doing this + a framework document + this field guide
- What Commonweave isn't: a platform, a broker, a funder, a standards body (yet)
- The Tier 3 coordination tool as a future option, gated on a real pilot partner stepping forward

### Appendix A: Directory quick-query
Short reference for readers: "here's how to pull a list of CLTs in your state from commonweave.earth/directory."

### Appendix B: Further reading
5-10 books/papers/orgs. Real citations, not filler.

### Back page
Links: commonweave.earth, commonweave.earth/directory, commonweave.earth/pipeline.pdf. Contact: whatever outreach email is in the OUTREACH.md.

## Build approach

Same pipeline as `pipeline.pdf`:

- Write as Markdown at `commonweave/LABOR-FOR-HOUSING-GUIDE.md` first
- Render to PDF at `commonweave/labor-for-housing-guide.pdf`
- Diagrams in `commonweave/assets/` with `.mmd` + `.svg` + `.png`
- Copy PDF to `simonlpaige.github.io/commonweave/labor-for-housing-guide.pdf`

Add a link to the guide from:
- `commonweave/index.html` (hero area or resources section)
- `commonweave/directory.html` (near the pipeline.pdf link)
- `commonweave/doc.html` if it has a resources section

Mirror edits to the live-site repo.

## Done checklist

- [ ] Land-ingest commits exist (precondition)
- [ ] `LABOR-FOR-HOUSING-GUIDE.md` exists, well-written, cites directory orgs
- [ ] `labor-for-housing-guide.pdf` renders cleanly, embedded diagrams look good
- [ ] Diagrams saved in `commonweave/assets/`
- [ ] PDF copied to live-site repo
- [ ] Index + directory + doc pages link to the guide in both repos
- [ ] Workspace repo committed + pushed (Feynman voice, one good first line)
- [ ] Live-site repo committed + pushed
- [ ] At end, run: `openclaw system event --text "Done: Labor-for-housing guide shipped. Ready for Codex red-team pass across unions, land, and guide." --mode now`

## Karpathy rules

1. State assumptions. Ask when unclear.
2. Minimum content. Cut if getting long.
3. Surgical edits. Don't rewrite existing docs.
4. "Done" checklist is your verifier.

## If you get stuck

- Missing directory orgs to cite? Check the DB — the previous runs should have populated 500-2000 new orgs. If the DB is empty, something broke upstream.
- Can't find a specific number (e.g. "how many hours to build a Habitat home")? Do the research. Cite a real source. Don't make up numbers.
- Dark-history section getting uncomfortable? That's right. Don't soften. Get it checked by Codex red-team after.
