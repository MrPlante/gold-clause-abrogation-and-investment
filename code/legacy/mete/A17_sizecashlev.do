version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

sum var_logasset if year == min_year & d > 0,d
gen small2 = (var_logasset < `r(p50)') 
bys permno: egen small = mean(small2)

sum var_cash if year == min_year & d > 0,d
gen lowcash2 = (var_cash < `r(p50)') 
bys permno: egen lowcash = mean(lowcash2)

sum var_booklev if year == min_year & d > 0,d
gen highlev2 = (var_booklev > `r(p50)') 
bys permno: egen highlev = mean(highlev2)

preserve
*Interaction terms 
gen d_Before_x = d*(year<=1932)*small
gen d_1933_x   = d*(year==1933)*small
gen d_1934_x   = d*(year==1934)*small
gen d_After_x  = d*(year>=1935)*small

gen d_x  = d*small

gen Before_x = (year<=1932)*small
gen y1933_x   = (year==1933)*small
gen y1934_x   = (year==1934)*small
gen After_x  = (year>=1935)*small

* (2) var_inv_rate
reghdfe var_inv_rate ///
    var_Q d d_x y1933_x-After_x d_1933 d_1934 d_After ///
    d_1933_x d_1934_x d_After_x, ///
    absorb(permno year) vce(cluster permno year)
eststo m1
restore

preserve
*Interaction terms 
gen d_Before_x = d*(year<=1932)*lowcash
gen d_1933_x   = d*(year==1933)*lowcash
gen d_1934_x   = d*(year==1934)*lowcash
gen d_After_x  = d*(year>=1935)*lowcash

gen d_x  = d*lowcash

gen Before_x = (year<=1932)*lowcash
gen y1933_x   = (year==1933)*lowcash
gen y1934_x   = (year==1934)*lowcash
gen After_x  = (year>=1935)*lowcash

* (2) var_inv_rate
reghdfe var_inv_rate ///
    var_Q d d_x y1933_x-After_x d_1933 d_1934 d_After ///
    d_1933_x d_1934_x d_After_x, ///
    absorb(permno year) vce(cluster permno year)
eststo m2
restore

preserve
*Interaction terms 
gen d_Before_x = d*(year<=1932)*highlev
gen d_1933_x   = d*(year==1933)*highlev
gen d_1934_x   = d*(year==1934)*highlev
gen d_After_x  = d*(year>=1935)*highlev

gen d_x  = d*highlev

gen Before_x = (year<=1932)*highlev
gen y1933_x   = (year==1933)*highlev
gen y1934_x   = (year==1934)*highlev
gen After_x  = (year>=1935)*highlev

* (3) var_inv_rate
reghdfe var_inv_rate ///
    var_Q d d_x y1933_x-After_x d_1933 d_1934 d_After ///
    d_1933_x d_1934_x d_After_x, ///
    absorb(permno year) vce(cluster permno year)
eststo m3
restore

* ---------- Keep/order list and labels ----------
local keep_list  ///
    var_Q d d_x y1933_x y1934_x After_x d_1933 d_1934 d_After ///
     d_1933_x d_1934_x d_After_x

local vlab ///
    var_Q        "Q" ///
    d            "\ensuremath{d}" ///
	d_x        "\ensuremath{d} \ensuremath{\times \text{ I}}" ///
	y1933_x    "1933 \ensuremath{\times \text{ I}}" ///
	y1934_x    "1934 \ensuremath{\times \text{ I}}" ///
	After_x    "After \ensuremath{\times \text{ I}}" ///
    d_1933       "1933 \ensuremath{\times d}" ///
    d_1934       "1934 \ensuremath{\times d}" ///
    d_After      "After \ensuremath{\times d}" ///
    d_1933_x   "1933 \ensuremath{\times d \times \text{I}}" ///
    d_1934_x   "1934 \ensuremath{\times d \times \text{I}}" ///
    d_After_x  "After \ensuremath{\times d \times \text{I}}"

* ---------- Export to Overleaf ----------
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_sizecashlev.tex"

esttab m1 m2 m3 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("Small" "Low cash" "High leverage", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1})     noobs nomtitles nonumber


display as res "Wrote -> `outfile'"

















