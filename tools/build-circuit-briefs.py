#!/usr/bin/env python3
"""
Build static, printable solution-circuit briefs from the public map export.

The briefs are attraction artifacts, not outreach messages. They never send
anything, contain no analytics, and state prominently that every circuit is a
derived, unverified possibility rather than an existing partnership.

Usage:
  python tools/build-circuit-briefs.py
  python tools/build-circuit-briefs.py --check
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlencode, urlparse
from site_navigation import header_markup as shared_header, footer_markup as shared_footer, version_assets


ROOT = Path(__file__).resolve().parents[1]
CIRCUITS_PATH = ROOT / "data" / "map" / "circuits.json"
ORGS_PATH = ROOT / "data" / "map" / "orgs.v3.geojson"
STATS_PATH = ROOT / "data" / "map" / "stats.v3.json"
OUTPUT_DIR = ROOT / "briefs"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"
SOURCE_RECORDS_PATH = OUTPUT_DIR / "source-records.json"
SITEMAP_PATH = ROOT / "sitemap.xml"

SITE_ORIGIN = "https://commonweave.earth"
REPO_ORIGIN = "https://github.com/simonlpaige/commonweave"
ISSUE_BASE = f"{REPO_ORIGIN}/issues/new"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,100}$")

CIRCUIT_ROLE_ORDER = {
    "labor_for_housing": ["land", "build_labor", "finance"],
    "community_food_system": ["grower", "distribution", "access"],
    "land_stewardship_alliance": ["tenure", "steward", "producer"],
    "community_health_mesh": ["clinic", "outreach", "education"],
    "disaster_resilience_grid": ["distribution", "care", "coordination"],
}


BRIEFS_CSS = r"""/* Generated support stylesheet for Commonweave circuit briefs. */
.brief-shell { max-width: 1120px; margin: 0 auto; padding: clamp(42px, 7vw, 92px) clamp(20px, 5vw, 56px) var(--s-9); }
.brief-hero { display: grid; grid-template-columns: minmax(0, 1fr) 210px; gap: var(--s-7); align-items: start; padding-bottom: var(--s-7); border-bottom: var(--rule); }
.brief-hero h1 { font-size: clamp(52px, 8vw, 104px); line-height: .92; font-style: italic; max-width: 13ch; margin: var(--s-4) 0 var(--s-5); text-wrap: balance; }
.brief-hero .lede { color: var(--ink-soft); max-width: 37ch; }
.status-stamp { border: 2px solid var(--clay); color: var(--clay); padding: 18px 14px; font-family: var(--f-mono); font-size: 11px; line-height: 1.45; letter-spacing: .13em; text-transform: uppercase; transform: rotate(2deg); text-align: center; background: color-mix(in oklab, var(--paper) 88%, transparent); }
.status-stamp strong { display: block; font-size: 15px; letter-spacing: .08em; margin-bottom: 6px; }
.brief-meta { display: flex; gap: var(--s-4); flex-wrap: wrap; margin-top: var(--s-5); font-family: var(--f-mono); font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-muted); }
.brief-section { padding: var(--s-8) 0; border-bottom: var(--rule); }
.brief-section h2 { font-size: clamp(38px, 5vw, 66px); max-width: 15ch; margin-bottom: var(--s-6); }
.section-intro { color: var(--ink-soft); font-size: 19px; max-width: 62ch; }
.circuit-loom { position: relative; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s-5); margin-top: var(--s-7); }
.circuit-loom::before { content: ""; position: absolute; left: 10%; right: 10%; top: 31px; height: 2px; background: var(--thread); z-index: 0; }
.role-card { position: relative; z-index: 1; border: var(--rule); background: var(--paper); padding: 58px var(--s-5) var(--s-5); min-height: 245px; }
.role-card::before { content: ""; position: absolute; top: 23px; left: 50%; width: 16px; height: 16px; margin-left: -9px; border-radius: 50%; background: var(--clay); border: 2px solid var(--paper); box-shadow: 0 0 0 1px var(--thread); }
.role-label { font-family: var(--f-mono); font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: var(--clay); }
.role-card h3 { font-size: clamp(24px, 2.4vw, 33px); margin: var(--s-3) 0; }
.role-card p { color: var(--ink-muted); font-size: 15px; }
.role-links { display: flex; gap: var(--s-3); flex-wrap: wrap; margin-top: var(--s-5); font-family: var(--f-mono); font-size: 10px; text-transform: uppercase; letter-spacing: .08em; }
.role-links a { text-decoration: none; border-bottom: 1px solid currentColor; }
.finding { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(260px, .6fr); gap: var(--s-7); align-items: start; }
.finding blockquote { margin: 0; font-family: var(--f-display); font-style: italic; font-size: clamp(27px, 3.2vw, 44px); line-height: 1.16; color: var(--moss-deep); }
.field-note { border-left: 3px solid var(--thread); padding-left: var(--s-5); color: var(--ink-soft); }
.unknowns { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--ink); border: var(--rule); margin-top: var(--s-6); }
.unknown { background: var(--paper); padding: var(--s-5); }
.unknown b { display: block; font-family: var(--f-mono); font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--clay); margin-bottom: var(--s-3); }
.brief-actions { display: flex; gap: var(--s-3); flex-wrap: wrap; align-items: center; margin-top: var(--s-6); }
.brief-button { appearance: none; border: 1px solid var(--ink); background: transparent; color: var(--ink); padding: 10px 16px; font: 500 10px/1 var(--f-mono); letter-spacing: .12em; text-transform: uppercase; text-decoration: none; cursor: pointer; }
.brief-button.primary { background: var(--moss); border-color: var(--moss); color: var(--paper); }
.brief-button:hover { background: var(--paper-2); color: var(--moss-deep); }
.brief-button.primary:hover { background: var(--moss-deep); color: var(--paper); }
.source-note { color: var(--ink-muted); font-size: 14px; overflow-wrap: anywhere; }
.source-note code { font-family: var(--f-mono); font-size: 12px; }
.brief-index-hero { padding-bottom: var(--s-7); border-bottom: var(--rule); }
.brief-index-hero h1 { font-size: clamp(56px, 9vw, 112px); line-height: .91; font-style: italic; max-width: 12ch; margin: var(--s-4) 0 var(--s-5); }
.filter-bar { display: grid; grid-template-columns: minmax(220px, 1fr) 220px; gap: var(--s-3); margin: var(--s-7) 0; }
.filter-bar label { display: grid; gap: 6px; font: 500 10px/1.4 var(--f-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--ink-muted); }
.filter-bar input, .filter-bar select { width: 100%; border: 1px solid var(--ink); border-radius: 0; background: var(--paper); color: var(--ink); padding: 12px 13px; font: 16px/1.3 var(--f-body); }
.brief-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s-5); }
.brief-card { border: var(--rule); padding: var(--s-5); background: color-mix(in oklab, var(--paper) 82%, var(--paper-2)); display: flex; flex-direction: column; }
.brief-card .card-kicker { display: flex; justify-content: space-between; gap: var(--s-3); font-family: var(--f-mono); font-size: 9px; letter-spacing: .11em; text-transform: uppercase; color: var(--ink-muted); }
.brief-card h2 { font-size: clamp(30px, 3vw, 44px); margin: var(--s-4) 0; }
.brief-card ul { list-style: none; margin: 0 0 var(--s-5); padding: 0; color: var(--ink-soft); }
.brief-card li { padding: 7px 0; border-top: var(--rule-soft); }
.brief-card > a { margin-top: auto; align-self: flex-start; font-family: var(--f-mono); font-size: 10px; letter-spacing: .1em; text-transform: uppercase; }
.empty-result { display: none; padding: var(--s-7); border: var(--rule); color: var(--ink-soft); }
.empty-result.visible { display: block; }
body.dark .role-card, body.dark .unknown, body.dark .filter-bar input, body.dark .filter-bar select { background: var(--paper); }
body.dark .status-stamp { background: var(--paper); }
@media (max-width: 820px) {
  .brief-hero { grid-template-columns: 1fr; }
  .status-stamp { max-width: 210px; transform: none; }
  .circuit-loom { grid-template-columns: 1fr; }
  .circuit-loom::before { top: 6%; bottom: 6%; left: 31px; right: auto; width: 2px; height: auto; }
  .role-card { padding: var(--s-5) var(--s-5) var(--s-5) 62px; min-height: 0; }
  .role-card::before { left: 23px; top: 50%; margin: -9px 0 0; }
  .finding, .unknowns, .brief-grid { grid-template-columns: 1fr; }
  .filter-bar { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .nav-links a:not(.nav-cta) { display: none; }
  .brief-shell { padding-left: 18px; padding-right: 18px; }
}
@media print {
  .site-nav, .site-foot, .brief-actions, .filter-bar { display: none !important; }
  body { background: #fff !important; color: #111 !important; font-size: 12pt; }
  .brief-shell { max-width: none; padding: 0; }
  .brief-hero { grid-template-columns: 1fr 150px; }
  .brief-hero h1 { font-size: 52pt; }
  .brief-section { padding: 28pt 0; }
  .role-card, .unknown { break-inside: avoid; background: #fff !important; }
  a { color: #111 !important; }
}
"""


BRIEFS_JS = r"""(function () {
  "use strict";
  var search = document.getElementById("brief-search");
  var country = document.getElementById("brief-country");
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-brief-card]"));
  var count = document.getElementById("brief-visible-count");
  var empty = document.getElementById("brief-empty");

  function applyFilters() {
    var q = search ? search.value.trim().toLowerCase() : "";
    var cc = country ? country.value : "";
    var visible = 0;
    cards.forEach(function (card) {
      var matchesText = !q || (card.getAttribute("data-search") || "").indexOf(q) !== -1;
      var matchesCountry = !cc || card.getAttribute("data-country") === cc;
      var show = matchesText && matchesCountry;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (count) count.textContent = String(visible);
    if (empty) empty.classList.toggle("visible", visible === 0);
  }

  if (search) search.addEventListener("input", applyFilters);
  if (country) country.addEventListener("change", applyFilters);

  document.querySelectorAll("[data-copy-url]").forEach(function (button) {
    button.addEventListener("click", function () {
      var url = button.getAttribute("data-copy-url") || location.href;
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(url).then(function () {
        var previous = button.textContent;
        button.textContent = "Link copied";
        window.setTimeout(function () { button.textContent = previous; }, 1600);
      });
    });
  });
}());
"""


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required input is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def html(value: object) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def normalize_org_id(value: object) -> str:
    raw = str(value or "").strip()
    return raw if raw.startswith("org_") else f"org_{raw}"


def validate_slug(value: object) -> str:
    slug = str(value or "").strip().lower()
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"Unsafe or invalid circuit group id: {value!r}")
    return slug


def safe_website(value: object) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if not re.match(r"^https?://", raw, flags=re.I):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return raw


def compact_number(value: object) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "unknown"


def most_common_nonempty(values: list[object]) -> str:
    cleaned = [str(v).strip() for v in values if str(v or "").strip()]
    if not cleaned:
        return ""
    return Counter(cleaned).most_common(1)[0][0]


def location_for(members: list[dict], country: str) -> str:
    city = most_common_nonempty([m.get("ci") for m in members])
    state = most_common_nonempty([m.get("st") for m in members])
    pieces = [p for p in (city.title() if city else "", state, country) if p]
    return ", ".join(pieces) if pieces else "Location not resolved"


def proximity_text(group: dict) -> str:
    try:
        span = float(group.get("span_km") or 0)
    except (TypeError, ValueError):
        span = 0
    if span <= 0:
        return "Published map locations resolve to the same point"
    if span < 1:
        return f"Published map locations span about {span:.1f} km"
    return f"Published map locations span about {span:.0f} km"


def feature_lookup(orgs: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for feature in orgs.get("features", []):
        props = feature.get("properties") or {}
        org_id = normalize_org_id(props.get("id") or feature.get("id"))
        result[org_id] = props
    return result


def source_record_lookup(payload: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for record in payload.get("records", []):
        org_id = normalize_org_id(record.get("id"))
        result[org_id] = record
    return result


def member_ids(circuits: dict) -> set[str]:
    return {
        normalize_org_id(member.get("id"))
        for groups in (circuits.get("candidates_by_country") or {}).values()
        for group in groups
        for member in group.get("members", [])
    }


def render_source_records(features: dict[str, dict], circuits: dict) -> str:
    public_fields = ("id", "n", "w", "src", "t", "m", "ci", "st", "cc")
    records = []
    for org_id in sorted(member_ids(circuits)):
        props = features.get(org_id, {})
        record = {
            key: props.get(key)
            for key in public_fields
            if props.get(key) not in (None, "")
        }
        record["id"] = org_id
        records.append(record)
    payload = {
        "schema_version": 1,
        "generated_at": circuits.get("generated_at"),
        "source": "data/map/orgs.v3.geojson",
        "note": (
            "Compact public-field snapshot for deterministic circuit brief builds; "
            "contains only organizations referenced by circuits.json."
        ),
        "records": records,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def enrich_group(group: dict, features: dict[str, dict]) -> dict:
    enriched_members = []
    for member in group.get("members", []):
        org_id = normalize_org_id(member.get("id"))
        props = features.get(org_id, {})
        enriched_members.append({
            **member,
            **props,
            "id": org_id,
            "name": member.get("name") or props.get("n") or "Unnamed organization",
            "website": safe_website(props.get("w")),
        })
    role_order = CIRCUIT_ROLE_ORDER.get(str(group.get("circuit")), [])
    rank = {role: index for index, role in enumerate(role_order)}
    enriched_members.sort(
        key=lambda member: (
            rank.get(str(member.get("role")), len(rank)),
            str(member.get("name") or ""),
        )
    )
    country = str(group.get("country") or most_common_nonempty([m.get("cc") for m in enriched_members]))
    return {
        **group,
        "group_id": validate_slug(group.get("group_id")),
        "members": enriched_members,
        "country": country,
        "location": location_for(enriched_members, country),
        "proximity": proximity_text(group),
    }


def flatten_groups(circuits: dict, features: dict[str, dict]) -> list[dict]:
    groups = []
    for country, country_groups in (circuits.get("candidates_by_country") or {}).items():
        if not isinstance(country_groups, list):
            raise ValueError(f"Expected a list of circuit candidates for {country}")
        for group in country_groups:
            groups.append(enrich_group(group, features))
    groups.sort(key=lambda item: (-float(item.get("score") or 0), item["group_id"]))
    if len({g["group_id"] for g in groups}) != len(groups):
        raise ValueError("Circuit group ids are not unique")
    return groups


def logo_markup() -> str:
    return """<svg viewBox="0 0 520 130" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="commonweave">
  <g transform="translate(0,5)">
    <circle cx="60" cy="60" r="56" fill="none" stroke="currentColor" stroke-width="1.6"/>
    <line x1="6" y1="60" x2="114" y2="60" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
    <path d="M 30 30 C 50 60, 70 60, 90 90" stroke="#2F4A33" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <path d="M 90 30 C 70 60, 50 60, 30 90" stroke="#2F4A33" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <circle cx="60" cy="60" r="3" fill="#B4593A"/>
  </g>
  <text x="140" y="80" font-family="Instrument Serif, Source Serif 4, Georgia, serif" font-style="italic" font-size="64" fill="currentColor" letter-spacing="-1.5">commonweave</text>
</svg>"""


def nav_markup(prefix: str = "../") -> str:
    return '<a href="#main-content" class="skip-link">Skip to main content</a>\n' + shared_header(prefix, 'map')


def footer_markup() -> str:
    return shared_footer('../')


def head_markup(title: str, description: str, canonical: str) -> str:
    return version_assets(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html(title)}</title>
<meta name="description" content="{html(description)}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="article">
<meta property="og:title" content="{html(title)}">
<meta property="og:description" content="{html(description)}">
<meta property="og:url" content="{html(canonical)}">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="{html(canonical)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..700;1,8..60,300..700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/brand.css">
<link rel="stylesheet" href="../assets/css/commonweave.css">
<link rel="stylesheet" href="briefs.css">
<link rel="stylesheet" href="../assets/css/site-shell.css">
</head>""", OUTPUT_DIR, {(OUTPUT_DIR / 'briefs.css').resolve(): BRIEFS_CSS.encode('utf-8')})


def correction_url(group: dict) -> str:
    member_lines = "\n".join(
        f"- {member['name']} — proposed role: {member.get('role_label') or member.get('role') or 'unknown'}"
        for member in group["members"]
    )
    body = f"""## Solution-circuit brief correction

**Circuit brief:** {SITE_ORIGIN}/briefs/{group['group_id']}.html
**Group id:** `{group['group_id']}`

The page currently presents this as a **derived, unverified possibility**, not an existing partnership:

{member_lines}

### What needs correction?

<!-- Is an organization inactive, misidentified, in the wrong role, at the wrong location, or unsafe to make more visible? -->

### Public evidence

<!-- Link only to public evidence. Do not post private contact details, addresses, or sensitive operational information. -->
"""
    return ISSUE_BASE + "?" + urlencode({
        "title": f"[Circuit correction] {group['group_id']}",
        "labels": "org-request",
        "body": body,
    }, quote_via=quote)


def render_role_card(member: dict) -> str:
    map_url = f"../map.html#selectedId={quote(member['id'])}"
    website = member.get("website")
    website_link = ""
    if website:
        hostname = urlparse(website).netloc.removeprefix("www.")
        website_link = (
            f'<a href="{html(website)}" target="_blank" rel="noopener">'
            f"{html(hostname)} &#8599;</a>"
        )
    source = member.get("src") or "Source not named in public map export"
    model = str(member.get("model") or member.get("m") or "model unknown").replace("_", " ")
    tier = member.get("t")
    tier_text = f"Tier {html(tier)} &middot; " if tier else ""
    role_links = f'    <a href="{html(map_url)}">View map record</a>'
    if website_link:
        role_links += f"\n    {website_link}"
    return f"""<article class="role-card">
  <div class="role-label">{html(member.get("role_label") or member.get("role") or "Possible role")}</div>
  <h3>{html(member["name"])}</h3>
  <p>{tier_text}{html(model)}<br>Source: {html(source)}</p>
  <div class="role-links">
{role_links}
  </div>
</article>"""


def render_brief(group: dict, stats: dict, generated_at: str) -> str:
    title = f"{group.get('circuit_name') or 'Solution circuit'} in {group['location']}"
    description = (
        f"A derived, unverified Commonweave field note connecting "
        f"{len(group['members'])} nearby organizations with complementary roles."
    )
    canonical = f"{SITE_ORIGIN}/briefs/{group['group_id']}.html"
    roles = "\n".join(render_role_card(member) for member in group["members"])
    correction = correction_url(group)
    built = stats.get("last_built_date") or str(stats.get("last_built") or "")[:10] or "unknown"
    mapped = compact_number(stats.get("orgs_on_map"))
    members = " + ".join(
        html(member.get("role_label") or member.get("role") or "role")
        for member in group["members"]
    )
    return f"""{head_markup(title, description, canonical)}
<body class="cw-page">
{nav_markup()}
<main id="main-content" class="brief-shell" tabindex="-1">
  <header class="brief-hero">
    <div>
      <div class="eyebrow">Solution-circuit field note &middot; {html(group['location'])}</div>
      <h1>{html(group.get('circuit_name') or 'Possible local circuit')}</h1>
      <p class="lede">{html(group.get('problem') or '')}</p>
      <div class="brief-meta">
        <span>{html(group['proximity'])}</span>
        <span>Map snapshot {html(built)}</span>
        <span>{mapped} mapped records</span>
      </div>
    </div>
    <aside class="status-stamp" aria-label="Derived and unverified status">
      <strong>Derived + unverified</strong>
      Possible introduction, not an existing partnership
    </aside>
  </header>

  <section class="brief-section" aria-labelledby="roles-heading">
    <div class="eyebrow">The possible circuit</div>
    <h2 id="roles-heading">{members}</h2>
    <p class="section-intro">Commonweave's public map data places these organizations nearby and classifies their public work as complementary. The classification may be wrong or stale.</p>
    <div class="circuit-loom">
      {roles}
    </div>
  </section>

  <section class="brief-section finding" aria-labelledby="finding-heading">
    <div>
      <div class="eyebrow">Why the system connected them</div>
      <h2 id="finding-heading">A lead worth checking.</h2>
      <blockquote>&ldquo;{html(group.get('explanation') or 'The public descriptions suggest complementary local roles.')}&rdquo;</blockquote>
    </div>
    <aside class="field-note">
      <p><strong>This is not evidence of a relationship.</strong> It is a machine-derived prompt for local knowledge: an invitation to confirm, reject, or refine a possible introduction.</p>
      <p class="source-note"><strong>Pattern source.</strong> <code>{html(group.get('evidence') or 'Not recorded')}</code></p>
    </aside>
  </section>

  <section class="brief-section" aria-labelledby="unknowns-heading">
    <div class="eyebrow">What the map cannot know</div>
    <h2 id="unknowns-heading">Three questions before anyone acts.</h2>
    <div class="unknowns">
      <div class="unknown"><b>01 &middot; Accuracy</b>Do these organizations still exist, and are their proposed roles described correctly?</div>
      <div class="unknown"><b>02 &middot; Consent</b>Do they want to be discoverable and introduced in this way?</div>
      <div class="unknown"><b>03 &middot; Fit</b>Is there a real local need, trust, and capacity for this circuit—or only geographic proximity?</div>
    </div>
    <div class="brief-actions">
      <a class="brief-button primary" href="{html(correction)}" target="_blank" rel="noopener">Correct this brief</a>
      <button class="brief-button" type="button" data-copy-url="{html(canonical)}">Copy brief link</button>
      <button class="brief-button" type="button" onclick="window.print()">Print field note</button>
      <a class="brief-button" href="index.html">All circuit briefs</a>
    </div>
  </section>
</main>
{footer_markup()}

<script src="briefs.js"></script>
</body>
</html>
"""


def render_index(groups: list[dict], stats: dict, generated_at: str) -> str:
    built = stats.get("last_built_date") or str(stats.get("last_built") or "")[:10] or "unknown"
    title = "Possible local collaborations — Commonweave circuit briefs"
    description = (
        f"{len(groups)} derived, unverified field notes connecting nearby organizations "
        "with complementary public roles."
    )
    countries = sorted({g["country"] for g in groups if g.get("country")})
    country_options = "\n".join(
        f'<option value="{html(country)}">{html(country)}</option>' for country in countries
    )
    cards = []
    for group in groups:
        role_lines = "\n".join(
            f"<li><strong>{html(member.get('role_label') or member.get('role') or 'Role')}:</strong> {html(member['name'])}</li>"
            for member in group["members"]
        )
        search_blob = " ".join([
            group.get("circuit_name") or "",
            group.get("location") or "",
            *[member.get("name") or "" for member in group["members"]],
            *[member.get("role_label") or member.get("role") or "" for member in group["members"]],
        ]).lower()
        cards.append(f"""<article class="brief-card" data-brief-card data-country="{html(group['country'])}" data-search="{html(search_blob)}">
  <div class="card-kicker"><span>{html(group['location'])}</span><span>Unverified</span></div>
  <h2>{html(group.get('circuit_name') or 'Possible local circuit')}</h2>
  <ul>{role_lines}</ul>
  <a href="{html(group['group_id'])}.html">Open field note &rarr;</a>
</article>""")
    return f"""{head_markup(title, description, f"{SITE_ORIGIN}/briefs/index.html")}
<body class="cw-page">
{nav_markup()}
<main id="main-content" class="brief-shell" tabindex="-1">
  <header class="brief-index-hero">
    <div class="eyebrow">Commonweave field notes &middot; Map snapshot {html(built)}</div>
    <h1>Possible collaborations, not claimed partnerships.</h1>
    <p class="lede">These {len(groups)} one-page briefs turn public directory data into specific questions: which nearby organizations might fill complementary roles, and what did the map get wrong?</p>
    <p class="section-intro">Every brief is derived and unverified. Nothing here says the listed organizations know one another, endorse Commonweave, or want an introduction. Each page carries its uncertainty and a correction path.</p>
  </header>

  <section aria-labelledby="brief-list-heading">
    <div class="filter-bar">
      <label>Search briefs
        <input id="brief-search" type="search" placeholder="Circuit, place, organization, or role">
      </label>
      <label>Country
        <select id="brief-country">
          <option value="">All countries</option>
          {country_options}
        </select>
      </label>
    </div>
    <div class="eyebrow" id="brief-list-heading"><span id="brief-visible-count">{len(groups)}</span> field notes shown</div>
    <div class="brief-grid" style="margin-top: var(--s-5);">
      {''.join(cards)}
    </div>
    <div id="brief-empty" class="empty-result">No briefs match those filters. Clear the search or choose another country.</div>
  </section>
</main>
{footer_markup()}

<script src="briefs.js"></script>
</body>
</html>
"""


def render_manifest(groups: list[dict], circuits: dict, stats: dict) -> str:
    payload = {
        "schema_version": 1,
        "generated_at": circuits.get("generated_at"),
        "source_script": "tools/build-circuit-briefs.py",
        "source_files": [
            "data/map/circuits.json",
            "briefs/source-records.json (compact fallback from data/map/orgs.v3.geojson)",
            "data/map/stats.v3.json",
        ],
        "stats_build_date": stats.get("last_built_date"),
        "brief_count": len(groups),
        "source_declared_candidate_count": circuits.get("total_candidates"),
        "source_count_matches": circuits.get("total_candidates") == len(groups),
        "briefs": [
            {
                "group_id": group["group_id"],
                "circuit": group.get("circuit"),
                "country": group.get("country"),
                "location": group.get("location"),
                "member_ids": [member["id"] for member in group["members"]],
            }
            for group in groups
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_sitemap(groups: list[dict], stats: dict) -> str:
    lastmod = "2026-09-06"  # Public page/navigation revision; source snapshot dates stay separate.
    urls = [
        (f"{SITE_ORIGIN}/", "1.0"),
        (f"{SITE_ORIGIN}/knowledge.html", "1.0"),
        (f"{SITE_ORIGIN}/directory.html", "0.7"),
        (f"{SITE_ORIGIN}/map.html", "0.9"),
        (f"{SITE_ORIGIN}/participate.html", "0.8"),
        (f"{SITE_ORIGIN}/briefs/index.html", "0.8"),
        (f"{SITE_ORIGIN}/doc.html?file=README", "0.8"),
        (f"{SITE_ORIGIN}/pipeline.html", "0.6"),
    ]
    urls.extend(
        (f"{SITE_ORIGIN}/briefs/{group['group_id']}.html", "0.6")
        for group in groups
    )
    entries = "\n".join(
        f"  <url><loc>{html(url)}</loc><lastmod>{html(lastmod)}</lastmod><priority>{priority}</priority></url>"
        for url, priority in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def expected_files(
    groups: list[dict],
    circuits: dict,
    stats: dict,
    features: dict[str, dict],
) -> dict[Path, str]:
    generated_at = str(circuits.get("generated_at") or stats.get("last_built") or "")
    files = {
        OUTPUT_DIR / "briefs.css": BRIEFS_CSS,
        OUTPUT_DIR / "briefs.js": BRIEFS_JS,
        OUTPUT_DIR / "index.html": render_index(groups, stats, generated_at),
        MANIFEST_PATH: render_manifest(groups, circuits, stats),
        SOURCE_RECORDS_PATH: render_source_records(features, circuits),
        SITEMAP_PATH: render_sitemap(groups, stats),
    }
    for group in groups:
        files[OUTPUT_DIR / f"{group['group_id']}.html"] = render_brief(
            group, stats, generated_at
        )
    return files


def check_files(files: dict[Path, str]) -> int:
    problems = []
    for path, expected in files.items():
        if not path.exists():
            problems.append(f"missing: {path.relative_to(ROOT)}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            problems.append(f"stale: {path.relative_to(ROOT)}")

    expected_brief_files = {
        path.name for path in files if path.parent == OUTPUT_DIR
    }
    if OUTPUT_DIR.exists():
        for path in OUTPUT_DIR.iterdir():
            if path.is_file() and path.name not in expected_brief_files:
                problems.append(f"unexpected: {path.relative_to(ROOT)}")

    if problems:
        print("Circuit briefs are not current:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"Circuit briefs are current ({len(files) - 6} briefs).")
    return 0


def write_files(files: dict[Path, str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    expected_brief_files = {
        path.name for path in files if path.parent == OUTPUT_DIR
    }
    if MANIFEST_PATH.exists():
        try:
            old_manifest = load_json(MANIFEST_PATH)
            old_slugs = {
                validate_slug(item.get("group_id"))
                for item in old_manifest.get("briefs", [])
                if item.get("group_id")
            }
        except (ValueError, json.JSONDecodeError):
            old_slugs = set()
        for slug in old_slugs:
            stale_path = OUTPUT_DIR / f"{slug}.html"
            if stale_path.name not in expected_brief_files and stale_path.exists():
                stale_path.unlink()

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when committed brief files do not match the current data export.",
    )
    args = parser.parse_args()

    circuits = load_json(CIRCUITS_PATH)
    stats = load_json(STATS_PATH)
    if ORGS_PATH.exists():
        features = feature_lookup(load_json(ORGS_PATH))
    else:
        features = source_record_lookup(load_json(SOURCE_RECORDS_PATH))
    groups = flatten_groups(circuits, features)
    declared = circuits.get("total_candidates")
    if declared is not None and int(declared) != len(groups):
        print(
            f"WARNING: circuits.json declares {declared} candidates but contains "
            f"{len(groups)}; generating only the observable groups.",
            file=sys.stderr,
        )
    files = expected_files(groups, circuits, stats, features)

    if args.check:
        return check_files(files)

    write_files(files)
    print(
        f"Wrote {len(groups)} circuit briefs to {OUTPUT_DIR.relative_to(ROOT)} "
        f"from map snapshot {stats.get('last_built_date') or 'unknown'}."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"build-circuit-briefs: {exc}", file=sys.stderr)
        sys.exit(1)
