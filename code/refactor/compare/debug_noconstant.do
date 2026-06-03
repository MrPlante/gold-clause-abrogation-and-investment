*   bash code/refactor/scripts/run_stata_do.sh code/refactor/compare/debug_noconstant.do
version 16
clear all
set more off
args repo
if "`repo'" == "" {
    display as error "Run via code/refactor/scripts/run_stata_do.sh"
    exit 198
}
global REPO "`repo'"
use "${REPO}/data/A4_merged.dta", clear
winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)

reghdfe cashrat var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year) noconstant
di "with noconstant: k=" colsof(e(b)) " se1933=" _se[d_year_1933]

reghdfe cashrat var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)
di "default: k=" colsof(e(b)) " se1933=" _se[d_year_1933]
