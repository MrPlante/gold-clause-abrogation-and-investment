version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

drop _merge
merge 1:1 permno year using chars_annual.dta

drop if var_inv_rate == . 
*winsor2 ann*, replace trim by(year) cuts(0.5 99.5)

drop ph 
gen ph = . 
foreach v of varlist ann_* {
drop ph 
gen ph = `v' if year == min_year // 1930 or first year
bys permno: egen fix_`v' = mean(ph)
}
foreach v of varlist ann_* {
	gen `v'_before = fix_`v'*(year < 1933)
	gen `v'_1933 = fix_`v'*(year == 1933)
	gen `v'_1934 = fix_`v'*(year == 1934)
	gen `v'_after = fix_`v'*(year > 1934)
}

*Deciles 
foreach v of varlist fix_ann* {
astile `v'_port = `v', nq(10)	
}
foreach v of varlist fix_ann*port{
forvalues xx = 1(1)10{
gen	`v'_`xx'before = (`v'==`xx')*(year < 1933)
gen	`v'_`xx'1933 = (`v'==`xx')*(year == 1933)
gen	`v'_`xx'1934 = (`v'==`xx')*(year == 1934)
gen	`v'_`xx'after = (`v'==`xx')*(year > 1934)
}
}


*(1)
reghdfe var_inv_rate ///
    var_Q_before var_Q_1933 var_Q_1934 var_Q_after ///
    var_logasset_before var_logasset_1933 var_logasset_1934 var_logasset_after ///
    var_netinc_before var_netinc_1933 var_netinc_1934 var_netinc_after ///
    var_cash_before var_cash_1933 var_cash_1934 var_cash_after ///
    var_payout_before var_payout_1933 var_payout_1934 var_payout_after ///
    var_booklev_before var_booklev_1933 var_booklev_1934 var_booklev_after ///
    var_marketlev_before var_marketlev_1933 var_marketlev_1934 var_marketlev_after ///
    var_logltl_before var_logltl_1933 var_logltl_1934 var_logltl_after ///
	ann* ///
    var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m1

*(2)
reghdfe var_inv_rate fix_ann_ret_mean_port_1before-fix_ann_ret_mean_port_10after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m2

*(3)
reghdfe var_inv_rate fix_ann_ret_sd_port_1before-fix_ann_ret_sd_port_10after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m3

*(4)
reghdfe var_inv_rate fix_ann_beta_mktrf_port_1before-fix_ann_beta_mktrf_port_10after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m4

*(5)
reghdfe var_inv_rate fix_ann_beta_smb_port_1before-fix_ann_beta_smb_port_10after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m5

*(6)
reghdfe var_inv_rate fix_ann_beta_hml_port_1before-fix_ann_beta_hml_port_10after var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m6

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
local outfile "`OL'\Tables\tab_reghdfe_retcontrols.tex"

esttab m1 m2 m3 m4 m5 m6 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("(1)" "(2)" "(3)" "(4)" "(5)" "(6)", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nonumber

display as res "✅ Wrote -> `outfile'"
