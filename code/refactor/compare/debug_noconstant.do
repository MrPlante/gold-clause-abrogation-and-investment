clear all
set more off
global REPO "/project/splante/git/gold-clause-abrogation-and-investment"
use "${REPO}/data/A4_merged.dta", clear
winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)

reghdfe cashrat var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year) noconstant
di "with noconstant: k=" colsof(e(b)) " se1933=" _se[d_year_1933]

reghdfe cashrat var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
di "default: k=" colsof(e(b)) " se1933=" _se[d_year_1933]
