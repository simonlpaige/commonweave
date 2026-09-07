"""Build the same static navigation on every public page; no browser JS needed."""
import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    'index.html': '', 'knowledge.html': 'knowledge', 'doc.html': 'knowledge',
    'map.html': 'map', 'directory.html': 'directory', 'participate.html': 'participate',
    'pipeline.html': 'pipeline', 'audit/index.html': 'participate', 'audit/enrich.html': 'participate',
}


def header_markup(prefix='', current=''):
    def link(path, label, key):
        active = ' aria-current="page"' if current == key else ''
        return f'<a href="{prefix}{path}"{active}>{label}</a>'
    return f'''<!-- cw:header:start -->
<header data-site-header>
  <nav class="cw-nav" aria-label="Main navigation">
    <a class="cw-brand" href="{prefix}index.html" aria-label="Commonweave home"><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="21"/><path d="M12 12C20 24 28 24 36 36M36 12C28 24 20 24 12 36"/><circle class="cw-seed" cx="24" cy="24" r="2"/></svg><span>commonweave</span></a>
    <div class="cw-primary">{link('knowledge.html', 'Knowledge base', 'knowledge')}{link('map.html', 'Map', 'map')}</div>
    <details class="cw-more"><summary>More</summary><div class="cw-more-links">
      {link('directory.html', 'Organization directory', 'directory')}
      {link('participate.html', 'Contribute or correct', 'participate')}
      {link('pipeline.html', 'About the data', 'pipeline')}
      <a href="https://github.com/simonlpaige/commonweave">Project on GitHub</a>
    </div></details>
  </nav>
</header>
<!-- cw:header:end -->'''


def footer_markup(prefix=''):
    return f'''<!-- cw:footer:start -->
<footer data-site-footer class="cw-footer">
  <p>A shared framework. Evidence to inspect. Work to improve together.</p>
  <div><a href="{prefix}knowledge.html">Knowledge base</a><a href="{prefix}map.html">Map</a><a href="{prefix}participate.html">Contribute or correct</a><a href="https://github.com/simonlpaige/commonweave/blob/master/LICENSE">Licensing and reuse</a></div>
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
