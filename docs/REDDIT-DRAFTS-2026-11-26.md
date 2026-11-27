# Reddit drafts, 26 November 2026

Status: **drafts only. Nothing here has been posted.** A human posts from their
own account after reading each community's current rules. Reddit was not
reachable from the drafting environment, so no subreddit rule, flair or
self-promotion limit below has been checked. Follow [OUTREACH.md](../OUTREACH.md).

## What the April posts show

Read from a public Reddit archive on 2026-11-27 (Reddit itself was not
reachable). Scores and counts are as archived and may differ from live values.

| Date | Where | Result |
|---|---|---|
| 2026-04-12 | [r/solarpunk](https://www.reddit.com/r/solarpunk/comments/1sj5ppk/) "Ecolibrium: An open-source blueprint for peaceful transition to post-scarcity" | Score 29, 32 comments. Linked the GitHub repo. |
| 2026-04-13 | [r/singularity](https://www.reddit.com/r/singularity/comments/1sjyz9g/) and [r/accelerate](https://www.reddit.com/r/accelerate/comments/1sjz08q/), same pitch | Score 0, no comments each. |
| 2026-04-25 | [r/web_design](https://www.reddit.com/r/web_design/comments/1sv0475/) asking to hire a map designer | Removed by moderators under the no-solicitation rule. One person asked for sample data. |

The r/solarpunk thread is the only one that drew a response, and most of the
response was objection. The comments with the most votes said, in order:

1. Another high-level "how society could be structured" post; the community
   sees these every few days and prefers do-it-yourself work (17 votes).
2. The post and the document read as AI-written, and that alone would put
   people off (12 votes; three more comments made the same point).
3. Organize something real instead of publishing a framework (7 votes).
4. It reads as a wishlist that points at other frameworks without the
   mechanics (4 votes).

The author's replies that told critics to fix it themselves ("then rewrite
it", "then help") were voted down, to as low as -6. The reply that accepted
the criticism was not. A few readers were interested, one said they reused
part of the project, and one asked where to read it.

What this changes:

- **Engagement was not approval.** Thirty-two comments came from a
  disagreement about AI authorship and manifestos, not from people using the
  work. It is weak evidence of demand and good evidence about what not to do.
- **Do not lead with a framework, blueprint, or transition.** The repository
  has since moved to "a directory and map"; posts should follow.
- **Write the post by hand.** The drafts below were produced with AI and say
  so here. Use them for structure and facts; the posted words should be the
  poster's own.
- **Say up front how AI was used**: the data pipeline and much of the
  documentation are AI-assisted. Being told is tolerated far better than
  finding out.
- **Never answer a critic with "then fix it."** Thank them, say what will
  change, change it, and report back.
- **r/solarpunk has seen the framework pitch once.** A second post there has
  to be a different thing: a tool someone can use, with the earlier thread
  acknowledged.
- **Read the rules first.** The r/web_design removal was avoidable.
- Cookieless visit counting was added on 2026-11-27
  ([TRAFFIC-2026-11-03.md](TRAFFIC-2026-11-03.md)). Wait for two weeks of
  baseline before posting, so a post's effect can be seen.

## Rules for posting

1. One community per post, written for that community, in the poster's own words. No cross-posting.
   State in the post that the data pipeline and documentation are AI-assisted.
2. Say you built it. Say what is wrong with it.
3. Stay in the thread for 48 hours and answer everything. Apply corrections
   and reply with what changed. Do not tell a critic to fix it themselves.
4. At most one post a week. Stop if a moderator or the thread says it is not
   wanted there.
5. Log each post in `outreach-log.md`: URL, date, replies, corrections received.

## Draft 1: co-operative communities (for example r/cooperatives)

**Title:** I mapped ~29,000 co-ops, land trusts and mutual aid groups from open data. Most of the pins have a known problem. Can you check your city?

**Body:**

I maintain an open directory and map of cooperative and community
organizations, built from public registries and directories such as ICA,
Transition Network, the Schumacher CLT map and Mutual Aid Hub:
https://commonweave.earth/map.html

It is free, has no login, no cookies and no ads, and the data is downloadable.

What is wrong with it, so you do not have to find out the hard way:

- 11,399 UK records are pinned to one dot in the middle of Scotland because
  they were geocoded to the country, not the town.
- About 9,800 records are hidden by a data bug.
- Coverage is mostly US and UK. Most countries have under 50 entries.
- A pin means "a public source lists this organization". It does not mean it
  is active or that it does what its category says.

The ask: zoom to a place you know. Tell me one organization that is missing,
dead or miscategorized. I will fix it and reply here with the change. There is
also a correction form: https://commonweave.earth/participate.html

If a directory already does this well for your area, I would rather link to
it than duplicate it. Which ones do you use?

## Draft 2: open data communities (for example r/opendata or r/datasets)

**Title:** Open dataset: 158k candidate nonprofit, co-op and mutual aid records from 25 public sources, with a published audit of its own defects

**Body:**

Dataset: https://github.com/simonlpaige/commonweave/tree/master/releases
(gzipped CSV and JSON, plus per-country and per-source splits).

Sources include Brazil's Mapa das OSCs, Australia's ACNC register, the IRS
exempt organizations file, the UK Charity Commission, Wikidata, and smaller
directories for co-ops, land trusts, transition groups and mutual aid.
Per-source licences differ; they are listed in DATA.md and the whole set
should not be treated as CC0.

The audit is the part I would like checked:
https://github.com/simonlpaige/commonweave/blob/master/docs/DATA-AUDIT-2026-09-05.md

Headline defects: 82% of rows are Brazil or Australia; 110,813 rows have no
website; 6,259 same-name-and-country groups may be duplicates; almost no row
has a verification date.

Questions for people who have done this before:

1. What is a sane entity-resolution approach across registries with no shared
   identifier, when the same name in the same country is often a real second
   organization?
2. Which open registries with coordinates and websites am I missing?

## Draft 3: r/solarpunk, only as a follow-up to the April thread

**Title:** In April I posted a "blueprint" here and you told me to build something instead. Here is the something. Tell me if it is useful.

**Body:**

In April I posted a framework for a post-scarcity transition. The top replies
were that it was another manifesto, that it read as AI-written, and that
organizing beats theorizing. That was fair.

What I kept working on is the practical part: a map for the question "who
near me is already doing this?" If you want to start a tool library, a food
co-op or a land trust, it lists organizations nearby to look into, the roles
a project like that usually needs, and which roles the data has nobody for:
https://commonweave.earth/find-community-organizations.html

Plainly: the data pipeline and most of the documentation are built with AI
assistance, from open registries and directories. I check and correct it by
hand, and a lot of it is still wrong. Locations are often only city-level,
coverage outside the US and UK is thin, and the suggested connections between
organizations are guesses from category and distance. These are leads to
check, not vetted partners.

I am looking for five people to try it on a place they know and tell me
whether it found anything they did not already know about. "No, it was
useless, and here is why" is an answer I can use.

## After posting

Record replies and corrections in `outreach-log.md`. Count a post as useful
only if it produces an applied correction, a named directory worth linking,
or someone reporting a lead they used. Upvotes and visits are not that.
