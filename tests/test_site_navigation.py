"""Public navigation must work consistently without browser JavaScript."""
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from site_navigation import PAGES, header_markup, footer_markup, render_page


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = []; self.ids = []
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag in ('a', 'link', 'script', 'img'):
            value = attrs.get('href') if tag in ('a', 'link') else attrs.get('src')
            if value:
                self.urls.append(value)


class NavigationTests(unittest.TestCase):
    def test_main_pages_share_current_navigation_without_placeholders(self):
        for name, current in PAGES.items():
            text = (ROOT / name).read_text(encoding='utf-8')
            prefix = '../' if '/' in name else ''
            self.assertEqual(text, render_page(text, current, prefix, footer=name != 'map.html'), name)
            self.assertIn(header_markup(prefix, current), text, name)
            self.assertNotIn('<header data-site-header></header>', text, name)
            self.assertEqual(text.count('aria-label="Main navigation"'), 1, name)

    def test_public_pages_have_existing_local_assets_destinations_and_unique_ids(self):
        for path in [*(ROOT / name for name in PAGES), *(ROOT / 'briefs').glob('*.html')]:
            parser = Links(); parser.feed(path.read_text(encoding='utf-8'))
            self.assertEqual(len(parser.ids), len(set(parser.ids)), str(path))
            for raw in parser.urls:
                url = urlsplit(raw)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (ROOT / unquote(url.path.lstrip('/'))) if url.path.startswith('/') else path.parent / unquote(url.path)
                self.assertTrue(target.exists(), f'{path.name}: missing {raw}')

    def test_nested_generated_briefs_use_same_primary_navigation_and_footer(self):
        pages = list((ROOT / 'briefs').glob('*.html'))
        self.assertGreaterEqual(len(pages), 14)
        for path in pages:
            text = path.read_text(encoding='utf-8')
            self.assertIn(header_markup('../', 'map'), text, path.name)
            self.assertIn(footer_markup('../'), text, path.name)
            self.assertIn('../assets/css/site-shell.css', text)


if __name__ == '__main__':
    unittest.main()
