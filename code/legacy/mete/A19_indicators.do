version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear


sum d if d > 0,d
gen dind2 = (d >= `r(p50)')
sum d if d > 0,d
gen dind3 = (d >= `r(p75)')

drop d_Before-d_After
*gen d_Before = dind*(year<=1932)
gen d_1933   = dind*(year==1933)
gen d_1934   = dind*(year==1934)
gen d_After  = dind*(year>=1935)

*gen d2_Before = dind2*(year<=1932)
gen d2_1933   = dind2*(year==1933)
gen d2_1934   = dind2*(year==1934)
gen d2_After  = dind2*(year>=1935)

*gen d3_Before = dind3*(year<=1932)
gen d3_1933   = dind3*(year==1933)
gen d3_1934   = dind3*(year==1934)
gen d3_After  = dind3*(year>=1935)


*(1)
reghdfe var_inv_rate var_Q dind d_1933-d_After, absorb(permno year) vce(cluster permno year)
eststo m1

*(2)
reghdfe var_inv_rate var_Q dind dind2 d_1933-d2_After, absorb(permno year) vce(cluster permno year)
eststo m2

*(3)
reghdfe var_inv_rate var_Q dind dind2 dind3 d_1933-d3_After, absorb(permno year) vce(cluster permno year)
eststo m3

local keep_list var_Q dind dind2 dind3 d_1933 d_1934 d_After ///
d2_1933 d2_1934 d2_After d3_1933 d3_1934 d3_After

local vlab ///
    var_Q    "Q" ///
    dind     "\ensuremath{(d > 0)}" ///
    dind2    "\ensuremath{(d > d_{0.5})}" ///
    dind3    "\ensuremath{(d > d_{0.75})}" ///
    d_1933   "1933 \ensuremath{\times (d > 0)}" ///
    d_1934   "1934 \ensuremath{\times (d > 0)}" ///
    d_After  "After \ensuremath{\times (d > 0)}" ///
    d2_1933  "1933 \ensuremath{\times (d > d_{0.5})}" ///
    d2_1934  "1934 \ensuremath{\times (d > d_{0.5})}" ///
    d2_After "After \ensuremath{\times (d > d_{0.5})}" ///
    d3_1933  "1933 \ensuremath{\times (d > d_{0.75})}" ///
    d3_1934  "1934 \ensuremath{\times (d > d_{0.75})}" ///
    d3_After "After \ensuremath{\times (d > d_{0.75})}"
	
*------------------------------------------------------
* Export LaTeX table
*------------------------------------------------------
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_dind.tex"

esttab m1 m2 m3 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("(1)" "(2)" "(3)", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nonumber

display as res "✅ Wrote -> `outfile'"

















