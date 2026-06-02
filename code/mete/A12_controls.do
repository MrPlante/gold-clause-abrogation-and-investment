set more off
display _newline(200)  
clear

/*
*******************************************************
* AER-style reghdfe table (final clean version)
*******************************************************
version 16
set more off
clear all

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

*var_psltl_before var_psltl_1933 var_psltl_1934  var_psltl_after /// including this kills the result in (2). d and psltl corr is -0.96 among d > 0 firms and -0.44 among all firms. 
*var_bdltl_before var_bdltl_1933 var_bdltl_1934  var_bdltl_after ///

*using ind FE in decile results weakens things quite a bit


*(1)
reghdfe var_inv_rate var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(2)
reghdfe var_inv_rate ///
var_Q_before var_Q_1933 var_Q_1934 var_Q_after ///
var_logasset_before var_logasset_1933 var_logasset_1934  var_logasset_after ///
var_netinc_before var_netinc_1933 var_netinc_1934 var_netinc_after ///
var_cash_before var_cash_1933 var_cash_1934 var_cash_after ///
var_payout_before var_payout_1933 var_payout_1934 var_payout_after ///
var_booklev_before var_booklev_1933 var_booklev_1934 var_booklev_after ///
var_marketlev_before var_marketlev_1933 var_marketlev_1934 var_marketlev_after ///
var_logltl_before var_logltl_1933 var_logltl_1934  var_logltl_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)

*(3)
reghdfe var_inv_rate ///
fix_var_Q_port_1_before-fix_var_Q_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(4)
reghdfe var_inv_rate ///
fix_var_logasset_port_1_before-fix_var_logasset_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(5)
reghdfe var_inv_rate ///
fix_var_netinc_port_1_before-fix_var_netinc_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(6)
reghdfe var_inv_rate ///
fix_var_cash_port_1_before-fix_var_cash_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(7)
reghdfe var_inv_rate ///
fix_var_payout_port_1_before-fix_var_payout_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(8)
reghdfe var_inv_rate ///
fix_var_booklev_port_1_before-fix_var_booklev_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(9)
reghdfe var_inv_rate ///
fix_var_marketlev_port_1_before-fix_var_marketlev_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*(10)
reghdfe var_inv_rate ///
fix_var_logltl_port_1_before-fix_var_logltl_port_10_after ///
var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
*/

*******************************************************
* 10 regressions -> AER-style table (Q, d, 1933xd, 1934xd, Afterxd)
*******************************************************
version 16
set more off
clear all

cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

eststo clear

*------------------------------------------------------
* (1) Baseline
*------------------------------------------------------
reghdfe var_inv_rate var_Q d d_1933 d_1934 d_After, absorb(permno sic2_year) vce(cluster permno year)
eststo m1

*------------------------------------------------------
* (2) Full baseline controls (var_* before/after)
*------------------------------------------------------
reghdfe var_inv_rate ///
    var_Q_before var_Q_1933 var_Q_1934 var_Q_after ///
    var_logasset_before var_logasset_1933 var_logasset_1934 var_logasset_after ///
    var_netinc_before var_netinc_1933 var_netinc_1934 var_netinc_after ///
    var_cash_before var_cash_1933 var_cash_1934 var_cash_after ///
    var_payout_before var_payout_1933 var_payout_1934 var_payout_after ///
    var_booklev_before var_booklev_1933 var_booklev_1934 var_booklev_after ///
    var_marketlev_before var_marketlev_1933 var_marketlev_1934 var_marketlev_after ///
    var_logltl_before var_logltl_1933 var_logltl_1934 var_logltl_after ///
    var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m2

*------------------------------------------------------
* (3)-(10) One-by-one fixed portfolios
*------------------------------------------------------
reghdfe var_inv_rate fix_var_Q_port_1_before-fix_var_Q_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m3

reghdfe var_inv_rate fix_var_logasset_port_1_before-fix_var_logasset_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m4

reghdfe var_inv_rate fix_var_netinc_port_1_before-fix_var_netinc_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m5

reghdfe var_inv_rate fix_var_cash_port_1_before-fix_var_cash_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m6

reghdfe var_inv_rate fix_var_payout_port_1_before-fix_var_payout_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m7

reghdfe var_inv_rate fix_var_booklev_port_1_before-fix_var_booklev_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m8

reghdfe var_inv_rate fix_var_marketlev_port_1_before-fix_var_marketlev_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m9

reghdfe var_inv_rate fix_var_logltl_port_1_before-fix_var_logltl_port_10_after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m10


*------------------------------------------------------
* Keep/order list and labels
*------------------------------------------------------
local keep_list var_Q d d_1933 d_1934 d_After

local vlab ///
    var_Q    "Q" ///
    d        "\ensuremath{d}" ///
    d_1933   "1933 \ensuremath{\times d}" ///
    d_1934   "1934 \ensuremath{\times d}" ///
    d_After  "After \ensuremath{\times d}"


*------------------------------------------------------
* Export LaTeX table
*------------------------------------------------------
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_reghdfe_controls.tex"

esttab m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("(1)" "(2)" "(3)" "(4)" "(5)" "(6)" "(7)" "(8)" "(9)" "(10)", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nonumber

display as res "✅ Wrote -> `outfile'"

