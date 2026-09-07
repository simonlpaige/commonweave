# Document reader dependencies

Pinned local browser files avoid runtime CDN dependencies for the reader.

- Marked 9.1.6: https://github.com/markedjs/marked/tree/v9.1.6 ; MIT, see MARKED-LICENSE.md.
- DOMPurify 3.4.14: https://github.com/cure53/DOMPurify/tree/3.4.14 ; Apache-2.0 or MPL-2.0, see DOMPURIFY-LICENSE.txt.

Marked parses Markdown; it does not sanitize HTML. The reader passes parsed
HTML through DOMPurify, then rewrites document links and constrains media URLs.
Update deliberately and rerun reader safety and browser checks together.
