* IA.15 (additional dividend specifications): reghdfe estimates, eight columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (resolves the one previously irreproducible SE digit in the divgr column;
* DISCREPANCIES.md D-023).
* Input:  data/processed/stata_inputs/ia15_dividend_additional.dta
*         (written by analysis/tables/appendix/ia15_dividend_additional.py:
*         the eight A18_additionaldividend.do samples stacked with mkey,
*         unified dependent variable depv; divshare uses raw Q as control)
* Output: analysis/stata/results/ia15_dividend_additional_results.csv
* Run:    stata-mp -b do analysis/stata/ia15_dividend_additional.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia15_dividend_additional.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia15_dividend_additional_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

foreach m in cashrat_lag_pos cashrat_lag_zero cashrat_divind_pos cashrat_divind_zero divgr divbeq divy divshare {
    local qc = cond("`m'" == "divshare", "Q", "var_Q")
    reghdfe depv `qc' d d_1933 d_1934 d_After if mkey == "`m'", absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `m' "`qc' d d_1933 d_1934 d_After"
}

file close fh
