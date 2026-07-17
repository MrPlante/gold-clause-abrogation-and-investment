# Compile with plain `latexmk Manuscript.tex` from this directory.
# Build artifacts (.aux, .bbl, .blg, .log, .fls, .fdb_latexmk) go to build/
# (gitignored); the compiled Manuscript.pdf lands here (versioned).
$pdf_mode = 1;
$aux_dir = 'build';
$out_dir = '.';
$emulate_aux = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';
$bibtex_use = 2;
