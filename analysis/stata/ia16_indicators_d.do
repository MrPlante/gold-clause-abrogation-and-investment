* IA.16 (extensive-margin exposure indicators): reghdfe estimates, three columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (DISCREPANCIES.md D-023).
* Input:  data/processed/stata_inputs/ia16_indicators_d.dta
*         (written by analysis/tables/appendix/ia16_indicators_d.py per
*         A19_indicators.do: dind/dind2/dind3 cutoffs and period interactions)
* Output: analysis/stata/results/ia16_indicators_d_results.csv
* Run:    stata-mp -b do analysis/stata/ia16_indicators_d.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia16_indicators_d.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia16_indicators_d_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local r1 var_Q dind d_1933 d_1934 d_After
local r2t var_Q dind dind2 d_1933 d_1934 d_After d2_1933 d2_1934 d2_After
local r3 var_Q dind dind2 dind3 d_1933 d_1934 d_After d2_1933 d2_1934 d2_After d3_1933 d3_1934 d3_After

reghdfe var_inv_rate `r1', absorb(permno year) vce(cluster permno year) version(5)
dumpcol dind "`r1'"
reghdfe var_inv_rate `r2t', absorb(permno year) vce(cluster permno year) version(5)
dumpcol dind2 "`r2t'"
reghdfe var_inv_rate `r3', absorb(permno year) vce(cluster permno year) version(5)
dumpcol dind3 "`r3'"

file close fh
