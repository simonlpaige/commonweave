# Claude V2 Final Pass Report - Labor-for-Housing Field Guide

Run: 2026-04-24
Model: Claude Opus 4.7 (1M context), extended thinking
Input: v1.5 of `commonweave/LABOR-FOR-HOUSING-GUIDE.md`, DeepSeek's red-team and v2 plan, Sonnet's triage
Bar: ship v2 tonight; only execute changes that materially improve honesty, truthfulness, or effectiveness; no spine restructure for the sake of it

---

## Final pass report

### 1. Effectiveness verdict: would this house people who can't afford housing now?

**Qualified yes, at a small scale, for a specific subset of people.**

Honest answer in three parts.

**At pilot scale, in places with the right ingredients, the pipeline works.** The constituent pieces are not theoretical. CLTs hold land at permanent affordability and have done so for forty years (Champlain has 3,000+ homes; Dudley has held a Boston neighborhood for a third of a century). Habitat affiliates have credited sweat-equity hours toward homes for fifty years. Project labor agreements are routine. Worker construction cooperatives in Mondragon and the Italian co-op federations build at industrial scale. None of this is hypothetical. A pilot of 3-10 homes, with a willing CLT, one to three trades locals, public land or a long ground lease, and a real subsidy stack, in 18-24 months, is achievable. The guide's operational scaffolding (Red Flag Checklist, Compliance Matrix, RACI) is genuinely useful for a team that can do this work.

**At national scale, against a 5-7M home shortage, this is not a solution.** The guide already says so in Part 1, which I think is correct and honest. The arithmetic is: a heroic pilot produces ~10 homes per 18 months at $5-8M of subsidy. Even if every CLT in the US ran a pipeline of this kind, the throughput is in the low thousands of units per year. The acute housing crisis is in tens of millions of households cost-burdened and in millions of homes short. This pipeline is one tool. It is not the tool.

**Worse, the people the housing crisis hurts most are the people the pipeline can least reach.** Single parents with no childcare, people in immediate housing crisis with no buffer, people displaced into geographies with no CLT or trades local within commute distance, people whose chronic illness makes the alternate-hours menu unworkable: the guide's own honest list of "who this can't help" maps almost perfectly onto the populations most squeezed by the housing crisis. Pilots that target 80% AMI-by-default, in places where the CLT has gotten land easily, end up housing relatively-stable working-class families on the way up, not the families being displaced. The guide names this and that's the right move; what it cannot do is solve it.

So: yes for who it can reach. No for the housing crisis as such. The guide as it stands is honest about both.

The single largest risk to effectiveness is something the guide cannot fix: **the political fight for land**. A 3-5 year campaign for one ground lease, against organized developer and NIMBY opposition, is the actual gate. If a community cannot win that fight, the rest of the pipeline is academic. Part 6's "find the land" note now acknowledges this; a v3 should have a real political-strategy appendix. (DeepSeek's v2 plan called for this and was right; I declined to draft it tonight because the right way to do it is with verifiable case studies, which I don't have time to verify.)

### 2. Has the document improved? Compared to what?

Yes, materially, across all four passes.

- **v1 (pre-Wave-1):** Had a wrong IRS revenue ruling cite (Rev Rul 75-493) that did not in fact address sweat equity, defaulted to LIHTC as a homeownership subsidy source (LIHTC is a rental credit), and described the union-PLA-plus-contributed-hours stack as "clean" without compliance gates. A housing-finance professional reading v1 would have closed the PDF on the LIHTC line.
- **Wave 1** killed the wrong cite, removed LIHTC as default, and added the Legal Review Required callout with the $25-75K budget guidance. This was the largest single credibility win.
- **Wave 2** added the Red Flag Checklist (16 do-not-proceed gates), the 15-row Labor Compliance Matrix, and the 21-row Construction Delivery RACI. This shifted the doc from advocacy to field-usable.
- **Wave 3 (DeepSeek-flagged credibility fixes)** added care-work-as-structural framing, the 80% AMI / justice-standard distinction, the Indigenous-land subsection, the firewall-control-vs-veto distinction, the wealth-building tradeoff, the "find the land is a political fight" note, and the SEWA-as-informal-sector clarification.
- **This pass (v2 final)** lifted the "who this can't help" content from buried subsections in Part 2 and Part 7 into a prominent Part 1 section; replaced the AI-displacement opening with a housing-cost lead; added a one-paragraph wealth-building tradeoff pointer in Part 1 so readers see it before they get invested; added a cost-of-entry note in Part 6 with concrete pro-bono pathways; cut the IG Metall padding paragraph; and compressed Part 8 from a Commonweave self-description into a brief honest "about this guide" note.

**Where it is still weak:**

- The guide remains overwhelmingly US-focused in its legal scaffolding. Appendix C is a stub. Non-US readers can use it for the questions, not the answers.
- The political-strategy material is still gestural. The "find the land" note acknowledges the fight but does not teach anyone how to win one. A genuine campaign anatomy is v3 work.
- The "if you are neither" section in Part 6 still reads as if individual readers can plausibly start a pipeline. The cost-of-entry note partially addresses this but the underlying truth is harsher: an individual without an organization or institutional patron almost certainly cannot start one alone, and the guide could be sharper about that.
- The math section assumes a single-family stick-built typology. DeepSeek's plan to add a climate/density/typology section is reasonable; tonight I did not draft one because I would have had to invent or borrow per-unit carbon numbers I could not verify, and that is exactly the failure mode Wave 1 was cleaning up.
- The directory is described honestly (1,700 verified out of 27,000) but the guide could not, in this pass, do anything to actually improve verification rates. That is a Commonweave roadmap item, not a guide-text problem.

### 3. Honesty audit: where v1.5 was not quite honest, and what changed

**Where v1.5 was misleading and I changed it:**

1. **The opening framed the housing problem around AI-displacement specifically** ("language models and cheap robots are eating the bottom rungs..."). This dated the guide to a 2025-26 narrative moment, alienated union readers who don't buy that diagnosis, and put the guide in the position of selling an AI-doom story it cannot back. **Changed:** rewrote the opening to lead with housing affordability, kept "industries restructuring, work that used to pay enough now paying less" as the labor-side story, dropped the LLM/robot framing.

2. **The "who can't be served" content was scattered through Part 2 and Part 7 where first-time readers wouldn't see it in time to decide whether the guide was for them.** The honest list of populations the model excludes (single parents without childcare, people in acute housing crisis, geographic-mismatch workers) was real but buried. **Changed:** lifted into a prominent Part 1 section "Who this pipeline can reach, and who it currently can't" with both an "ideal participant" list and a "currently does not work for" list, plus an explicit "if this is not for you, this guide is not the answer" closer.

3. **The wealth-building tradeoff was honestly named but only in Part 7, after a reader had already invested in the model.** A prospective applicant reading v1.5 from front to back wouldn't hit the "permanent wealth exclusion" framing until page 25. **Changed:** added a one-paragraph "One thing to know up front about money" section in Part 1, with a pointer to the full Part 7 discussion.

4. **The $25-75K legal budget was named in the front-matter callout but never softened or addressed as a class barrier.** A displaced worker reading the callout would (correctly) decide the model was not for them and stop reading. **Changed:** added a "Note on the cost of entry" subsection in Part 6 with five concrete pro-bono pathways (law school clinics, state bar pro bono, CDFI technical assistance, law firm pro bono adoption, community development legal fellowships), with the honest caveat that none of them are guaranteed.

5. **Part 8 read like Commonweave marketing in a field guide** - three paragraphs of "what Commonweave is," four bullets of "what Commonweave isn't," and a Tier 3 coordination tool roadmap that does not belong in a practitioner's PDF. **Changed:** compressed to three paragraphs total - directory caveat, what Commonweave is and isn't, and a brief note on coordination platforms. Kept the directory verification disclosure because it is genuinely important.

6. **The IG Metall paragraph in Part 2 added no substance** - it was using the metalworkers' union as a "template" for federation, which is not actually how a labor-for-housing pipeline would use it, and reading more like directory padding than guidance. **Changed:** cut entirely. IG BAU paragraph stayed and was lightly tightened.

7. **The "robust" in Part 4 was AI-style language** (one of Simon's banned words). **Changed:** to "toughest configuration for permanent affordability to break."

**Where v1.5 was already honest and I left it:**

- The firewall section (Part 7) already distinguishes voice / veto / control with appropriate sharpness. DeepSeek's v2 plan suggested further tightening; I think the current language is adequate and further changes would be tinkering.
- The dark-history chapter is appropriately unsparing and is the guide's strongest asset. Did not touch.
- The Red Flag Checklist, Labor Compliance Matrix, and RACI are operational-grade. Did not touch.
- The "we don't know yet" hedges around sweat-equity tax treatment and Davis-Bacon volunteer interaction are already in place from Waves 1-3. Did not touch.
- The Indigenous-land subsection in Part 6 is honest about what the guide can and cannot do. Did not move it.
- The 80% AMI / 60% AMI justice-standard discussion in Part 5 is already pointed. Did not touch.

**Where I am still uncertain about honesty and am flagging:**

- The pipeline's claim of producing homes for "60-70% of open-market cost" comes from Habitat's institutional history. I have not verified that figure independently. The guide now says "depending on volunteer labor, donated materials, and local construction costs" via earlier waves' edits, which I think is enough hedging, but a fact-check pass before publication would be wise.
- The ~400-hour Habitat sweat-equity figure is widely cited but varies enormously by affiliate. The guide says "around 300 to 500 hours" with affiliate variance, which I think is accurate.
- The "27,000 entries / 1,700 verified" directory numbers are Simon's. I cannot independently verify them.

### 4. Changes I made (itemized)

**Front matter:**
- Bumped version from "Version 1" to "Version 2" (line 11).

**"What you are holding" section:**
- Replaced the AI-displacement opening with a housing-cost lead. Removed "language models and cheap robots are eating the bottom rungs" framing.
- Added a one-paragraph honest scope note: "this guide is about new construction on land taken out of the speculative market. It is not the only or fastest tool. Vacancy taxes, rent stabilization, public acquisition of empty units, public housing investment are also necessary, will move more people faster in many crisis markets, etc."
- Added a brief acknowledgment of the pipeline metaphor ("we call it a pipeline for short; some prefer pathway or cycle; the word matters less than the fact that the pieces fit").

**Part 1, "Work is getting weirder" subsection:**
- Removed AI-displacement specifics (junior software engineering, call centers, translation, basic legal drafting). Replaced with a more general "industries restructuring, white-collar work being automated faster than people can retrain, trades work shielded for now but with its own apprenticeship-pipeline problem" framing.

**Part 1, new "Who this pipeline can reach, and who it currently can't" section:**
- New section, ~250 words. Lists ideal-participant criteria (schedule flexibility, physical or admin capacity, geographic proximity, pre-existing housing buffer). Lists exclusions (immediate-crisis applicants, single parents without childcare, people whose chronic illness makes alternate hours unworkable, geographic-mismatch applicants, white-collar displacement with no construction path). Explicitly says these are design gaps, not moral failings, and that some are solvable.

**Part 1, new "One thing to know up front about money" section:**
- New ~120-word section that pulls the wealth-building tradeoff up from Part 7. Names "permanent affordability for the next family" / "permanent wealth exclusion for the current family" both as accurate descriptions. Points to Part 7 for the fuller discussion.

**Part 1, "The one-sentence thesis":**
- Changed "convert surplus hours into permanent homes" to "convert hours that have nowhere else to go into permanent homes." "Surplus hours" was treating labor as commodity; the new phrasing keeps the accessibility of the metaphor without the dehumanization.

**Part 2, Leg 2 (Labor unions):**
- Cut the IG Metall paragraph entirely as padding.
- Lightly tightened the IG BAU paragraph (removed the "successor to a building-trades union folded into DGB after WWII" specifics, which were trivia).

**Part 4, "Housing cooperative versus condo versus CLT":**
- "Most robust configuration" -> "toughest configuration to break" to remove banned AI-style word.

**Part 6, new "A note on the cost of entry" subsection:**
- New ~200-word subsection inserted between the Part 6 opener and "If you are a union local." Lists five pro-bono pathways. Notes none are guaranteed. Explicitly says individuals without institutional capital cannot start cold and the work is finding the institution first.

**Part 8, "About this guide" (replaced "What Commonweave does and doesn't do"):**
- Cut from ~600 words (3 sections, 4 bullets, Tier 3 subsection) to ~200 words (3 paragraphs). Kept: directory verification caveat, Commonweave-is-not-a-platform position, brief note on why coordination software is not the project's path. Cut: extended directory description, bullet list of "what Commonweave isn't," entire Tier 3 coordination tool subsection.

**Appendix C:**
- "Version 1.5" reference -> "Version 2" reference.

### 5. Changes I considered and rejected (with reasoning)

**Rejected from DeepSeek's v2 plan:**

- **Restructure the spine.** DeepSeek proposed reordering into 11 numbered parts with a new Part 2 ("lay of the land: power, politics, and perils") and a new Part 5 ("design principles for an inclusive pipeline"). Rejected. The guide's existing flow (problem -> three legs -> pipeline -> law -> math -> how-to -> failure modes -> about) is intuitive and field-tested. Reordering would require renumbering every cross-reference, would push the page count up significantly, and would not materially improve any reader's ability to use the doc. Practitioners who need the RACI chart should not have to wade through a power-analysis section to reach it.

- **Add a standalone "Design principles for an inclusive pipeline" part.** Rejected. The care-work, anti-harassment, accessibility, and gender-power material is already in the right places (Part 2 leg-3, Part 7 sweat-equity disability, Red Flag Checklist). Lifting it into a new section would create a tour-of-our-values section, which is the wrong tone for a field guide and would duplicate content that already lands.

- **Add a "Who benefits from the status quo" section naming institutional landlords, REITs, developer lobbies.** Rejected for v2 ship. The substance is right, but Simon's hard rule was "Don't introduce new factual claims you can't back." Naming specific developer associations and citing specific lawsuits or campaigns requires verifiable case studies. The current "find the land is a political fight" note acknowledges the antagonists exist without naming them. A v3 with verified case studies (California Association of Realtors specifics, identified NIMBY lawsuits) is the right move; tonight is not.

- **Build out Appendix C, the international legal wrappers, into a substantial appendix.** Rejected. This is genuine v3 work. The current stub is honest about being a stub. Producing real jurisdiction-by-jurisdiction guidance for the UK, France, Germany, Belgium, Uruguay, the Philippines, Kenya, India, Australia/NZ/Canada requires expertise I do not have and citations I cannot verify in one pass.

- **Build out Appendix D, political strategy for land acquisition.** Same rationale as above. v3.

- **Add a climate/density/typology section in Part 5.** Rejected for the carbon-numbers reason. The current Part 5 already says "multifamily, modular, and adaptive-reuse typologies often produce significantly lower per-unit cost and lower embodied carbon" and "do not site a permanently-affordable home in a mandatory-evacuation flood zone or high-fire-risk zone without explicit hazard analysis." The climate-vulnerable siting prohibition is in the Red Flag Checklist. Going further with specific kg-CO2-per-m2 figures requires verification. v3.

- **Consolidate Red Flag Checklist + Labor Compliance Matrix + RACI into a separate "Operational checklists" Part 9.** Rejected. They are already living in Part 6, which is the right home. Pulling them into a Part 9 would mean a reader has to bounce between Parts 6 and 9 to get from "how to start" to "what to verify before starting." That is worse for usability.

- **Cut the "Pipeline explainer" and "Source repository" links from the back page.** Rejected. They are short, useful, and not promotional in the back-matter context.

- **Move the Indigenous-land subsection earlier in the guide (into a new Part 2).** Rejected. The current placement in Part 6 (where the reader is making site-selection decisions) is operationally correct. Moving it to a power-analysis Part 2 would turn it from a practical instruction ("here is what to do at site selection") into a conceptual statement, which is weaker.

- **Move the AI-coordination-risks subsection out of Part 7 into a "Power asymmetries" section in Part 2.** Rejected. The subsection's home in the dark-history chapter is correct because it names a failure mode of the model, which is what Part 7 is for.

**Considered on my own and rejected:**

- **Rewriting "Surplus workers do not own land" in Part 1.** "Surplus workers" still has the commodification problem. I changed the thesis line and the opening but left this paragraph because rewriting it would have cascaded into the rest of the section without obvious gain.

- **Naming specific NIMBY case studies in the "find the land is political" note.** Rejected on verification grounds.

- **Adding a brief paragraph on Indigenous-led CLTs (e.g., naming Sogorea Te' Land Trust or similar).** Rejected on verification grounds and to avoid tokenizing a specific organization in a brief mention. A v3 with proper consultation and verified description is the right path.

- **Adding a "decommodification of existing stock vs new construction" subsection beyond the brief scope note.** The scope note in the new opening is enough to acknowledge the critique without the guide pretending to be a tenant-organizing manual it is not.

- **Cutting more from Part 7's union-corruption subsection.** Considered and decided the historical context is load-bearing. Left as-is.

### 6. Open questions

- **Tax treatment of sweat-equity credit, again.** The guide says counsel review is the only safe path. Is that still accurate as of 2026? An IRS Notice or a Tax Court case I don't know about could have moved the ground. Worth a verification pass before final ship.

- **Davis-Bacon volunteer-labor question.** The guide says "get this in writing from DOL Wage and Hour, in writing, project by project." Is there now a published DOL opinion letter or a category-of-projects guidance that would let pilots avoid project-by-project review? I don't know.

- **HUD SHOP allocations.** The guide names SHOP as a primary subsidy source. Is the program still funded at meaningful levels in 2026? Funding levels for SHOP have varied substantially over its history.

- **Habitat affiliate count and country-office count.** v1.5 says "around 355 affiliates" (US) and "around 65 country offices" (international). These are Commonweave's figures. They should be re-verified before final PDF ship.

- **Champlain Housing Trust unit count.** v1.5 says "more than three thousand permanently-affordable homes." Worth checking against CHT's most recent annual report.

- **Verification rate of the Commonweave directory.** "1,700 of 27,000 verified" is the current self-reported figure. Is that current as of the day this PDF ships? If the verification rate has improved since the v1.5 draft, the number should be updated.

### 7. What v3 should tackle

These are the genuine remaining holes that this final-pass scope did not reach. In order of impact:

1. **A real political-strategy appendix.** Two or three case studies of CLT land-acquisition campaigns with verified detail (Dudley Street, St Clements, possibly a third). Power-mapping framework. NIMBY playbook with counter-tactics. Municipal budget-cycle engagement guide. This is the single highest-leverage v3 addition; without it, "find the land" remains the unfunded crucial step.

2. **A real international legal-wrappers appendix.** Per-jurisdiction guidance for at least UK, France, Germany/Austria/Switzerland (Baugenossenschaften), Belgium, and Uruguay (FUCVAM). Each section should answer the four universal questions: what entity holds the land at permanent affordability, what wage rules apply, what tax treatment, what insurance. This is a 10,000-15,000-word lift and probably needs a co-author with international housing-law expertise.

3. **A climate/density/typology section in Part 5.** Adaptive reuse, multifamily, mass-timber, passive-house considerations. Per-unit carbon and cost tradeoffs at order-of-magnitude. Climate-vulnerable siting decision framework with concrete thresholds.

4. **Named-antagonist political analysis.** Specific developer associations, specific institutional landlord lawsuits against affordable housing, specific NIMBY tactics with public-record case citations. Done carefully, this would be the most polarizing addition; done well, it would be the most useful for organizers.

5. **A "what to do if you are starting cold" subsection** in Part 6 that is more honest than the current "If you are neither..." section about the gap between an interested individual and an actually-launchable pilot.

6. **Per-row directory verification badges** on the Commonweave directory itself, so the guide can stop carrying the "1,700 of 27,000" disclaimer and instead point to an actually-curated subset.

7. **Indigenous-led CLT case studies and rematriation framework**, drafted with consultation rather than secondary-source description. This is the right thing to do and was not possible tonight.

8. **A non-construction-trades union-equivalent leg.** The current model assumes Northern industrial unionism. Worker centers, gig-economy organizing, informal-sector organizing (along the lines of SEWA, but actually applicable to the construction context in Global South cities), and political-unionism traditions are all gaps. v3 or v4.

9. **A defaults-and-anti-defaults checklist.** v1.5 has the Red Flag Checklist (do-not-do gates) and the Compliance Matrix (must-answer questions). It does not yet have a "good-defaults" checklist (what good pilots typically include even when they are not legally required). This would be modestly useful and modestly long.

10. **Updated and verified all numerical claims** (Habitat affiliate counts, Champlain unit counts, Mondragon firm counts, FUCVAM home counts, directory verification rates, etc.) against current sources before the v3 PDF ship.

---

*End of report.*
