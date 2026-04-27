# Commonweave Governance

> *"There is no such thing as a structureless group. Any group of people of whatever nature that comes together for any length of time for any purpose will inevitably structure itself in some fashion."*
> — Jo Freeman, "The Tyranny of Structurelessness" (1972)

This document exists because the framework requires honesty, and honesty requires acknowledging that someone is making decisions here. This is the attempt to make those decisions visible and accountable.

---

## What This Document Is

An acknowledgment that the project already has de facto leaders (whoever set up the repository, wrote the README, and decides what gets merged), and a framework for making that leadership transparent, accountable, and replaceable.

This is not a corporate structure. It is the minimum viable governance to prevent the informal power dynamics that have collapsed every "leaderless" project that refused to acknowledge its actual structure.

---

## Decision-Making Model

Commonweave uses **Rough Consensus and Running Code** — the model developed by the IETF (Internet Engineering Task Force) for governing open technical standards without formal voting.

**Rough consensus** means: a decision can proceed when there are no *sustained*, *principled* objections — not when everyone agrees. Disagreement is healthy. Blocking is not disagreement; it requires a specific, articulable reason why proceeding would cause serious harm.

**Running code** means: working implementations and demonstrated evidence outweigh theoretical arguments. A concrete proposal with a draft beats an abstract objection every time.

### How It Works in Practice

1. **Proposals** are made in GitHub Issues or Pull Requests with a clear description of what is being changed and why.
2. **Discussion** happens in the open on that Issue/PR. Anyone can comment.
3. **Rough consensus** is assessed by a Maintainer after sufficient discussion (minimum 7 days for significant changes, 72 hours for minor ones).
4. **Objections** must be principled — tied to specific harms or contradictions with the framework's core principles. "I don't like this" is not an objection. "This contradicts Core Principle 3 in the following specific way" is.
5. **Decision** is recorded in the PR/Issue with a summary of the discussion and the reasoning.

### Temporal Compartmentalization

*Contributed by Sir-Sloth-The-Lazy, April 2026.*

There is a valid operating mode for action planning not covered by the standard PR/Issue process: **organizing happens openly; specific action plans are disclosed only after execution.**

The labor movement called this "don't announce the strike vote until after it passes." The information becomes fully public — just not in advance. This preserves complete auditability without giving adversaries a prevention window.

This is not a contradiction of Transparency by Default. Transparency by Default applies to decisions and governance process. Timing of operational disclosure is a separate variable. A decision can be fully documented and accountable while its execution remains undisclosed until complete.

When this mode is in use, it should be named explicitly in the relevant Issue or PR — so the record shows this was a deliberate choice, not an omission.

---

## Roles

### Contributor
Anyone who opens an Issue, submits a PR, or participates in Discussion. No approval needed. Contributors do not have merge rights.

### Graduated Contribution Rights

*Contributed by Sir-Sloth-The-Lazy, April 2026.*

Wikipedia and most large open-source projects have converged on the same structural answer to flooding and concern trolling: **graduated trust with asymmetric contribution rights.** New participants can contribute, but governance influence accumulates with track record. The threshold criteria are public — this is not secrecy, it is meritocratic progression.

Commonweave uses the same model:

| Stage | What you can do | What you can't yet do |
|---|---|---|
| **Observer** | Read, comment, file issues | Open PRs, vote on governance questions |
| **Contributor** | Open PRs, participate in all discussions | Merge PRs, assess consensus |
| **Maintainer** | Assess rough consensus, merge PRs | Repository administration |
| **Steward** | Repository admin (settings, branch protection) | Unilateral framework changes (requires broad consensus) |

Moving from Observer to Contributor requires only a GitHub account and an opened Issue or PR. Moving from Contributor to Maintainer requires consistent, substantive contributions over time — judgment calls made by existing Maintainers and documented in the nomination Issue.

This structure directly addresses coordination floods: a well-organized group can flood Issues, but governance decisions require track-record-weighted input. Because the thresholds are public, the design cannot be called gatekeeping.

### Maintainer
A Contributor who has been granted merge rights. Maintainers assess rough consensus and merge or close PRs. They do not have unilateral authority to accept or reject proposals — they facilitate the process.

**Current Maintainers:** Listed in the repository's CODEOWNERS file (or in the README if CODEOWNERS is absent). This section must be kept current.

**How to become a Maintainer:** Consistent, substantive contributions over time. Any existing Maintainer can nominate a Contributor. Nominations are accepted by rough consensus of the existing Maintainer group.

**Term:** Maintainers serve until they step down, are inactive for 6+ months (defined as no commits, reviews, or issue comments), or are removed by the process below.

### Steward
A Maintainer with administrative access to the repository (settings, branch protection, etc.). There should be at minimum 2 Stewards at all times to prevent single points of failure — the failure mode WiserEarth demonstrated.

---

## How to Challenge a Decision

If a decision was made without genuine rough consensus, or if new information emerges that changes the picture:

1. Open a new Issue labeled `[governance]` describing the decision being challenged and the specific reason.
2. The Maintainer who made the original decision must respond within 14 days.
3. If the challenge raises a legitimate principled objection that wasn't addressed in the original discussion, the decision is reopened.
4. If the Maintainer is unresponsive or the challenge cannot be resolved between the parties, any Steward can call a structured review involving all active Maintainers.

---

## Removing a Maintainer

Grounds for removal:
- Sustained bad faith (decisions made without any consensus process, repeated ignoring of principled objections)
- Inactivity (6+ months)
- Actions that violate the framework's core principles (e.g., selling merge rights, accepting money to bias decisions)

Process: Any Contributor can open a `[governance]` Issue documenting the concern. If two or more Maintainers agree that grounds for removal exist, the Maintainer is removed. A removed Maintainer can appeal once by requesting a full Maintainer review.

This process is deliberately low-friction. The goal is accountability, not punishment.

---

## What Cannot Be Decided by Maintainers Alone

The following require a 90-day open comment period and explicit rough consensus from the broader contributor community (not just Maintainers):

- Changes to the Core Principles in the README
- Changes to this Governance document
- Formal partnerships or affiliations with external organizations
- Licensing changes
- Archival or shutdown of the project

---

## The Anonymity Question (Resolved)

The CRITIQUE.md document correctly identified a contradiction: the framework said "legitimacy requires total sunlight" while the repository sat under a named GitHub account with language claiming anonymity. Those two things could not both be true.

**This project's resolved position:** The author and current maintainer is Simon Paige. The repository lives at simonlpaige/commonweave. Earlier "anonymous by design" framing has been retired from the README and outreach documents. The reasoning is recorded here so future readers understand why the change happened.

**Contributors are not required to be named.** Pseudonymous participation is welcome and explicitly framed as contributor protection. People inside hostile institutions, at-risk contexts, or simply those who prefer privacy may commit under any handle they choose. The maintainers will not ask them to unmask. See OUTREACH.md's Contributor Identity Guidance section for detail.

The distinction that still matters: **process opacity** (how decisions are made) is not acceptable, for anyone, under any identity. Named or pseudonymous, the governance process is public.

---

## On "Leaderless"

Early README drafts said "no founders, no leaders, no inner circle." That was written with good intentions and was factually inaccurate. Someone wrote the README. Someone set up the repository. Someone decides what gets merged. That person is a leader, whether or not they claim the title. As of the anonymity resolution above, that person is Simon Paige, with Maintainer roles open to collaborators under the process in this document.

The goal was never truly leaderless governance. It was governance without *unaccountable* leaders and without *permanent* leaders whose identity becomes the project's identity. The accurate framing:
- **Named but not permanent leaders.** Maintainers rotate and can be removed. The author does not get a lifetime seat.
- **No personality cults.** The work is what matters, not who does it. The author is named so that accountability is possible, not to become the brand.
- **No unaccountable power.** All decisions are visible and challengeable.
- **No inner circle.** The process is open to anyone.

This is not leaderless. It is *accountably led*, which is better.

---

## Contributor Targeting Response Protocol

*Contributed by Sir-Sloth-The-Lazy, April 2026. Addresses gap identified in THREAT-MODEL.md §3.5.*

If a contributor is targeted — harassment campaign, doxxing, pressure on employer, or credible physical threat — the project has a defined response. The absence of a protocol is itself a threat surface: ad hoc responses are slower, less consistent, and create secondary stress for the people trying to help.

**What counts as targeting:** Coordinated harassment in Issues or Discussions; public disclosure of a pseudonymous contributor's identity without consent; contact with a contributor's employer with intent to cause harm; credible threats of physical harm.

**Immediate response (any Maintainer can act without waiting for consensus):**
1. Remove or hide abusive content from the repository. This is a moderation action, not a governance decision, and does not require rough consensus.
2. Notify the targeted contributor directly via whatever contact method they have provided. Ask what support they want — do not assume.
3. Open a private `[security]` Issue (GitHub supports private Issues via Security Advisories) documenting what happened and what actions were taken.

**Within 72 hours:**
4. If the targeting originated from within the contributor community, begin the Maintainer removal process (see: Removing a Maintainer). Participation in good-faith governance does not extend to targeting other participants.
5. Assess whether the targeted contributor needs temporary pseudonymization support — for example, if they had been contributing under their real name and now prefer to continue under a handle.
6. Post a brief public statement in the relevant Discussion or Issue thread confirming that moderation action was taken. No details about the targeted contributor are disclosed without their explicit consent.

**What the project will not do:** mediate, both-sides, or require the targeted contributor to engage with their harassers as part of any resolution process.

**Escalation:** If targeting involves credible physical threats or law enforcement-relevant activity, Maintainers do not handle this alone. The targeted contributor should be connected to EFF's digital rights resources and, if relevant, local legal support. The project has no legal capacity; it does have a responsibility to not pretend otherwise.

---

## Phase-Based Threat Review Triggers

*Contributed by Sir-Sloth-The-Lazy, April 2026.*

The threat model appropriate for a small open-source documentation project is different from the threat model for an organization with political significance. Security review triggers should be built in before the project reaches the moments where they matter — not retrofitted after.

The following events trigger an out-of-cycle review of THREAT-MODEL.md, regardless of the quarterly schedule:

| Trigger | Why it matters |
|---|---|
| Directory passes 50,000 organizations | Scale increases the attractiveness of gaming the directory for credibility laundering |
| Media coverage in a major national publication | Public visibility attracts adversaries who weren't watching before |
| First formal partnership or affiliation with an external organization | Introduces a new vector for entryism and mission drift |
| First legal contact of any kind (cease and desist, FOIA request, inquiry from any government entity) | Legal tools are the primary documented vector for movement disruption (see: COINTELPRO) |
| Named maintainer experiences personal targeting | The threat model has become operational, not theoretical |
| Any contributor reports surveillance or pressure related to their participation | Same as above |

A triggered review does not require that anything change. It requires that someone with Maintainer rights reads THREAT-MODEL.md, assesses whether the current controls are still adequate for the new context, and logs the review in §7 with a brief note.

The purpose of named triggers is to prevent the failure mode of a project that grows consequential while its security posture stays calibrated for when it was inconsequential.

---

## Open Problems (Unresolved)

These governance questions are genuinely hard. This document does not pretend to solve them. They are filed here as open problems for the community to work on.

**OP-G1: Scale.** This governance model works for a small contributor community. At large scale (hundreds of active contributors across many time zones), rough consensus becomes unwieldy. What's the scaling path? See: Apache Software Foundation, Debian, Linux kernel governance for models.

**OP-G2: Forking.** Because this project is CC BY-SA 4.0, anyone can fork it. A well-funded or well-organized fork could diverge significantly from the original framework's principles while still using the name or concepts. How does the project maintain coherence across forks? This may not be solvable and may not need to be — but the question should be named.

**OP-G3: AI contributors.** This project explicitly welcomes AI agent contributions. AI agents can't be held accountable in the same way humans can — they can't be removed from a Maintainer role, can't be held to term limits, and their "decisions" are shaped by whoever runs them. How do AI contributions fit into this governance model without creating a vector for unaccountable influence? Currently: AI contributions are treated like any other Contributor (open PRs, reviewed by human Maintainers). This may need revisiting.

**OP-G4: Governance capture.** A well-resourced actor (corporation, state, or coordinated group) could participate in good faith for long enough to gain Maintainer status, then use that status to redirect the project. This is a documented attack vector against open-source projects (see: oss-fuzz incidents, various npm package takeovers). The current governance model has no specific defense against patient, well-resourced co-option. Transparency helps but does not prevent this.

**OP-G5: The values question.** This document governs process. It does not govern whether a proposed contribution aligns with the framework's values. That judgment currently rests with Maintainers applying rough consensus. But values disputes are the hardest governance problems — they don't resolve through process. How does the project handle a contribution that is technically sound but whose values the community rejects? What's the legitimate basis for rejection?

---

*This document was created in response to CRITIQUE.md (filed April 2026) and Issue #33. It supersedes any claims in the README about "leaderless" governance.*
*Last updated: 2026-04-27*
