set more off
display _newline(200)  
clear


*******************************************************
* AER-style reghdfe table (final clean version)
*******************************************************
version 16
set more off
clear all

* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5) 

* ---------- Run regressions ----------
eststo clear

drop d_year_1932_Low
drop year_1932_Low

reghdfe var_inv_rate ///
    var_Q d d_Low rating_ind d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)

reghdfe payout ///
    var_Q d d_Low rating_ind d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)

reghdfe cashrat ///
    var_Q d d_Low rating_ind d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)


reghdfe cashrat ///
    var_Q d d_Low y1933_Low-After_Low d_1933 d_1934 d_After ///
    d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)

/*
* (1) var_inv_rate
reghdfe var_inv_rate ///
    var_Q d d_1933 d_1934 d_After ///
    d_Before_Low d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m1

* (2) payout
reghdfe payout ///
    var_Q d d_1933 d_1934 d_After ///
    d_Before_Low d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m2

* (3) cashrat
reghdfe cashrat ///
    var_Q d d_1933 d_1934 d_After ///
    d_Before_Low d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m3
*/
* (1) var_inv_rate
reghdfe var_inv_rate ///
    var_Q d d_Low y1933_Low-After_Low d_1933 d_1934 d_After ///
    d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m1

* (2) payout
reghdfe payout ///
    var_Q d d_Low y1933_Low-After_Low d_1933 d_1934 d_After ///
    d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m2

* (3) cashrat
reghdfe cashrat ///
    var_Q d d_Low y1933_Low-After_Low d_1933 d_1934 d_After ///
    d_1933_Low d_1934_Low d_After_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m3
* ---------- Keep/order list and labels ----------
local keep_list  ///
    var_Q d d_Low y1933_Low y1934_Low After_Low d_1933 d_1934 d_After ///
     d_1933_Low d_1934_Low d_After_Low

local vlab ///
    var_Q        "Q" ///
    d            "\ensuremath{d}" ///
	d_Low        "\ensuremath{d} \ensuremath{\times \text{ Low rating}}" ///
	y1933_Low    "1933 \ensuremath{\times \text{ Low rating}}" ///
	y1934_Low    "1934 \ensuremath{\times \text{ Low rating}}" ///
	After_Low    "After \ensuremath{\times \text{ Low rating}}" ///
    d_1933       "1933 \ensuremath{\times d}" ///
    d_1934       "1934 \ensuremath{\times d}" ///
    d_After      "After \ensuremath{\times d}" ///
    d_1933_Low   "1933 \ensuremath{\times d \times \text{Low rating}}" ///
    d_1934_Low   "1934 \ensuremath{\times d \times \text{Low rating}}" ///
    d_After_Low  "After \ensuremath{\times d \times \text{Low rating}}"

* ---------- Export to Overleaf ----------
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_reghdfe_Q_d_low.tex"

esttab m1 m2 m3 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("Net investment" "Payout" "Dividend", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1})     noobs nomtitles nonumber


display as res "Wrote -> `outfile'"
