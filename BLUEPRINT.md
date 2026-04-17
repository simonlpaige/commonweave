# Ecolibrium: Blueprint

> This is the specification document. It covers Phase 1 infrastructure requirements in detail: what systems need to exist before any power transfer is viable, what we know about each, and where the honest scale and cost problems lie. If you want the "why this exists" version, see [VISION.md](VISION.md). If you want the theory of how transition actually happens, see [THEORY-OF-CHANGE.md](THEORY-OF-CHANGE.md).

---

## A Note on Sequencing

The framework below is organized as Phase 1 / 2 / 3 for readability, but this is misleading if read as a strict timeline. Many Phase 1 prerequisites (land transition, cooperative economics) depend on Phase 3 outcomes (values transformation). The phases are better understood as parallel tracks with dependencies that co-evolve, not a linear sequence.

The Mycelial Strategy described in [VISION.md](VISION.md) is not a phase -- it is the connective tissue that operates across all phases at all times.

**The core claim of Phase 1:** The transfer of power to a better system can only happen if a better system is ready to receive it. History is full of examples of what happens when the old system collapses before the new one is operational. It is not pretty. So these systems need to exist and be demonstrably working, even if only at small scale, before any transfer scenario is realistic. Think of it as load testing before launch.

---

## Phase 1: Pre-Transfer -- Systems That Must Exist

### 1.1 Democratic Infrastructure

The first category is not glamorous but is foundational. Every other system requires legitimate governance to function.

#### Voting Systems

- [ ] **Verifiable, tamper-resistant voting** at local, regional, and international scale
  - Electronic systems must be auditable -- not just "electronic," but independently verifiable with paper trails or cryptographic proofs
  - End-to-end verifiable election systems exist and are production-ready: *Belenios* (belenios.org) provides cryptographic vote verification without requiring voters to trust the counting infrastructure. *ElectionGuard* (GitHub: Election-Tech-Initiative) provides verifiable ballot marking and counting for existing election software.
  - The specific threat model: insider fraud, external manipulation, and loss of verifiability. All three are different attack vectors requiring different mitigations.
- [ ] **Liquid democracy options**
  - Direct vote or delegation to trusted representatives per issue
  - Existing deployments: *Liquid Democracy e.V.* (Berlin), *Decidim* (Barcelona and 7,000+ cities), *vTaiwan* (Taiwan's Pol.is-based policy co-creation platform, used for Uber regulation and alcohol sales law reform)
  - *Open problem: Cascading delegation creates influence concentration. If ten people all delegate to one trusted expert, that expert accumulates decision weight. Needs bounded delegation or mandatory re-authorization. Research ongoing.*
- [ ] **Constitutional protections against majority tyranny**
  - Specifically: protection of minorities from democratic override on rights, ecological boundaries from democratic override on sustainability, and future generations from override on long-term consequences
  - *Legal precedent: German Constitutional Court (Bundesverfassungsgericht) ruled in 2021 that the German Climate Protection Act violated future generations' rights (BVerfGE, April 2021). First major constitutional court ruling that current democratic decisions must account for future persons.*
- [ ] **Mandatory inclusion for marginalized voices**
  - Sortition (random selection) as a complement to election: randomly selected citizens' assemblies produce more representative outcomes than elected bodies for complex policy questions
  - *Empirical evidence: Ireland's Citizens' Assembly (2016-2018) resolved abortion and marriage equality through sortition + deliberation. French Citizens' Convention on Climate (2020) produced more ambitious proposals than the elected parliament. Reviewed in: Gastil & Knobloch, "Hope for Democracy" (2020).*
- [ ] **Recall and accountability mechanisms** built into every elected role from the start, not retrofitted

#### Structural Limits on Power Concentration

- [ ] Term limits, rotation, and sortition for governance roles
- [ ] Separation of celebrity and governance
  - The specific problem: high-profile, fame-based roles create incentive structures toward performance over substance. Charismatic authority in governance has a consistent failure mode across cultures and political systems.
  - *Warning: This clause has obvious free-speech and definitional risks. What counts as a "public figure"? How long is the cooling-off period? These belong in a constitutional-design working group, not a principles document. The framework identifies the failure mode; it does not specify the remedy.*
- [ ] Decision-making by council and rough consensus, not charismatic authority
  - "Rough consensus and running code" as a governance principle (originally from IETF internet standards development -- a useful model for non-hierarchical technical and governance decisions)

#### Conflict Resolution

- [ ] Restorative justice replacing punitive justice where applicable
  - *Evidence base: Danielle Sered's "Until We Reckon" (2019) documents restorative justice for violent felonies at Common Justice (New York). Victim satisfaction rates significantly higher than traditional prosecution. Meta-analysis of restorative justice programs: Sherman & Strang, "Restorative Justice: The Evidence" (2007).*
  - *Honest limit: Restorative justice works where victims want it and offenders accept accountability. For cases where neither condition holds, the alternative framework is unspecified.*
- [ ] Community mediation infrastructure
- [ ] International arbitration frameworks (existing: ICC, ICSID, UNCITRAL -- but these are corporate-focused and need redesign for commons governance)

---

### 1.2 Resource Distribution Systems

#### Food

- [ ] **Local and regional food sovereignty**
  - Communities controlling their own food supply as a hedge against supply chain fragility and as a democratic principle
  - *Existing models: Brazil's Programa Nacional de Alimentação Escolar (PNAE) -- mandatory purchase of 30% of school food from local family farmers since 2009. 47 million students, 200,000+ family farms. "The school feeding program in Brazil" (FAO, 2015).*
  - Vertical farming: current economics make it competitive for leafy greens in urban contexts; not yet competitive for calorie-dense crops (grains, legumes). Technology trajectory suggests cost parity possible in 10-20 years for controlled-environment crops.
  - Permaculture and regenerative agriculture: *Savory Institute holistic planned grazing, Rodale Institute certified organic no-till (50+ years of comparative data -- "Farming Systems Trial" is the longest-running comparison in North America).* Higher labor input per acre, often lower input costs, soil carbon sequestration as a measurable co-benefit.
  - System of Rice Intensification (SRI): produces higher yields with 25-50% less water in 60+ countries. *Documented in Uphoff, "The System of Rice Intensification" (2011); adoption data from Cornell SRI International Network.*
- [ ] **Universal free access to nutritious food**
  - This is not technically difficult in wealthy nations. US annual food waste is approximately 80 million tons (USDA estimate). The constraint is political, not logistical.
  - Community kitchen models (UK food banks, India's Akshaya Patra -- 1.8 million meals/day -- show feasibility at scale)
- [ ] **Elimination of food waste through logistics and redistribution**
  - *Scale: 30-40% of US food supply wasted (USDA/EPA). Approximately $161 billion annually. The logistics problem is solvable; the property rights problem (who owns "waste") is the barrier.*

#### Healthcare

- [ ] **Universal, free-at-point-of-use healthcare**
  - *Proof of concept: Multiple countries have this. UK NHS (est. 1948), Canada's Medicare (est. 1966), Taiwan's National Health Insurance (est. 1995 -- covers 99.9% of population at cost roughly half of US per-capita spending). None of these are perfect. All demonstrate that universal access is achievable.*
  - Cost argument: The US spends approximately 17-18% of GDP on healthcare (CMS data, 2023) vs. 10-12% in comparable universal-coverage countries, with worse outcomes on most population health metrics. The argument that universal care is unaffordable is not supported by international comparison.
- [ ] **Preventive care prioritized over reactive treatment**
  - Economic case is straightforward: prevention is cheaper. The incentive misalignment is that fee-for-service payment structures reward treatment, not health.
- [ ] **Mental health fully integrated**
  - Currently treated as specialty care in most systems. Evidence for integrated primary care models: *Archer et al., "Collaborative care for depression and anxiety problems" (Cochrane Review, 2012).* Integration reduces costs and improves outcomes.
- [ ] **Open-source medical research**
  - No patents on life-saving treatments -- or at minimum, mandatory licensing at cost-of-production for essential medicines
  - *Existing model: Medicines Patent Pool (MPP), UN-backed -- negotiates voluntary licenses for HIV, hepatitis, tuberculosis medicines. Covers 116 low/middle-income countries. Partial model; needs expansion to all essential medicines.*
  - Open-source drug discovery: *Open Source Malaria* consortium, *COVID Moonshot* project -- demonstrated that open publication of drug candidates accelerates development
- [ ] **Care work recognized and resourced as essential**
  - Childcare, eldercare, disability support: currently handled by unpaid (predominantly women's) labor or low-wage workers
  - *Economic analysis: Folbre, "Valuing Children" (2008); Mazzucato, "The Value of Everything" (2018) -- care work is not "unproductive" by any serious economic accounting; it is systematically undervalued because it doesn't flow through markets.*

#### Education

- [ ] **Lifelong, free, universally accessible education**
  - "Free at point of access" already exists in public education systems worldwide; the constraint is quality and genuine access (transportation, childcare, economic pressure to work instead)
  - *Kolibri* (learningequality.org): offline-first education platform, works without internet, deployed in refugee camps and rural communities in 40+ countries
- [ ] **Not job training -- genuine cultivation of critical thinking, creativity, civic participation**
  - *The framework's position:* Education systems optimized for labor market output produce workers who are useful but not free. The historical argument for public education as civic formation (John Dewey, "Democracy and Education," 1916) is older than the human capital argument and more coherent.
- [ ] **Open-source curricula collaboratively developed**
  - *Existing precedent: Khan Academy, Wikipedia, OpenStax -- proof that collaboratively developed open educational content reaches large-scale use without per-unit cost.*
- [ ] **Emphasis on ecological literacy, systems thinking, and emotional intelligence**
  - Not aspirational -- these are teachable skills with measurable outcomes. *Collaborative for Academic, Social, and Emotional Learning (CASEL) meta-analysis: SEL programs improve academic performance by 11 percentile points on average (Durlak et al., 2011).*

#### Housing

- [ ] **Shelter as a right, not a commodity**
  - *Proof of concept: Finland's Housing First program (implemented 2008) has reduced homelessness by 75% (ARA, 2023). Cost analysis shows it saves money compared to emergency shelter and hospitalization. Utah's Housing First implementation (2005-2015) similarly reduced chronic homelessness. Both work by giving people stable housing first, then addressing other challenges.*
- [ ] **Community Land Trusts as primary mechanism for affordable housing**
  - *Current scale: approximately 300 CLTs in the US, 250+ in England and Wales. Burlington Community Land Trust (Vermont) -- the oldest US CLT -- has maintained affordable housing for 40 years without displacement. Champlain Housing Trust manages 2,500+ homes.*
  - *Honest limit: CLTs work well as an affordable housing tool. Scaling from "affordable housing tool" to "all land is commons" is a civilizational transformation. These are categorically different claims. The framework should not present CLT scaling as a straightforward extrapolation.*
- [ ] **Transition from private land ownership to stewardship models**
  - *Scale problem: US residential real estate alone is worth approximately 45 trillion dollars (Federal Reserve Z.1 data, 2024). Any transition that involves compensating current owners at market value requires a funding mechanism that does not exist. Any transition that does not compensate them is a large-scale redistribution that requires political legitimacy that does not currently exist. Honest path: start with public, abandoned, and tax-delinquent land; scale CLTs; build proof over decades before attempting anything more sweeping.*
- [ ] **Indigenous land return as foundational justice**
  - Not equivalent to "land reform" in the standard sense -- this is restitution for documented theft under documented treaty violations
  - *Legal framework: UNDRIP (UN Declaration on the Rights of Indigenous Peoples, 2007) establishes the international rights basis. Specific restitution mechanisms require case-by-case legal and negotiated processes.*

---

### 1.3 Economic Transition Mechanisms

> Every proposal here requires evaluation on three dimensions: cost at scale, funding mechanism, and who bears the transition cost. Without those numbers, this is a wish list. Partial numbers are included; full analysis belongs in a dedicated ECONOMICS.md.

#### Wealth Distribution

- [ ] **Gradual wealth caps and redistribution schedules**
  - *Scale challenge:* Enforcement requires international coordination to prevent capital flight. Existing partial precedents: Norway's sovereign wealth fund (Government Pension Fund Global -- 1.6 trillion USD in assets, funded by oil revenues, managed with democratic accountability). Switzerland's wealth tax (annual, applied at cantonal level, rates vary by canton). No country has implemented hard wealth caps.
  - *The capital flight problem is real and has to be addressed directly, not hand-waved. The OECD Global Minimum Tax (Pillar Two, 2021) -- 15% minimum corporate rate across 140+ countries -- is the first serious attempt at coordinated international tax enforcement. It's partial and riddled with carve-outs, but it demonstrates the mechanism is achievable.*

- [ ] **Universal Basic Income as a bridge mechanism**
  - *Scale (US): $1,000/month to all adults = approximately 3-4 trillion dollars/year (roughly the entire federal budget). The arithmetic is stark.*
  - *Proposed funding mechanisms that partially close the gap:*
    - Land value tax: approximately 1.7 trillion dollars potential (estimates vary widely -- Tideman & Plassmann, 2004)
    - Carbon tax: approximately 200 billion dollars at $50/ton (EPA social cost of carbon estimate)
    - Financial transaction tax: approximately 75 billion dollars (estimate based on EU FTT proposals)
    - Automation dividend / robot tax (proposed by Gates, Piketty et al., modeled in IMF staff papers)
    - Sovereign wealth funds built from natural resource commons
  - These do not fully close the gap at current scale. UBI at this level requires simultaneous cost reduction through selective abundance -- cheaper energy, food, housing, healthcare. The math works only if the Phase 1 systems are also being built in parallel.
  - *Evidence base: 100+ pilot programs tracked at guaranteedincome.us. Notable: Stockton SEED (California), Finland's 2017-2018 experiment, Kenya GiveDirectly (long-term). Pilots show positive effects on mental health, employment, and food security. None have been run at national scale in wealthy nations.*

- [ ] **Cooperative and mutual ownership replacing corporate structures**
  - *Best evidence: Mondragon Cooperative Corporation (Basque Country, Spain) -- founded 1956, now 80,000+ worker-owners, 12 billion euros+ annual revenue. Multiple business lines including manufacturing, retail (Eroski), and a university. Governance: one worker, one vote.*
  - *Honest limits of Mondragon as a model:*
    - Fagor Electrodomesticos (the washing machine company, Mondragon's founding business) declared insolvency in 2013 after market competition from Asian manufacturers. 5,600 workers displaced. The cooperative system absorbed some through redeployment, but not all.
    - Mondragon increasingly employs non-member temporary workers, particularly in Eroski supermarkets. The cooperative principle frays at the edges under competitive pressure.
    - The transition path from a 100,000-employee global supply chain with geographically distributed operations and complex capital structures to worker ownership is not a known solved problem. Mondragon's model works at specific scales and in specific cultural contexts.
  - *Italy's Marcora Law (1985):* Government-backed low-interest loans for workers who use their unemployment benefits as collateral to buy out their employer. Has created thousands of worker cooperatives in Italy. Replicable mechanism.
  - *The Emilia-Romagna region (Italy):* 40% of GDP produced by cooperatives. The cooperative ecosystem effect -- cooperatives preferentially buy from other cooperatives -- creates resilience. (Zamagni & Zamagni, "Cooperative Enterprise," 2010)

- [ ] **Debt jubilee -- cancellation of unjust debts**
  - *Scale: US student debt approximately 1.7 trillion dollars (Federal Reserve, 2024); medical debt approximately 220 billion dollars (KFF, 2022); developing-nation external debt approximately 3 trillion dollars (World Bank International Debt Statistics, 2024).*
  - *The problem with partial jubilees:* Debt held as an asset by pension funds, retirement accounts, and banks with depositors. Canceling debt is a wealth transfer from whoever holds the debt as an asset -- which includes many ordinary people's retirement savings. A jubilee without a plan for downstream losses is a wealth transfer from some regular people to other regular people. This requires careful sequencing and clarity about who absorbs the loss.
  - *Historical precedent: The 1953 London Debt Agreement canceled approximately half of West Germany's postwar debt and restructured the remainder, with payments linked to Germany's trade surplus. Often cited as enabling the Wirtschaftswunder. Analysis: Ritschl, "Germany, Greece, and the Marshall Plan" (2012).*

- [ ] **Community wealth funds -- regional pools of shared resources**
  - *Existing models: Alaska Permanent Fund (oil-revenue sovereign wealth fund, pays annual dividend to all residents -- approximately $1,300-$2,000/year -- since 1982); Aberdeen Asset Management has analyzed CLT-adjacent land wealth fund models at municipal scale. Norway's GPFG is the largest sovereign wealth fund by assets.*

#### Land Transition

Already covered in housing section above. The circular dependency is real and should be named:
- Full land transition requires the values transformation that's listed as a Phase 3 outcome.
- Phase 3 values transformation requires Phase 1 systems that work.
- The honest path is CLTs and public land as proof-of-concept, not grand proclamation.

#### Dismantling Unjust Power

- [ ] Corporate charter revocation for entities acting against public interest
  - *Legal precedent: Corporate chartering is a state-granted privilege, not a right. Attorney General actions to dissolve corporations exist in US law. Recent use: New York AG against National Rifle Association (2020, initially dismissed, refiled). The mechanism exists; using it against major corporations is politically unprecedented in modern US context.*
- [ ] Lobbying and political bribery criminalized
  - *Current status: Citizens United v. FEC (2010) treats corporate political spending as protected speech under the First Amendment. This is a constitutional problem, not just a legislative one. Requires either constitutional amendment or a Supreme Court reversal.*
- [ ] Monopoly dissolution in energy, media, tech, and agriculture
  - *Precedent: AT&T breakup (1984); Standard Oil breakup (1911). Modern application: DOJ antitrust action against Google (2024 ruling finding illegal monopoly maintenance in search). The tools exist.*
- [ ] Tax havens dismantled through international cooperation
  - *Reality check: Tax havens exist because some nation-states benefit from them. Luxembourg, Cayman Islands, British Virgin Islands, Ireland -- these are not rogue states; they are rational actors extracting rent from international capital flows. Dismantlement requires the cooperation of states that profit from the status quo.*
  - *Progress: OECD Global Minimum Tax (Pillar Two) -- 15% minimum corporate rate; automatic information exchange agreements (CRS, FATCA) that have meaningfully reduced bank secrecy. These are real but partial victories. Full dismantlement requires political leverage that doesn't currently exist.*
- [ ] Transparent asset registries -- no hidden beneficial ownership
  - *Progress: UK's Register of Overseas Entities (2022) requires disclosure of foreign beneficial owners of UK property. US Corporate Transparency Act (2024) requires beneficial ownership disclosure. Both have gaps and enforcement challenges but represent directional movement.*

---

### 1.4 Energy and Infrastructure

#### Energy Sovereignty

- [ ] **100% renewable, community-owned energy grids**
  - *Technical feasibility: NREL's 2022 Electrification Futures Study and Princeton's Net Zero America report both show technically feasible pathways to 100% clean electricity at US scale. The constraint is capital, grid infrastructure, and policy -- not physics.*
  - *Community ownership precedent: Rural Electric Cooperatives -- 900+ member-owned utilities serving 42 million Americans across 56% of US land area. Cooperative ownership of energy infrastructure is not new or experimental; it has existed since the Rural Electrification Act of 1936.*
  - *International example: Feldheim, Germany -- village of 145 households that owns 100% of its energy generation (wind + biogas) and has since 2010. Per-kilowatt-hour cost to residents is lower than national grid average.*

- [ ] **Decentralized generation at household and community scale**
  - Solar cost curve: utility-scale solar has dropped approximately 90% in cost over the past decade (IRENA, 2023). Residential solar payback period has fallen below 6-8 years in most US markets. The economics are now favorable without subsidies in high-insolation areas.
  - *Problem: Decentralized generation creates grid stability challenges. Solutions exist (grid storage, demand response, virtual power plants) but require investment and coordination.*

- [ ] **Energy as a public utility, not a commodity**
  - The distinction matters: commodities are priced by markets and distributed to those who can pay. Utilities are priced by regulators and distributed by connection. Community ownership of energy generation removes the profit motive from a fundamental need.

#### Digital Commons

- [ ] **Internet as a public utility**
  - *Municipal broadband precedent: Chattanooga, TN's EPB Fiber -- fastest internet in the US at its launch, municipal utility, gigabit service widely available. Similar: Stockholm's Stokab open-fiber network.*
  - *Rural broadband gap: FCC data (debated -- many researchers argue FCC data significantly overstates coverage) shows significant rural and tribal access gaps. Infrastructure Investment and Jobs Act (2021) allocates $65 billion for broadband expansion.*

- [ ] **Data sovereignty -- personal data belongs to individuals**
  - *Legal framework: GDPR (EU, 2018) establishes data minimization, purpose limitation, right to deletion, and data portability as legal requirements. California Consumer Privacy Act (CCPA) and Consumer Privacy Rights Act (CPRA) partial US analogs.*
  - *The gap: These frameworks give individuals rights but do not establish community data governance. Data generated by a community (traffic patterns, health outcomes, energy use) is currently captured by the platforms that mediate it, not by the community that produced it.*

- [ ] **Open-source everything**
  - *Scale of existing open-source commons:* Linux kernel powers approximately 97% of the world's top 1 million servers. Apache HTTP Server, PostgreSQL, Python, Kubernetes -- the infrastructure of the internet is substantially open-source. The commons is already the dominant model for software infrastructure; the framework proposes extending this logic to hardware (Open Source Ecology -- 50 open-source industrial machines), pharmaceuticals, and research.

- [ ] **AI governance -- publicly auditable algorithms**
  - *The problem: Algorithmic systems that affect hiring, credit, criminal justice, social media exposure, and healthcare access are currently proprietary. No external audit is possible.*
  - *Existing frameworks: EU AI Act (2024) -- risk-based regulation, mandatory transparency for high-risk AI systems. US Executive Order on AI (2023). These are a start.*
  - *What the framework requires beyond existing regulation: Mandatory open publication of training data, model architecture, and evaluation methodology for algorithms with significant public impact. The technical tools for this (model cards, datasheets for datasets, algorithmic auditing) exist and need regulatory backing.*

#### Transportation

- [ ] **Free public transit**
  - *Precedent: Tallinn (Estonia) free transit since 2013; Luxembourg nationwide free transit since 2020; Kansas City, MO since 2020. None have eliminated car use but all show ridership increases and equity benefits for low-income residents.*
  - *Cost: Typically offset by savings in road maintenance, healthcare (air quality), and parking infrastructure.*
- [ ] Shared vehicle networks replacing private car ownership
- [ ] Walkable, bikeable communities by design
  - *Evidence: Netherlands and Denmark show that cycling infrastructure at city scale dramatically reduces car dependency. Not a cultural predisposition -- it's a built environment outcome. (Pucher & Buehler, "City Cycling," 2012)*

---

## Tensions and Tradeoffs

> The core principles are in tension with each other. Pretending otherwise would be dishonest. These tensions are not bugs -- they are the hardest design problems. They do not have clean answers. Anyone presenting this framework without engaging these tensions is selling something.

### Democratic Sovereignty vs. Ecological Equilibrium

What happens when a democratic majority votes to allow resource extraction that violates planetary limits? This is not hypothetical -- it is the story of every coal-dependent community that votes to keep mines open, every fishing village that votes against catch limits.

**The framework's position:** Ecological limits function like constitutional rights -- they are not subject to majority override. Just as a majority vote cannot legally strip a minority of civil rights in a constitutional democracy, a majority vote cannot strip future generations of a livable planet. Planetary boundaries are pre-political: they exist whether or not anyone votes for them.

This means democratic sovereignty is real but bounded. You may govern how you live within the limits of what the earth can sustain. You may not vote to exceed those limits.

**Open problem:** Who defines the planetary boundaries, and who enforces them when democratic institutions disagree? This requires a body of scientific governance that is itself democratically accountable but insulated from short-term political pressure. No such body currently exists at adequate scale. The IPCC comes closest in the climate domain but has no enforcement authority.

This is a genuine constitutional design problem, not a rhetorical one. See Issue #35.

---

### Voluntary Contribution vs. Universal Sufficiency

If contribution is truly voluntary, who does the unglamorous work? Sewage treatment. Garbage collection. Elder care at 3 AM. Slaughterhouse labor. Psychiatric emergency response.

Every intentional community, commune, and cooperative in history has confronted this. The kibbutz movement developed elaborate systems for task rotation, compensation differentials, and eventually reintroduced wage labor for roles voluntarism could not reliably fill. Historical analysis: Near & Moshe, "The Kibbutz Movement: A History" (2008).

**The framework's position:** Voluntary contribution means work is not performed under threat of starvation. It does not mean all work is equally pleasant. Mechanisms for necessary-but-unpleasant work, in order of preference:

1. **Automation** -- priority target. If a task is necessary and undesirable, automate it first.
2. **Rotation** -- shared burden distributed on a schedule.
3. **Compensation premiums** -- additional resources for roles that remain undesirable after automation.
4. **Genuine voluntarism** -- some people find meaning in work others find unpleasant. This is real and documented, not wishful thinking.

**Open problem:** Free-rider dynamics are documented in every commons. Ostrom's design principles (clear boundaries, monitoring, graduated sanctions, conflict resolution, external recognition) are the best available empirical framework for managing realistic human behavior, but they require enforcement mechanisms not yet fully specified here. See RESEARCH.md and Issue #35.

---

### Common Ownership vs. Cultural Adaptation

The framework says the commons belongs to everyone and that local implementation is culturally adapted. These conflict the moment a community uses "cultural adaptation" to exclude someone from the commons.

**The framework's position:** Local communities may govern *how* resources are distributed and *what* governance processes look like. They may not govern *whether* a person is entitled to food, shelter, healthcare, or safety. Cultural adaptation is permitted within the commons. Using cultural adaptation to deny commons access is not.

**Open problem:** Who decides when a local community has crossed from adaptation into exclusion, and with what enforcement authority? This is the federalism problem in its oldest form. The EU struggles with it constantly. The US struggled with it violently for a century. The framework does not have a clean answer.

---

## On Human Nature

The framework does not assume humans are angels. It also does not assume they are irredeemably selfish economic maximizers. The empirical record suggests neither extreme is accurate.

Humans are:
- Capable of genuine cooperation, especially in small groups with clear shared stakes (Axelrod, "The Evolution of Cooperation," 1984)
- Also capable of defection, free-riding, status competition, in-group favoritism, and apathy, particularly in large anonymous settings
- Heavily influenced by the incentive structures they live within -- people surviving under coercive conditions behave coercively; people in secure, dignified conditions tend to behave better (though not always)

**The design principle:** Build systems for the full range of human behavior. Don't design for angels; don't design for demons. Design for humans.

Elinor Ostrom's work on commons governance is the most empirically grounded framework available: clear boundaries, rules proportional to local conditions, collective choice arrangements, monitoring, graduated sanctions, conflict resolution mechanisms, recognition by external authorities, and -- crucially -- nested governance for larger-scale commons. These principles were derived from extensive fieldwork on successfully governed commons across multiple cultures and time periods ("Governing the Commons," 1990). Ostrom won the Nobel in Economics in 2009 for this work.

The failure mode this framework is designed to avoid is not "people will behave badly" -- that's manageable with good systems. The failure mode is "the systems will be designed by and for the people with power to design them." That's the actual problem.

---

## What Phase 1 Is Not

Phase 1 is not a shopping list of nice things. It is a set of minimum conditions for a stable transfer of power to be survivable. "Survivable" means: people don't lose access to food, shelter, and healthcare during the transfer; the new systems don't fail during the transition period; there is no power vacuum that authoritarians can fill.

Each Phase 1 item has two relevant questions that this document tries to answer honestly:
1. Does this work at some proven scale? (Evidence check)
2. What stands between the current proven scale and the required scale? (Honest gap)

Where the answer to (2) is "nothing yet," the document says so.

---

*See [THEORY-OF-CHANGE.md](THEORY-OF-CHANGE.md) for Phase 2 (the transfer) and Phase 3 (post-transfer governance), plus the rigorous engagement with power, historical cases, and the mechanisms through which transitions actually happen.*
