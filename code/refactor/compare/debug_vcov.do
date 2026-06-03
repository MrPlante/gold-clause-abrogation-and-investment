* Debug: export vcov diagonal for cashrat table4 model
clear all
set more off
global REPO "/project/splante/git/gold-clause-abrogation-and-investment"
use "${REPO}/data/A4_merged.dta", clear
winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)

local dep cashrat
reghdfe `dep' var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)

matrix V = e(V)
* Export full vcov for Python comparison
preserve
clear
svmat V, names(v)
gen row = _n
save "${REPO}/code/refactor/compare/output/debug_stata_V.dta", replace
restore

* Export coef names and se
tempname posth
postfile `posth' str32 term double se diag using "${REPO}/code/refactor/compare/output/debug_stata_vcov.dta", replace
local names : colnames e(b)
local k : colsof(e(b))
forvalues i = 1/`k' {
    local nm : word `i' of `names'
    scalar s = sqrt(V[`i',`i'])
    post `posth' ("`nm'") (s) (V[`i',`i'])
}
postclose `posth'

display "N=" e(N) " df_r=" e(df_r) " df_m=" e(df_m) " df_a=" e(df_a)
capture noisily display "N_clust=" e(N_clust)
capture noisily display "unclustered_df_r=" e(unclustered_df_r)
