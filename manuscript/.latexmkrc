# Compile with plain `latexmk main.tex` from this directory.
# Build artifacts (.aux, .bbl, .blg, .log, .fls, .fdb_latexmk) go to build/
# (gitignored); the compiled gold-clause.pdf lands here (versioned).
$pdf_mode = 1;
$aux_dir = 'build';
$out_dir = '.';
$emulate_aux = 1;
$jobname = 'gold-clause';
$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';
$bibtex_use = 2;
# Run bibtex from this directory (not build/) so relative ../ bib paths resolve.
$bibtex_fudge = 0;
# After every successful compile, refresh the self-contained HTML render
# of the PDF (gold-clause.html, versioned) for convenient browser review.
$success_cmd = 'python3 ../tools/pdf2html.py gold-clause.pdf gold-clause.html';
