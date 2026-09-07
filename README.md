# Commonweave: A framework and map for meeting shared needs

> **Skeptics start here:** [CRITIQUE.md](CRITIQUE.md) is a section-by-section honest audit of where this framework is weak, magical, or incomplete. It's linked first on purpose. If you're looking for the case against this project, it's already written, and we'd rather you sharpened it than discovered it.

**Official site:** https://commonweave.earth/

---

## The Idea

Commonweave is an open directory of cooperative, commons, ecological, and community organizations, with working notes on how their efforts might complement one another. Start with a problem and a place; find possible contributors, inspect the evidence, and see which roles are missing.

Start with the [framework knowledge base](https://commonweave.earth/knowledge.html) to explore principles, evidence and open questions. Use the [map](https://commonweave.earth/map.html) to investigate organizations and possible roles in a community project. The [organization directory](https://commonweave.earth/directory.html) and [contribution form](https://commonweave.earth/participate.html) support those two main paths.

See the [September implementation review](docs/REVIEW-2026-09-05.md) for the data audit, new planning flow, named-organization offers, validation and remaining release work.

Automation may change who does work and who benefits, but its timing, distribution, and limits are uncertain. The immediate problem is already practical: people need food, shelter, care, and a say in decisions. Connecting useful existing work should help under several economic futures, not depend on a forecast of labor disappearing.

Ownership, institutions, public policy, and bargaining power all influence who benefits. Cooperative and commons arrangements are possibilities to investigate, with costs and failure modes to measure.

The directory includes cooperatives, community land trusts, mutual aid networks, open-source tools, participatory governance projects, community energy, and connector networks. These are candidate records, not endorsements or confirmed service providers. The [September 2026 audit](docs/DATA-AUDIT-2026-09-05.md) documents inconsistent public exports, unreliable locations, and evidence gaps. Suggested connections are hypotheses; a shared location or use case does not establish a partnership.

It's not a manifesto. It's more like an engineering problem with a lot of political and historical constraints. The goal is to figure out what needs to be true for people to have food, shelter, healthcare, and a say in their own lives -- and then figure out how to make those things true.

### Selective Abundance, Not Post-Scarcity

This framework uses *selective abundance* as a scenario to test, not a forecast that essentials will become cheap everywhere. A resource can be plentiful in one setting and inaccessible in another. Production, distribution, affordability, ecological limits, maintenance, and human work must be checked separately. A local proposal should state which constraint it addresses and what evidence would show an improvement.

Different resource categories may require different governance mechanisms. The table below is a set of hypotheses. An organization fitting a category does not demonstrate that its governance works; independent evidence of outcomes, costs, inclusion, and durability is needed.

| Resource or coordination problem | Examples | Constraints to check | Governance hypothesis | Failure mode to test | Directory research leads |
|---|---|---|---|---|---|
| Material provision (energy, basic food) | Solar power, community gardens | Production cost, distribution, affordability, storage, land and labor | Cooperative provision; shared infrastructure; access rules | Unfunded maintenance, exclusion, or capture of distribution | Centre for Renewable Energy and Action on Climate Change [NG] |
| Digital resources (information, software) | Learning platforms, shared reference works | Access, hosting, maintenance, accessibility, contributor time | Open licensing; accountable stewardship; funded maintenance | Platform capture, neglected upkeep, unequal access | [Moodle](https://moodle.com/about/open-source/); [Wikimedia Foundation](https://wikimediafoundation.org/who-we-are/) — software and knowledge infrastructure, not evidence of universal access |
| Persistently scarce (land, fresh water, rare minerals) | Urban land, aquifers, lithium | Physical limits; rival consumption | Democratic allocation; stewardship/usufruct models; Ostrom-style commons with monitoring and graduated sanctions | Enclosure; privatization of the governance body itself | ADDISON COURT HOUSING COOPERATIVE INC [US]; LANDWELL HOUSING COOPERATIVE [US] |
| Skilled care (healthcare, childcare, eldercare) | Community health workers, midwives, teachers | Human labor hours; training pipeline | Recognized as essential work; compensation premiums; community health worker networks | Burnout and wage suppression when treated as volunteer surplus | [NEEDS EXAMPLE] |
| Ecological systems (atmosphere, oceans, biodiversity) | Carbon cycle, ocean fisheries, pollinator networks | Extraction limits, interdependence, delayed feedback; some uses are rival | Monitoring and use limits with democratic accountability; explicit review and appeal rules | Excess extraction, weak enforcement, or regulatory capture | Environmental Monitoring Group (EMG) [ZA] |
| Attention and meaning | Culture, community, creative work | Cannot be manufactured or stockpiled | Cultural and institutional responses; time sovereignty | Commodification; algorithmic capture of attention for extraction | [NEEDS EXAMPLE] |
| Cooperative economics (worker ownership, mutual aid) | Worker co-ops, mutual aid networks, credit unions | Capital access; competition from non-cooperative firms | Solidarity economy networks; preferential sourcing between co-ops; policy support (Marcora Law model) | Scale pressure causes drift back to conventional employment (Mondragon precedent) | Mutual Aid Twin Cities Housing Cooperative [US]; PRAGYA [GB] |

The final column contains research leads, not validated exemplars. The two linked digital-resource examples have [dated official-source checks](docs/featured-organizations-review-2026-09-05.md); their presence does not establish the proposed governance outcomes. The other names and missing examples need source review. `alignment_score` is a classification aid, not a measure of organizational effectiveness. Coverage gaps do not by themselves disprove a governance hypothesis. The [operating model](FRAMEWORK-OPERATING-MODEL.md) specifies narrower tests with baselines and decisions on failure.

The framework is designed to work under conditions of *partial* abundance and *persistent* scarcity -- not to wait for a threshold that may never fully arrive.

---

## What Exists Today

This section matches ambition to evidence. The public files were structurally audited on 2026-09-05; their source snapshots are older.

### The Directory

The shipped release, search, and map files disagree. Counts below describe records in those files, not independently verified distinct organizations or current operational coverage:

| Public surface audited | Observed records | Meaning |
|---|---:|---|
| April 27 release | 158,715 distinct record IDs | Candidate rows; entity deduplication and activity still need review. |
| Country search files | 144,731 rows | Actual files differ from the search index's claimed total. |
| Map points file | 29,423 points | Many coordinates are approximate or shared centroids; a pin does not establish service reach. |

See the [audit and limits](docs/DATA-AUDIT-2026-09-05.md) and [machine-readable report](reports/data-audit-2026-09-05/summary.json). Do not combine old database counts with public-map counters or describe a structural audit as verification of every organization.

Honest breakdown of what these records mean:

- **Candidate, not gospel.** A row means "worth review," not "endorsed by Commonweave."
- **Legibility matters.** The working database tracks whether an organization is formal, hybrid, informal, or unknown so registry-backed groups do not crowd out rural, off-grid, Indigenous, mutual-aid, and social-first networks.
- **Coverage repair needs evidence.** Discovery and enrichment tooling can stage candidates, but a script or historical log does not establish that a live process is running. New sources need permission, provenance, review, and export validation.
- **Solution composition is experimental.** Organizations, tools, policies, and funding mechanisms can suggest complementary roles. Current capacity, service area, willingness, and practical compatibility require separate checks.
- **Sensitive groups need protection.** Public-presence-only by default; human review before mapping/promoting sensitive rural, Indigenous, land-defense, migrant, or mutual-aid groups.

Older documents and generated files contain historical totals. Prefer the dated audit of the actual surface being used; the local working database is not included in this checkout.

### The Framework

This README is the framework document. Its current maturity:

- **Draft.** The core thesis, three-phase structure, and Mycelial Strategy are written and internally consistent. Core tensions are documented. Open questions are flagged as open.
- **Critique-first.** [CRITIQUE.md](CRITIQUE.md) is a section-by-section honest audit of where the framework is weak or incomplete. It exists because the failure modes should be on the table before anyone commits to this.
- **Open to correction.** Some historical claims remain insufficiently sourced; the critique is an active work list. Pull requests are the revision mechanism.
- **Operational proposal.** [FRAMEWORK-OPERATING-MODEL.md](FRAMEWORK-OPERATING-MODEL.md) defines a ten-practitioner comparison, accountable roles, time budget, and continue/revise/stop rules. No outcomes are claimed before that pilot runs.

### Related project: NeighborhoodOS

[NeighborhoodOS](https://neighborhoodos.org) is a sibling project — an open-source operating system for neighborhoods that want to solve their own problems, starting with one sharp "wedge" at a time. It was originally developed inside Commonweave as a ground-level implementation layer; in April 2026 it was split out into its own project so each can move at its own pace.

The two projects stay loosely connected: NeighborhoodOS can optionally consume the Commonweave directory to answer "who's already working on this near me?" when a wedge calls for it. But each project has its own repo, roadmap, and governance.

Current NeighborhoodOS wedge: home maintenance in West Waldo, Kansas City (owner-occupied only).

- Site: [neighborhoodos.org](https://neighborhoodos.org)
- Code: [GitHub](https://github.com/simonlpaige/neighborhoodos) / [Codeberg](https://codeberg.org/AlphaWorm/neighborhoodos)

---

## What Does Not Exist Yet

To be specific:

- **No running pilots under the Commonweave banner.** Organizations in the directory operate independently. None are affiliated with or funded by this project.
- **No confirmed collaboration agreements in the evidence reviewed here.** Prior outreach attempts exist; replies, consent, and formal affiliation are separate matters. The [participation plan](OUTREACH-ATTRACTION-PLAN.md) starts with useful contributions to named organizations.
- **No named legal entity.** There is no Commonweave Foundation, LLC, or unincorporated association. This is a repository and a framework document.
- **No staff.** This is an open-source project.

---

## Core Principles

These are the load-bearing walls. Everything else is details.

1. **Universal Sufficiency** -- Every person has an unconditional right to food, shelter, healthcare, education, and meaningful participation in society.
2. **Ecological Equilibrium** -- No economic activity may degrade the systems that sustain life. The economy operates within planetary boundaries.
3. **Democratic Sovereignty** -- Power flows from people, not capital. Decisions are made by those affected by them.
4. **Common Ownership of the Commons** -- Land, water, air, energy, data, and infrastructure belong to everyone. They cannot be privately hoarded.
5. **Voluntary Contribution** -- Work is not coerced. People contribute because they find meaning, not because survival depends on it.
6. **Non-Violence** -- The transition happens through preparation, legitimacy, and collective action -- not force.
7. **Transparency by Default** -- Systems of governance and resource allocation operate in the open. "By default" does work here, and the exceptions matter: individual medical records, whistleblower and dissident protection, survivors of domestic violence, children's data, and contributors operating under authoritarian regimes. Transparency applies to *power and resources*, not to *people made vulnerable by visibility*. The failure mode of "radical transparency" is surveillance dressed as accountability; the framework rejects that trade. See the Mycelial Strategy's failure-mode subsection for operational detail.

These principles are in tension with each other. That's not a bug. See [Tensions and Tradeoffs](#tensions-and-tradeoffs) below.

---

## The Framework in 90 Seconds

Three phases, one connective tissue. The phases are parallel tracks that co-evolve, not a linear sequence -- Phase 1 prerequisites depend on Phase 3 outcomes and vice versa.

**Phase 1 -- Pre-transfer:** Build the alternatives before anything collapses. Democratic infrastructure, food/healthcare/housing/energy systems designed for sufficiency rather than profit, cooperative economics. These need to be working at small scale before any transfer is realistic -- think of it as load testing before launch. Full specification: [BLUEPRINT.md](BLUEPRINT.md).

**Phase 2 -- The transfer:** Not a revolution, a migration with resistance. The prepared alternatives scale up, institutions transform from within and under pressure, the old economy loses its revenue base. Full analysis of mechanisms and historical cases: [THEORY-OF-CHANGE.md](THEORY-OF-CHANGE.md).

**Phase 3 -- Maintenance:** The hard part isn't building the good world, it's keeping it from sliding back. Anti-backsliding mechanisms, beyond-GDP measurement, nested governance, ecological restoration. Phase 3 is the immune system. [THEORY-OF-CHANGE.md](THEORY-OF-CHANGE.md).

### The Mycelial Strategy

The proposed connective tissue is people and organizations sharing useful knowledge, running pilots, and helping each other fill gaps. Existing alternatives may improve people's options; their existence does not demonstrate readiness to replace wider institutions. Commonweave's immediate test is whether discovery and evidence-backed suggestions help a defined local task.

In 2007, Paul Hawken published *Blessed Unrest* arguing the world's largest social movement already existed -- millions of organizations with no name and no central organization. He and colleagues catalogued 114,994 of them on WiserEarth. Then the funding ran out and the whole thing disappeared in a weekend. That was 2014.

The lesson isn't that the idea was wrong. It's about infrastructure -- both technical (don't depend on a single server) and social (don't depend on everyone running their own). The realistic model is decentralized in *governance* but may be centralized in *operations* -- like the Wikimedia Foundation or the Apache Foundation. Not ideologically pure, but actually works.

Transparency can support accountability but cannot by itself prevent capture or protect contributors. Openness has known failure modes that must be actively managed:

- **Flooding and noise:** Bad actors can overwhelm discussion to dilute signal. *Countermeasure: moderation policies, contribution quality standards, rough consensus decision-making with clear timelines.*
- **Concern trolling:** Using the open process to slow-walk decisions to death. *Countermeasure: decision deadlines, "rough consensus and running code" -- working implementations outweigh theoretical objections.*
- **Strategic co-option:** Aligning publicly with the movement while redirecting its resources toward industry-friendly goals (see: corporate greenwashing). *Countermeasure: clear alignment criteria, willingness to refuse partnerships that don't meet them, outcome-based evaluation.*
- **Harassment of contributors:** Visible participation makes contributors targets. *Countermeasure: contributor pseudonymity is supported as protection, not ideology. People may contribute under any identity.*
- **State surveillance:** Publishing locations and relationships can expose people to harm. Commonweave cannot accept that tradeoff on their behalf. Prefer public organizational information, coarse location or omission where needed, and prompt correction/removal. Confidential contributor protection is compatible with accountable governance.

Network governance, accountability structures, named leadership: [GOVERNANCE.md](GOVERNANCE.md).

### Theory of Power Transfer

The framework requires an honest answer to the hardest question: *why would those with power give it up?*

Most won't. Not voluntarily. Power does not become "irrelevant" because better alternatives exist. The history of fossil fuels, tobacco, feudal land tenure, and colonial governance shows that entrenched power fights to preserve itself long after superior alternatives are available.

The framework relies on five mechanisms, in order of realism:

1. **Economic obsolescence.** Some power structures erode when technology changes -- newspaper classified ad revenue, taxi medallions, music label distribution monopolies. The framework identifies which current power structures are vulnerable to technological displacement and builds alternatives there first.
2. **Democratic capture in reverse.** Electing people committed to commons-based policy into existing structures. Already happening: participatory budgeting in 7,000+ cities, community wealth building in Preston and Cleveland, state-level cooperative development legislation. Slow, boring, effective.
3. **Coalition pressure.** Labor movements, consumer boycotts, shareholder activism, divestment campaigns. The anti-apartheid movement, marriage equality, the tobacco settlement -- none waited for the powerful to see the light.
4. **Parallel institution-building.** Email didn't ask the postal service for permission. Wikipedia didn't negotiate with Encyclopaedia Britannica. When commons-based alternatives are demonstrably better, migration happens.
5. **Nonviolent non-cooperation.** When power refuses to yield: strikes, tax resistance, civil disobedience. The framework is nonviolent. It is not passive.

**What the framework does NOT assume:** That power holders will voluntarily step aside. That the transition will be smooth or painless. Some power will have to be taken, even if the taking is nonviolent. Full engagement with historical cases: [THEORY-OF-CHANGE.md](THEORY-OF-CHANGE.md).

---

## Tensions and Tradeoffs

The core principles are in tension with each other. These are not bugs -- they are the hardest design problems. They do not have clean answers.

**Democratic Sovereignty vs. Ecological Equilibrium:** What happens when a democratic majority votes to allow resource extraction that violates planetary boundaries? The framework's position: ecological limits function like constitutional rights -- not subject to majority override. A majority vote cannot strip future generations of a livable planet. Planetary boundaries are pre-political. **Open problem:** Who defines them, and who enforces them when democratic institutions disagree? No such body currently exists at adequate scale. (See Issue #35)

**Voluntary Contribution vs. Universal Sufficiency:** If contribution is truly voluntary, who does the unglamorous work? Sewage treatment, garbage collection, elder care at 3 AM. Every commune and cooperative in history has confronted this. The framework's position: voluntary contribution means work is not performed under threat of starvation. Mechanisms in order of preference: automation first, then rotation, then compensation premiums, then genuine voluntarism. **Open problem:** Free-rider dynamics are documented in every commons. Ostrom's design principles are the best available framework but require enforcement mechanisms not yet fully specified here. (See Issue #35)

**Common Ownership vs. Cultural Adaptation:** Local communities may govern *how* resources are distributed. They may not govern *whether* a person is entitled to food, shelter, healthcare, or safety. **Open problem:** Who decides when a community has crossed from adaptation into exclusion? This is the federalism problem in its oldest form. (See Issue #35)

The framework does not assume humans are angels. It assumes systems designed for the full range of human behavior -- free-riding, status competition, in-group formation, apathy -- will produce better outcomes than systems that punish people for surviving under coercive conditions. See [RESEARCH.md](RESEARCH.md).

---

## Open Questions

These are genuinely unresolved. Good questions are only useful if they become work packages. The "Blocker" column says what specifically is needed -- often that's the real constraint, not the expertise.

| Question | Status | Needed expertise | Issue | Blocker |
|---|---|---|---|---|
| How do you transition a globalized economy without leaving developing nations worse off? | Open | Development economics, global trade policy | | Needs practitioner from a developing-nation context to co-author |
| What role do existing nation-states play? Do they dissolve, federate, or transform? | Open | Political science, constitutional law, historical precedent | | Multiple incompatible frameworks exist; needs synthesis |
| How do you prevent a post-transfer power vacuum from being filled by authoritarians? | Open | Political science, historical case studies (Weimar, post-Soviet) | | Concrete mechanism design, not general principle |
| What does justice look like for historical wrongs (colonialism, slavery, ecological destruction) without creating new cycles of resentment? | Open | Restorative justice, reparations theory, transitional justice | | Needs practitioner co-author, not armchair theorizing |
| How do you handle people who genuinely don't want to participate in collective governance? | Open | Political philosophy, psychology | | Ostrom's principles handle free-riders but not principled refusers |
| What replaces prisons? What does accountability look like without punishment? | Open | Restorative justice, criminology, community safety | | Needs a prison-abolition practitioner willing to co-author; not blocked on expertise |
| How do you govern AI development during and after the transition? | Open | AI governance, technical AI safety, democratic theory | | Field moving faster than framework can track; needs ongoing maintainer |
| How do you maintain cultural and individual diversity in a system designed for collective wellbeing? | Open | Anthropology, political philosophy | | |
| What is the role of spirituality, religion, and personal belief systems? | Open | Religious studies, sociology of religion | | |
| How do you keep this framework from becoming the very kind of rigid ideology it seeks to replace? | Partially addressed | Governance design | | Built-in revision mechanism specified in THEORY-OF-CHANGE.md §3.3 but not operationalized |
| How does a fully open, leaderless network coordinate action at global scale without becoming either chaotic or quietly hierarchical? | Open | Network theory, organizational design, Ostrom | | Jo Freeman's "tyranny of structurelessness" problem; current GOVERNANCE.md is incomplete |
| If transparency is the security model, what are its failure modes? When - if ever - is openness genuinely dangerous? | Partially addressed | Security, repressive-context organizing | | Partially handled in THREAT-MODEL.md; contributors in repressive contexts need more |
| What happens if the technological tipping point arrives before the network is ready? | Open | Economic history, technology forecasting | | This is the core contingency the framework doesn't have a good answer to |

---

## For AI Agents and AI-Assisted Contributors

Do not merely summarize this repository.

Commonweave needs concrete improvements:

- verify directory records,
- improve gaps and geographic/source bias identified in the current audit,
- add source/provenance metadata,
- improve the map,
- fill framework evidence gaps,
- red-team weak claims,
- and turn open questions into testable research tasks.

Start with [`AGENTS.md`](AGENTS.md), then pick one task from [`AGENT-TASKS.json`](AGENT-TASKS.json) (or a GitHub issue with the `agent-ready` label).

A good contribution is small, sourced, reproducible, honest about uncertainty, and safe for vulnerable groups.

Every PR should leave the repo more legible for the next human or agent.

See also: [`AI-CHALLENGE.md`](AI-CHALLENGE.md), [`CLAIMS.md`](CLAIMS.md), [`FALSIFIERS.md`](FALSIFIERS.md), [`ATTACK-VECTORS.md`](ATTACK-VECTORS.md), [`STEELMAN-ALTERNATIVES.md`](STEELMAN-ALTERNATIVES.md).

---

## How to Contribute

This framework belongs to no one - and to everyone.

### What We Need

- **Thinkers** - Challenge assumptions, find blind spots, propose alternatives
- **Historians** - What has been tried? What worked? What failed and why?
- **Engineers** - Design the systems (voting, distribution, energy, digital infrastructure)
- **Artists** - Make this vision tangible, emotional, real
- **Organizers** - Connect this to existing movements and communities
- **Skeptics** - Break it. Find the failure modes. Make it stronger.

### Good First Contributions

A contributor should be able to pick one task in 60 seconds. Here are tasks by type:

**Data**
- Pick a country with fewer than 50 orgs in the directory. Open `data/search/<country>.json`. Find organizations that are missing, misclassified, or have broken websites. File a PR with corrections and a one-line note at the top explaining what you checked.
- **Directory verification (45 minutes).** Pick one country with <50 orgs. Open `data/search/<country>.json`. Spot-check 10 orgs: website works, description matches framework area. File a PR editing the JSON with your corrections + a note at the top. Country-scoped tasks work because a contributor in Nairobi or Mexico City immediately has local knowledge we don't have.

**Research**
- Pick one Open Question from the table below and find at least one peer-reviewed source or documented real-world experiment that speaks to it. File a PR adding the source and a 2-sentence summary to RESEARCH.md.
- Find a working cooperative, land trust, or mutual aid network in your country or city not yet in the directory. Document it in a PR following the format in `data/CONTRIBUTING-DATA.md`.

**Code**
- Test whether people can distinguish location precision, source-backed records, and unverified service claims in the map filters.
- Check a sample of map connections against their claimed evidence, explanation, and source date; repair unsupported relationships.
- Run a phone-sized discovery task with a practitioner and fix the largest observed obstacle.

**Design / Writing**
- The governance matrix in the Selective Abundance section has several `[NEEDS EXAMPLE]` cells. Find a real organization from the directory that fits and fill one in with a PR.
- Draft a 3-sentence plain-language explanation of one framework mechanism (community land trust, participatory budgeting, mutual aid) for someone who has never heard of it. Submit to GLOSSARY.md (create it if it doesn't exist).

### How to Contribute

1. Fork this repository
2. Create a branch for your contribution
3. Submit a pull request with a clear description of what you're adding or changing
4. Engage in discussion on Issues - this is where the real work happens

### Guiding Rules for Contribution

- No single person owns this. No cult of personality. Leadership is transparent and accountable (see [GOVERNANCE.md](GOVERNANCE.md)).
- Ideas are evaluated on merit, not on who proposed them.
- Disagree constructively. We are building, not debating.
- Publish governance decisions, evidence, and resource use. Keep private contact details and sensitive contributor or beneficiary information out of public records.
- Specificity is valued. "We should fix healthcare" is a starting point. "Here is a model for community health worker networks based on Cuba's system" is a contribution.
- Cite your sources. Build on what already exists.

---

## Influences and Prior Art

> *We are not starting from zero. Many have thought deeply about these problems.*

### Thinkers and Theorists
- **Paul Hawken** - *Blessed Unrest* (2007): the largest movement in the world already exists, leaderless, without ideology, and no one has seen it. WiserEarth was the mirror he built so it could.
- **Murray Bookchin** - Social ecology, libertarian municipalism
- **Elinor Ostrom** - Governing the commons without privatization or state control
- **André Gorz** - Post-work society, reclaiming time from capital
- **Kate Raworth** - Doughnut Economics: thriving within planetary boundaries
- **Paulo Freire** - Education as liberation, critical pedagogy
- **Ursula K. Le Guin** - *The Dispossessed*: a fictional blueprint for an anarchist society
- **Danielle Sered** - *Until We Reckon*: restorative justice for violent harm

### Living Models
- **Mondragon Cooperative** - 80,000+ worker-owners, €12B+ revenue (Basque Country)
- **Kerala Model** - High human development on low GDP (India)
- **Zapatista Autonomous Municipalities** - Indigenous self-governance (Mexico)
- **Bhutan's Gross National Happiness** - Alternative metrics for societal success
- **Preston Model** - Community wealth building through anchor institutions (UK)
- **Community Land Trusts** - 300+ in the US, 250+ in England/Wales, growing globally
- **Rural Electric Cooperatives** - 900+ member-owned utilities serving 42M Americans
- **Common Justice** - Restorative justice for violent felonies (New York City)
- **Barcelona Superblocks** - Reclaiming streets for people, play, and community

### Historical Precedents
- **WiserEarth / Wiser.org** (2007-2014) - The first large-scale civil society coordination network. 114,994 NGOs in 243 countries, 79,651 members, 3,273 groups, 381 sub-issue taxonomy. Leaderless, open-source, ad-free, women-led. Direct precedent for the Mycelial Strategy. Closed 2014 due to centralized funding failure -- the key cautionary lesson. See [WISEREARTH.md](WISEREARTH.md) for full analysis. (Paul Hawken / Natural Capital Institute)

### Referenced Open-Source Projects
- **Decidim** - Participatory democracy framework (github.com/decidim)
- **Open Food Network** - Software and locally led networks for community food enterprises ([official overview](https://openfoodnetwork.org/about-us/)).
- **Community Health Toolkit** - Open technologies and implementer resources for community health ([project](https://communityhealthtoolkit.org/)).
- **OpenMRS** - Electronic medical record platform and implementer community ([about](https://openmrs.org/about/)).
- **ElectionGuard** - End-to-end verifiable elections (github.com/Election-Tech-Initiative)
- **Open Source Ecology** - 50 open-source industrial machines (github.com/OpenSourceEcology)
- **Liquid Democracy e.V.** - Participatory governance tools (github.com/liqd)
- **OpenDemocracy AI** - AI-powered participatory democracy (github.com/AshmanRoonz/OpenDemocracy)
- **HumanityOS** - Free, public-domain (CC0) cooperative platform + game engine for ending poverty through capability. Self-custody identity, federated, local-first, peer marketplace, offline-first. The Humanity Accord is a model constitution with strong alignment to Commonweave's principles. (united-humanity.us, github.com/Shaostoul/Humanity)
- **Kolibri** - Offline-first education platform (learningequality.org)
- **Belenios** - Verifiable online voting system (belenios.org)

### Policy Frameworks
- **The Commons Transition Plan** - P2P Foundation (commonstransition.org)
- **Doughnut Economics Action Lab** - Economics within planetary boundaries (doughnuteconomics.org)
- **Wellbeing Economy Alliance** - Governments moving beyond GDP (weall.org)
- **Guaranteed Income Pilots Dashboard** - 100+ UBI pilots tracked (guaranteedincome.us)

> For a comprehensive deep dive into existing work in each framework area, see **[RESEARCH.md](RESEARCH.md)**. Evidence quality varies: some cited projects are proven at scale (Mondragon, CLTs), some are promising experiments (UBI pilots), and some are theoretical. RESEARCH.md should be read with that gradient in mind.
> For the collaboration outreach plan, see **[OUTREACH.md](OUTREACH.md)**.
> For explicit governance, decision-making, and accountability structures, see **[GOVERNANCE.md](GOVERNANCE.md)**.
> For the honest section-by-section critique of this framework, see **[CRITIQUE.md](CRITIQUE.md)**.

---

## License

This work is released under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to share, adapt, and build upon this work - even commercially - as long as you give credit and share your contributions under the same license.

---

*"Another world is not only possible, she is on her way. On a quiet day, I can hear her breathing."*
- Arundhati Roy

---

## Project Status

🌱 **Seedling** - This framework is in its earliest stage. Everything is open for discussion, revision, and expansion.
