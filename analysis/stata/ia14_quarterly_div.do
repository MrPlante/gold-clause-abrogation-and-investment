* IA.14 (quarter-specific dividends): reghdfe estimates, five columns.
*
* Engine: reghdfe legacy version(5) - one engine everywhere (D-023
* addendum 3). SEs here are one-way clustered by firm; both engines
* reproduce the submitted table at printed precision.
* Input:  data/processed/stata_inputs/ia14_quarterly_div.dta
*         (written by analysis/tables/appendix/ia14_quarterly_div.py: the
*         annual and per-quarter firm-year samples stacked with mkey,
*         unified dependent variable depv)
* Output: analysis/stata/results/ia14_quarterly_div_results.csv
* Run:    stata-mp -b do analysis/stata/ia14_quarterly_div.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia14_quarterly_div.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia14_quarterly_div_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local yrs d_year_1926 d_year_1927 d_year_1928 d_year_1929 d_year_1930 ///
    d_year_1931 d_year_1933 d_year_1934 d_year_1935 d_year_1936 ///
    d_year_1937 d_year_1938 d_year_1939 d_year_1940
local rhs var_Q d `yrs'

foreach m in annual Q1 Q2 Q3 Q4 {
    reghdfe depv `rhs' if mkey == "`m'", absorb(permno year_int) vce(cluster permno) version(5)
    dumpcol `m' "`rhs'"
}

file close fh
