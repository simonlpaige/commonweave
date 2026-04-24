"""
Build pipeline.pdf from PIPELINE.md + pipeline-diagram.svg.

Approach:
1. Convert PIPELINE.md -> HTML with a clean print stylesheet.
2. Shell out to Chrome --headless --print-to-pdf to render.
3. Also save the diagram as PNG using Chrome --screenshot.

Run from commonweave/ (or anywhere; uses absolute paths).
"""
import os
import re
import subprocess
import sys

import markdown

ROOT = r"C:\Users\simon\.openclaw\workspace\commonweave"
MD_PATH = os.path.join(ROOT, "PIPELINE.md")
ASSETS = os.path.join(ROOT, "assets")
SVG_PATH = os.path.join(ASSETS, "pipeline-diagram.svg")
PNG_PATH = os.path.join(ASSETS, "pipeline-diagram.png")
HTML_TMP = os.path.join(ASSETS, "pipeline.html")
PDF_PATH = os.path.join(ROOT, "pipeline.pdf")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = r"""
@page {
  size: Letter;
  margin: 24mm 20mm 22mm 20mm;
  @bottom-right { content: "page " counter(page) " / " counter(pages); }
}
html, body {
  font-family: 'Inter', 'Segoe UI', Georgia, serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #2d2d2d;
  background: #ffffff;
}
body { max-width: 720px; margin: 0 auto; }
h1 {
  font-size: 26pt;
  font-weight: 800;
  color: #2d4026;
  letter-spacing: -0.3px;
  margin: 0 0 4pt 0;
  line-height: 1.15;
}
h1 + p em {
  color: #5e7a52;
  font-size: 12pt;
  font-style: italic;
}
h2 {
  font-size: 16pt;
  font-weight: 800;
  color: #2d4026;
  margin: 20pt 0 8pt 0;
  letter-spacing: -0.2px;
  border-bottom: 1px solid #d4c9a8;
  padding-bottom: 4pt;
}
h3 {
  font-size: 12pt;
  font-weight: 700;
  color: #3a5a32;
  margin: 14pt 0 4pt 0;
}
p {
  margin: 0 0 8pt 0;
}
ul, ol {
  margin: 2pt 0 10pt 0;
  padding-left: 22pt;
}
li {
  margin-bottom: 4pt;
}
code, tt {
  font-family: 'Menlo', 'Consolas', 'Courier New', monospace;
  font-size: 9.3pt;
  background: #f4efe2;
  padding: 1px 4px;
  border-radius: 3px;
  color: #3a5a32;
}
pre code { background: transparent; padding: 0; }
strong { color: #2d4026; }
em { color: #5e7a52; }
a { color: #3a5a32; text-decoration: none; border-bottom: 1px dotted #9cb58a; }
hr {
  border: none;
  border-top: 1px solid #d4c9a8;
  margin: 14pt 0;
}
img {
  display: block;
  max-width: 100%;
  margin: 10pt auto;
  page-break-inside: avoid;
}
figure, .figure {
  margin: 10pt 0;
  page-break-inside: avoid;
}
blockquote {
  border-left: 3px solid #9cb58a;
  padding-left: 12pt;
  color: #5e7a52;
  font-style: italic;
  margin: 10pt 0;
}
.pagebreak { page-break-before: always; }
.cover {
  text-align: center;
  padding-top: 90pt;
  page-break-after: always;
}
.cover h1 {
  font-size: 34pt;
  color: #2d4026;
  margin-bottom: 20pt;
  line-height: 1.15;
}
.cover .subtitle {
  font-size: 14pt;
  color: #5e7a52;
  font-style: italic;
  margin-bottom: 60pt;
  line-height: 1.5;
}
.cover .tagline {
  font-size: 11pt;
  color: #7a8a6a;
  margin-bottom: 24pt;
}
.cover .date {
  font-size: 10pt;
  color: #7a8a6a;
  font-family: 'Menlo', 'Consolas', monospace;
}
.cover-rule {
  width: 80pt;
  border-top: 2px solid #c4a55d;
  margin: 40pt auto;
}
/* avoid orphan stage headings */
h3 { page-break-after: avoid; }
h2 { page-break-after: avoid; }
"""

COVER = """
<div class="cover">
  <h1>How Commonweave<br>Finds and Grades<br>Organizations</h1>
  <div class="cover-rule"></div>
  <div class="subtitle">A field guide to how we find aligned organizations,<br>grade them, and keep the list honest.</div>
  <div class="tagline">25,837 organizations · 61 countries · one SQLite file</div>
  <div class="date">Version 1 &middot; 2026-04-24</div>
</div>
"""


def main():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md = f.read()

    # Strip the YAML frontmatter the template already covers
    md = re.sub(r"^---\n.*?\n---\n", "", md, count=1, flags=re.DOTALL)
    # Strip everything up through the first "---" horizontal rule. The
    # HTML cover page above already carries the title, tagline, and date.
    md = re.sub(r"^\s*#\s+How Commonweave.*?^---\s*$", "", md,
                count=1, flags=re.DOTALL | re.MULTILINE).lstrip()
    # Convert latex-style \newpage into an HTML page break div
    md = md.replace("\\newpage", '<div class="pagebreak"></div>')

    html_body = markdown.markdown(
        md,
        extensions=["extra", "sane_lists", "toc"],
    )

    # Inline the SVG so the PDF renderer doesn't need network or fetch
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        svg = f.read()
    # Remove the XML declaration so it embeds cleanly inside HTML
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    html_body = html_body.replace(
        '<img alt="The Commonweave pipeline, source to published directory." '
        'src="assets/pipeline-diagram.svg" />',
        f'<figure class="figure">{svg}</figure>',
    )
    # Fallback in case markdown order differs
    html_body = re.sub(
        r'<img[^>]*pipeline-diagram\.svg[^>]*/>',
        f'<figure class="figure">{svg}</figure>',
        html_body,
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>How Commonweave Finds and Grades Organizations</title>
  <style>{CSS}</style>
</head>
<body>
{COVER}
{html_body}
</body>
</html>
"""
    with open(HTML_TMP, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {HTML_TMP}")

    # Render PDF via Chrome headless
    file_url = "file:///" + HTML_TMP.replace("\\", "/")
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={PDF_PATH}",
        file_url,
    ]
    print("rendering PDF...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print("Chrome stderr:", r.stderr[-1000:])
    if not os.path.exists(PDF_PATH):
        print("ERROR: PDF not produced")
        sys.exit(1)
    print(f"wrote {PDF_PATH}  ({os.path.getsize(PDF_PATH):,} bytes)")

    # Render diagram as PNG via Chrome screenshot
    svg_html = os.path.join(ASSETS, "pipeline-diagram-wrap.html")
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        svg_only = f.read()
    svg_only = re.sub(r"<\?xml[^>]*\?>", "", svg_only).strip()
    with open(svg_html, "w", encoding="utf-8") as f:
        f.write(
            "<!DOCTYPE html><html><head><style>"
            "html,body{margin:0;padding:0;background:#eee7d6}"
            "svg{display:block}"
            "</style></head><body>"
            f"{svg_only}</body></html>"
        )
    png_url = "file:///" + svg_html.replace("\\", "/")
    png_cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1200,1700",
        "--hide-scrollbars",
        f"--screenshot={PNG_PATH}",
        png_url,
    ]
    print("rendering PNG...")
    r = subprocess.run(png_cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("Chrome stderr:", r.stderr[-1000:])
    if os.path.exists(PNG_PATH):
        print(f"wrote {PNG_PATH}  ({os.path.getsize(PNG_PATH):,} bytes)")
    try:
        os.remove(svg_html)
    except OSError:
        pass


if __name__ == "__main__":
    main()
