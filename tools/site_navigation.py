"""Build the same static navigation on every public page; no browser JS needed."""
import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    'index.html': '', 'knowledge.html': 'knowledge', 'doc.html': 'knowledge',
    'find-community-organizations.html': '',
    'map.html': 'map', 'directory.html': 'directory', 'participate.html': 'participate',
    'pipeline.html': 'pipeline', 'audit/index.html': 'participate', 'audit/enrich.html': 'participate',
}


# The mark is a plain weave: two threads over, two under.
MARK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 8H13M19 8H22M2 16H5M11 16H22M8 2V5M8 11V22M16 2V13M16 19V22"/></svg>'
# Every destination is visible in the header; nothing is tucked into a menu.
LINKS = [
    ('map.html', 'Map', 'map'),
    ('directory.html', 'Directory', 'directory'),
    ('knowledge.html', 'Framework', 'knowledge'),
    ('pipeline.html', 'Data', 'pipeline'),
    ('participate.html', 'Contribute', 'participate'),
]


def header_markup(prefix='', current=''):
    def link(path, label, key):
        active = ' aria-current="page"' if current == key else ''
        return f'<li><a href="{prefix}{path}"{active}>{label}</a></li>'
    links = ''.join(link(*item) for item in LINKS)
    return f'''<!-- cw:header:start -->
<header data-site-header class="cw-header">
  <nav class="cw-nav" aria-label="Main navigation">
    <a class="cw-brand" href="{prefix}index.html">{MARK}<span>Commonweave</span></a>
    <ul class="cw-links">{links}</ul>
  </nav>
</header>
<!-- cw:header:end -->'''


# Shown on the main site pages, which load Cloudflare Web Analytics. Brief
# pages (prefix '../') load no analytics and say nothing about it.
ANALYTICS_NOTE = '\n      <p class="cw-footer-note">Visits are counted in aggregate with Cloudflare Web Analytics. No cookies, no accounts, no ad tracking.</p>'


def footer_markup(prefix=''):
    note = '' if prefix else ANALYTICS_NOTE
    return f'''<!-- cw:footer:start -->
<footer data-site-footer class="cw-footer">
  <div class="cw-footer-inner">
    <div>
      <p>Commonweave is an open directory of community organizations, with working notes on how their efforts might fit together. Records are leads to check, not endorsements.</p>{note}
    </div>
    <ul>
      <li><a href="{prefix}map.html">Map</a></li>
      <li><a href="{prefix}directory.html">Directory</a></li>
      <li><a href="{prefix}knowledge.html">Framework</a></li>
      <li><a href="{prefix}doc.html?file=CRITIQUE">Critique</a></li>
      <li><a href="{prefix}pipeline.html">About the data</a></li>
      <li><a href="{prefix}participate.html">Contribute or correct</a></li>
      <li><a href="https://github.com/simonlpaige/commonweave">GitHub</a></li>
      <li><a href="https://github.com/simonlpaige/commonweave/blob/master/LICENSE">Licence and reuse</a></li>
    </ul>
  </div>
</footer>
<!-- cw:footer:end -->'''


def render_page(text, current, prefix='', footer=True):
    replacements = [('header', header_markup(prefix, current))]
    if footer:
        replacements.append(('footer', footer_markup(prefix)))
    for kind, markup in replacements:
        pattern = rf'<!-- cw:{kind}:start -->[\s\S]*?<!-- cw:{kind}:end -->|<{kind} data-site-{kind}></{kind}>'
        text, count = re.subn(pattern, lambda _: markup, text)
        if count != 1:
            raise ValueError(f'Expected exactly one shared {kind} placeholder/block, found {count}')
    return text


def version_assets(text, folder, overrides=None):
    """Content versions prevent old browser/CDN CSS or JS surviving a release."""
    def replace(match):
        value = urlsplit(match[2])
        if value.scheme or value.netloc or not value.path.endswith(('.css', '.js')):
            return match[0]
        path = (ROOT / value.path.lstrip('/')) if value.path.startswith('/') else folder / value.path
        content = (overrides or {}).get(path.resolve())
        if content is None and not path.is_file():
            raise ValueError(f'Missing public asset: {path}')
        digest = hashlib.sha256((content if content is not None else path.read_bytes()).replace(b'\r\n', b'\n')).hexdigest()[:12]
        return match[1] + value.path + '?v=' + digest + match[3]
    return re.sub(r'(<(?:script|link)\b[^>]*?\b(?:src|href)=")([^"]+)(")', replace, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for filename, current in PAGES.items():
        path = ROOT / filename
        before = path.read_text(encoding='utf-8')
        after = version_assets(render_page(before, current, '../' if '/' in filename else '', footer=filename != 'map.html'), path.parent)
        if before != after:
            stale.append(filename)
            if not args.check:
                path.write_text(after, encoding='utf-8')
    if args.check and stale:
        parser.exit(1, 'Stale navigation: ' + ', '.join(stale) + '\n')
    print(f'Shared navigation {"checked" if args.check else "built"} for {len(PAGES)} pages.')


if __name__ == '__main__':
    main()
