# Commonweave site design and voice

Updated September 6, 2026.

The two primary destinations are **Knowledge base** and **Map**. Keep both
visible on every public page and at phone widths. The home wordmark returns
to the introduction. Directory, contribution and data notes belong in More.
Avoid competing names such as Docs, Sections, Explore and Directory for the
same destination. Secondary tools and generated briefs share the same header.

The knowledge base is a curated reading collection, with title/topic search,
ten areas of shared needs and a reading path: overview, critique, then a
practical test. Preserve the distinction between a proposal, evidence,
unresolved question and legacy research awaiting source review. The document
reader supplies a contents list, source link and a route back to the collection.

Use the paper, ink, moss and clay tokens in `assets/css/brand.css`.
Instrument Serif is for headings; Source Serif 4 is for reading and controls.
Use restrained rules, readable text, simple buttons and generous margins.
Map controls, details and plans use the same light surfaces as the reader.
Color can distinguish map categories, but should not be the only identifier.

Write in practical language. Say what someone can read, check or do next.
Use 'organization', 'record', 'source', 'role', 'proposed plan' and 'contribution'
consistently. Avoid manifesto claims, decorative metaphors, unexplained
technical labels and numbers presented without their snapshot or uncertainty.
Do not call a category match a partnership or a source classification a
service recommendation. Do not imply that all older research has been verified.

## Maintaining the shared pages

`tools/site_navigation.py` owns static header/footer markup and versions local
CSS/JS links by content. Navigation works without JavaScript. Keep the marked
header/footer blocks in all nine primary/support pages; edit the generator
instead of copying another navigation variant into a page. Generated briefs
reuse the same functions. Changing source styles/scripts requires regeneration
so repeat visitors receive the new assets after publication.

```text
python tools/site_navigation.py
python tools/build-circuit-briefs.py
python tools/site_navigation.py --check
python tools/build-circuit-briefs.py --check
node --test tests/*.test.js assets/js/map/*.test.cjs
python -m unittest discover -s tests -p 'test_*.py' -v
```

Browser review should include desktop, 390px and 520px widths, main navigation,
More, reading search/empty/reset, nested document links and outline anchors,
map place/list/goal selection and contribution draft generation. Check actual
text contrast after changing the map skin; legacy styles can refer to paper as
a text color. Place/list views must not run the Network force simulation.

## Publication

The repository's GitHub Pages configuration publishes `master` at `/` to
`commonweave.earth`. After the user's authorized release, merge only the tested
head and verify both the Pages build commit and the public pages/assets. Do
not infer successful deployment from a successful Git push alone.
