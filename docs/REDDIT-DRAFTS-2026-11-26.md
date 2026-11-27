# Reddit drafts, 26 November 2026

Status: **drafts only. Nothing here has been posted.** A human posts from their
own account after reading each community's current rules. Reddit was not
reachable from the drafting environment, so no subreddit rule, flair or
self-promotion limit below has been checked. Follow [OUTREACH.md](../OUTREACH.md).

## What is and is not known

- The repository holds no record of an earlier Reddit post. `outreach-log.md`
  lists one Moltbook post and four GitHub issues from April. If a Reddit post
  did get replies, add its URL, subreddit, date and what people responded to
  in the log. That thread is the best evidence available about what works and
  these drafts should be revised against it.
- No analytics baseline exists ([TRAFFIC-2026-11-03.md](TRAFFIC-2026-11-03.md)),
  so a post's effect cannot be measured yet beyond replies and corrections.
- Every prior attempt recorded here led with the project. Each draft below
  leads with something the reader can use or correct in two minutes, states a
  real weakness, and asks one question.

## Rules for posting

1. One community per post, written for that community. No cross-posting.
2. Say you built it. Say what is wrong with it.
3. Stay in the thread for 48 hours and answer everything. Apply corrections
   and reply with what changed.
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

It is free, has no login and no tracking, and the data is downloadable.

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

## Draft 3: place-based or solarpunk communities (for example r/solarpunk)

**Title:** A map for answering "who near me is already doing this?" Looking for people to break it

**Body:**

If you wanted to start a tool library, a food co-op or a community land
trust, the first question is who nearby already runs one or could help. I
built a map for that question from open registries and directories:
https://commonweave.earth/find-community-organizations.html

Pick a goal and a place, and it lists organizations to look into along with
the roles a project like that usually needs and which ones the data has no
candidate for.

It is a list of leads to check, not a list of vetted partners. Locations are
often city-level, coverage outside the US and UK is thin, and the suggested
connections between organizations are guesses from category and distance.

I am looking for five people willing to try it for a real place and tell me
whether it found anything they did not already know about. If it did not, I
want to know that too.

## After posting

Record replies and corrections in `outreach-log.md`. Count a post as useful
only if it produces an applied correction, a named directory worth linking,
or someone reporting a lead they used. Upvotes and visits are not that.
