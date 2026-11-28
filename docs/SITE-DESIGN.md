# Commonweave site design and voice

Updated November 28, 2026. This replaces the September paper-and-serif design.

## What the site is for

The site is a reference tool. Someone arrives with something they want to do
and a place, and leaves with a list of organizations to check and a clear view
of which roles have no record. The framework is supporting reading. Design
decisions follow from that: say what a visitor can do, put the action first,
and state the limits of the data where the data is shown.

## Navigation

Five destinations, all visible in the header at every width: **Map**,
**Directory**, **Framework**, **Data**, **Contribute**. Nothing is tucked into
a menu. On phones the links sit in a second row under the name. Use one name
per destination; the framework page is "Framework", not "Knowledge base" or
"Docs".

The home page leads with the goals from `assets/js/map/pathways.js`, grouped
by how well each combination is documented. Each goal links to the map's List
view for that goal (`map.html#goal=<id>&view=list`). A test in
`tests/knowledge.test.js` fails if the home page and the goal data disagree.

## Look

`assets/css/site.css` holds the tokens and every content-page style.
`assets/css/map.css` adds the map. `assets/css/review-tools.css` adapts the
audit tools. Briefs get `briefs/briefs.css`, written by
`tools/build-circuit-briefs.py`.

- **Ground and ink.** White ground, near-black text, grey rules. Sections are
  separated by a single ink rule, with the heading in a left column on wide
  screens (`.band`).
- **Blue means you can act on it.** Links, buttons, focus rings, the current
  page. Do not use blue for decoration.
- **Yellow means unverified.** The `.note` block, the `mark` highlight and the
  dashed `.status-open` label carry caveats about the data: approximate pins,
  unreviewed records, untested combinations, missing roles. Keep caveats in
  these, next to the data they qualify.
- **Type.** Archivo, self-hosted from `assets/fonts/` (SIL Open Font License;
  no request leaves the site). Headings use the narrower width at weight 700.
  No uppercase letter-spaced labels and no italic display type.
- **Shapes.** 4px corners, 1px borders, no shadows on content, no gradients.
  Lists and ruled rows are preferred to cards.
- **Dark mode** follows the visitor's system setting through the tokens. The
  map canvas stays light because the basemap and point colours are fixed.
- Color can distinguish map categories, but must not be the only identifier:
  category names are always written in ink beside the dot.

## Voice

Write in practical language. Say what someone can read, check or do next.
Use 'organization', 'record', 'source', 'role', 'proposed plan' and
'contribution' consistently. Avoid manifesto claims, decorative metaphors,
unexplained technical labels and numbers presented without their snapshot or
uncertainty. Do not call a category match a partnership or a source
classification a service recommendation. Do not imply that all older research
has been verified.

## Maintaining the shared pages

`tools/site_navigation.py` owns the static header and footer markup and
versions local CSS/JS links by content. Navigation works without JavaScript.
Keep the marked header/footer blocks in every page it lists; edit the
generator instead of copying markup into a page. Generated briefs reuse the
same functions. Changing a stylesheet or script requires regeneration so
repeat visitors receive the new assets.

```text
python tools/site_navigation.py
python tools/build-circuit-briefs.py
python tools/site_navigation.py --check
python tools/build-circuit-briefs.py --check
node --test tests/*.test.js assets/js/map/*.test.cjs
python -m unittest discover -s tests -p 'test_*.py' -v
node tools/build_share_image.js        # only if the preview card changes
```

The map script is inline in `map.html` and has no unit tests of its own.
After changing it, load the page and go through: Map, List, Coverage and
Network; a goal with a country; opening a record; the phone-width sheet.
Check 390px, 520px and desktop, in light and dark. Map and List must not run
the Network force simulation.

## Publication

The repository's GitHub Pages configuration publishes `master` at `/` to
`commonweave.earth`. After the user's authorized release, merge only the tested
head and verify both the Pages build commit and the public pages/assets. Do
not infer successful deployment from a successful Git push alone.
