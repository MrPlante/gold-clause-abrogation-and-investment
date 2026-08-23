#!/usr/bin/env python3
"""Self-contained HTML render of a compiled PDF, for browser review.

Runs poppler's ``pdftohtml`` in complex single-document mode into a temp
directory, inlines every page/figure image as a base64 data URI, embeds
the PDF outline as a clickable table of contents at the top, and writes
ONE portable .html file next to the PDF.

Called automatically by each document's ``.latexmkrc`` (``$success_cmd``)
after every successful compilation, so ``<jobname>.html`` always matches
``<jobname>.pdf``. Can also be run by hand:

    python3 tools/pdf2html.py manuscript/gold-clause.pdf [output.html]

Uses only the standard library. Never exits non-zero: an HTML failure
must not fail the LaTeX build.
"""

import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ZOOM = "1.5"


def build(pdf: Path, out: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        subprocess.run(
            ["pdftohtml", "-s", "-c", "-zoom", ZOOM, "-q", str(pdf), str(tmp / "doc")],
            check=True,
        )
        html = (tmp / "doc-html.html").read_text(encoding="utf-8", errors="replace")

        def inline(match: re.Match) -> str:
            data = base64.b64encode((tmp / match.group(1)).read_bytes()).decode()
            return f'src="data:image/png;base64,{data}"'

        html = re.sub(r'src="(doc[0-9]+\.png)"', inline, html)
        # pdftohtml titles every page section with the temp-file path
        html = re.sub(r"<title>[^<]*</title>", f"<title>{out.stem}</title>", html)

        # Embed the PDF bookmarks as a table of contents; pdftohtml writes
        # them as links to per-page files (doc-N.html), which in single-
        # document mode correspond to the id="pageN-div" anchors.
        nav = ""
        outline = tmp / "doc-outline.html"
        if outline.exists():
            body = re.search(
                r"<body[^>]*>(.*)</body>",
                outline.read_text(encoding="utf-8", errors="replace"),
                re.S,
            )
            if body:
                toc = re.sub(r'href="doc-(\d+)\.html', r'href="#page\1-div', body.group(1))
                nav = (
                    '<div style="margin:1em auto; max-width:60em; '
                    'font-family:sans-serif; font-size:14px;">'
                    f"{toc}</div>\n"
                )
        html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + nav, html, count=1)

        out.write_text(html, encoding="utf-8")


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        raise SystemExit("usage: pdf2html.py <pdf> [output.html]")
    pdf = Path(argv[1]).resolve()
    out = Path(argv[2]).resolve() if len(argv) > 2 else pdf.with_suffix(".html")
    build(pdf, out)
    print(f"pdf2html: wrote {out}")


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception as exc:  # an HTML failure must never fail the build
        print(f"pdf2html: WARNING: html render failed: {exc}", file=sys.stderr)
    sys.exit(0)
