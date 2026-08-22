* Table 5 (other outcomes): reghdfe estimates for all six columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (reghdfe 6's revised two-way-cluster computation moves several SEs by one
* printed digit; see DISCREPANCIES.md D-023).
* Input:  data/processed/stata_inputs/table5_other_outcomes.dta
*         (written by analysis/tables/body/t05_other_outcomes.py: deps
*         winsorized per A10_otheroutcomes.do, d-year interactions built)
* Output: analysis/stata/results/table5_other_outcomes_results.csv
* Run:    stata-mp -b do analysis/stata/table5_other_outcomes.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/table5_other_outcomes.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/table5_other_outcomes_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local yrs d_year_1926 d_year_1927 d_year_1928 d_year_1929 d_year_1930 ///
    d_year_1931 d_year_1933 d_year_1934 d_year_1935 d_year_1936 ///
    d_year_1937 d_year_1938 d_year_1939 d_year_1940
local rhs var_Q d `yrs'

foreach spec in "payout var_payout" "cashrat cashrat" "netrep netrep" ///
    "nippe nippe" "cashppe cashppe" "leverage var_booklev" {
    tokenize `spec'
    local key `1'
    local dep `2'
    reghdfe `dep' `rhs', absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `key' "`rhs'"
}

file close fh
