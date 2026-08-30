* IA.12 (omit-repayer and balanced panels): reghdfe estimates, four columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (DISCREPANCIES.md D-023). Column 1's sample is the D-017-family
* reconstruction (the published sample, N = 5,572, is a lost esttab state).
* Input:  data/processed/stata_inputs/ia09_repayers_balanced.dta
*         (written by analysis/tables/appendix/ia09_repayers_balanced.py
*         with the four sample flags from A16_balanced.do)
* Output: analysis/stata/results/ia09_repayers_balanced_results.csv
* Run:    stata-mp -b do analysis/stata/ia09_repayers_balanced.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia09_repayers_balanced.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia09_repayers_balanced_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local yrs d_year_1926 d_year_1927 d_year_1928 d_year_1929 d_year_1930 ///
    d_year_1931 d_year_1933 d_year_1934 d_year_1935 d_year_1936 ///
    d_year_1937 d_year_1938 d_year_1939 d_year_1940
local rhs var_Q d `yrs'

foreach col in omit_repayer balanced_1930_36 balanced_1929_40 balanced_1926_40 {
    reghdfe var_inv_rate `rhs' if `col' == 1, absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `col' "`rhs'"
}

file close fh
