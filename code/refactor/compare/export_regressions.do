* Export regression coefficients for Python vs Stata comparison.
* Run from repository root:
*   /usr/local/stata/stata-mp -b do code/refactor/compare/export_regressions.do
version 16
set more off
set linesize 255

local REPO "`c(pwd)'"
local DATA "`REPO'/data"
local OUT  "`REPO'/code/refactor/compare/output"
cap mkdir "`OUT'"

cap which require
if _rc {
    display as text "Installing require from SSC..."
    ssc install require, replace
}
cap which ftools
if _rc {
    display as text "Installing ftools from SSC..."
    ssc install ftools, replace
}
cap which reghdfe
if _rc {
    display as text "Installing reghdfe from SSC..."
    ssc install reghdfe, replace
}
cap which winsor2
if _rc {
    display as text "Installing winsor2 from SSC..."
    ssc install winsor2, replace
}
cap ftools, compile

tempname posth
postfile `posth' ///
    str32 table str32 model str64 term ///
    double coef double se double pval long N double r2 ///
    using "`OUT'/stata_regressions.dta", replace

program define _post_reghdfe
    args posth table model
    local cols : colnames e(b)
    foreach v of local cols {
        if inlist("`v'", "_cons", "Intercept") {
            continue
        }
        scalar __b = _b[`v']
        scalar __se = _se[`v']
        if __se < . {
            scalar __p = 2 * ttail(e(df_r), abs(__b / __se))
        }
        else {
            scalar __p = .
        }
        scalar __r2 = e(r2)
        if missing(__r2) {
            scalar __r2 = e(r2_within)
        }
        capture post `posth' ("`table'") ("`model'") ("`v'") ///
            (__b) (__se) (__p) (e(N)) (__r2)
    }
end

*---------------------------------------------------------------------------
* Table 3 — A9_inv_results.do (models present in Stata export)
*---------------------------------------------------------------------------
use "`DATA'/A4_merged.dta", clear

reghdfe var_inv_rate var_Q, absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 classic

reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 overhang

reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 ///
    if ind_3134 != 1, absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 no_maturity

drop d d_year_*
gen d = dalt
forvalues yy = 1926/1940 {
    gen d_year_`yy' = dalt_year_`yy'
}
drop d_year_1932
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 dalt

drop d d_year_*
gen d = ps
forvalues yy = 1926/1940 {
    gen d_year_`yy' = ps_year_`yy'
}
drop d_year_1932
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 pref_shares

drop d d_year_*
gen d = bd
forvalues yy = 1926/1940 {
    gen d_year_`yy' = bd_year_`yy'
}
drop d_year_1932
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table3 bank_debt

*---------------------------------------------------------------------------
* Table 4 — A10_otheroutcomes.do
*---------------------------------------------------------------------------
use "`DATA'/A4_merged.dta", clear
winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)

reghdfe payout var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 payout

reghdfe cashrat var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 cashrat

reghdfe netrep var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 netrep

drop denom*
gen denom2 = netppe_bs if year <= min_year
bys permno: egen denom3 = mean(denom2)
gen denom = denom3
gen cashppe = cash_bs / denom
gen nippe = ni_is / denom
winsor2 cashppe nippe, replace by(year) cuts(0.5 99.5)

reghdfe nippe var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 nippe

reghdfe cashppe var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 cashppe

reghdfe var_booklev var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table4 leverage

*---------------------------------------------------------------------------
* Table 5 — A21_ratings_yearbyyear.do
*---------------------------------------------------------------------------
use "`DATA'/A4_merged.dta", clear
winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)

quietly summarize d if d > 0, meanonly
replace d = d - r(mean)
replace d_Low = d * rating_ind
forvalues xx = 1926/1940 {
    replace d_year_`xx' = d * year_`xx'
    replace d_year_`xx'_Low = d * year_`xx' * rating_ind
}
drop d_year_1932_Low year_1932_Low

reghdfe var_inv_rate var_Q d d_Low ///
    d_year_1926-d_year_1940 year_1926_Low-year_1940_Low ///
    d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table5 var_inv_rate

reghdfe cashrat var_Q d d_Low ///
    d_year_1926-d_year_1940 year_1926_Low-year_1940_Low ///
    d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)
_post_reghdfe `posth' table5 cashrat

postclose `posth'

use "`OUT'/stata_regressions.dta", clear
export delimited "`OUT'/stata_regressions.csv", replace
display as res "Wrote `OUT'/stata_regressions.csv (" _N " rows)"
