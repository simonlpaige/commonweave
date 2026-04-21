# NeighborhoodOS

> A subprogram of [Ecolibrium](../README.md). Turns a neighborhood association into a self-aware civic entity.

NeighborhoodOS is Ecolibrium's ground-level implementation. Where Ecolibrium maps the global ecosystem of commons-aligned organizations, NeighborhoodOS gives a single neighborhood the tools to govern itself, track city behavior, and connect to that ecosystem.

---

## Position in the Ecolibrium Stack

```
Ecolibrium (global directory + theory of change)
    └── NeighborhoodOS (local implementation layer)
            ├── Civic Intelligence Feed     ← city data + meeting transcripts
            ├── Neighborhood Health Index   ← 311, crime, permits, violations
            ├── Institutional Memory        ← meeting minutes, commitments
            ├── Resident Voice Layer        ← civic-identity/ (signup + voting)
            └── Federation Layer            ← connects to other neighborhoods
                    └── Ecolibrium Directory connection (orgs near you)
```

The Federation Layer is the bridge. When a neighborhood federates with others, it also gains a window into the Ecolibrium directory - organizations, cooperatives, and civic groups already working nearby that align with what residents care about.

---

## Submodules

| Directory | What it does |
|-----------|--------------|
| `connectors/` | Data source connectors (KC Open Data, Legistar, Nextdoor, Facebook Groups) |
| `ingest/` | Cron-ready ingest scripts that populate the local SQLite DB |
| `../civic-identity/` | Signup, trust levels, and federated voting (Layer 4+5) |

---

## Data Sources

### Live API (no scraping needed)
- KC Open Data: 311, permits, crime, violations, budget, vendor payments
- Legistar: city council meetings, ordinances, votes, committee actions

### Social (scrape + parse)
- **Nextdoor** - neighborhood posts, issue reports, event announcements
- **Facebook Groups** - meeting announcements, neighbor discussions, event RSVPs

Social data is treated as signal, not ground truth. It surfaces what neighbors are talking about, not official records.

### Manual / semi-automatic
- Meeting minutes (manual entry or Whisper transcript)
- Commitment tracking (extracted from minutes)
- Resident issue reports (via the Resident Voice API)

---

## Ecolibrium Directory Integration

When a neighborhood is active in NeighborhoodOS, it can query the Ecolibrium directory for:

1. **Nearby aligned organizations** - food co-ops, community land trusts, credit unions, tool libraries, mutual aid networks within the neighborhood's geography
2. **Issue-matched orgs** - if residents keep flagging "housing stability," surface orgs working on housing in KC
3. **Federation candidates** - other neighborhood associations already using NeighborhoodOS that share a boundary or issue cluster

This turns NeighborhoodOS from a local tool into an on-ramp to the broader Ecolibrium ecosystem. A resident asks "who's already working on affordable housing near me?" and gets real answers from the directory, not a search engine.

---

## Deployment

Each neighborhood runs its own node. No central server required.

```bash
# Start everything
cd ecolibrium/neighborhood-os
node ingest/sync.js          # Pull latest city data
node ../civic-identity/api.js  # Start identity + voting API
```

See `connectors/` for individual source setup.

---

## Connection Points to Ecolibrium Core

| NeighborhoodOS concept | Ecolibrium concept |
|------------------------|-------------------|
| Neighborhood boundary | Geographic scope for directory queries |
| Resident trust level 4+ | Eligible to participate in Ecolibrium federation governance |
| Federated vote result | Input to regional/city-level Ecolibrium governance proposals |
| Health Index decline | Trigger for Ecolibrium "mutual aid escalation" signal |
| Commitment tracker miss | Evidence for Ecolibrium accountability layer |

The long game: when enough neighborhoods run NeighborhoodOS, their federated data becomes the empirical backbone for Ecolibrium's theory of change. Not vibes - actual measurements of whether communities are getting more or less sovereign over time.
