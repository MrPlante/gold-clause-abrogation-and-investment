* Table 7 (controls): reghdfe estimates for all ten columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (DISCREPANCIES.md D-023). These are the specs on which the old in-process
* Python-Stata bridge segfaulted; run as a batch do-file they are unremarkable.
* Input:  data/processed/stata_inputs/table7_controls.dta
*         (written by analysis/tables/body/t07_controls.py: core terms,
*         linear characteristic-period controls, decile-period dummies,
*         sic2_year cell id)
* Output: analysis/stata/results/table7_controls_results.csv
* Run:    stata-mp -b do analysis/stata/table7_controls.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/table7_controls.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/table7_controls_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local core var_Q d d_1933 d_1934 d_After
local lin
foreach c in var_Q var_logasset var_netinc var_cash var_payout var_booklev var_marketlev var_logltl {
    foreach p in before 1933 1934 after {
        local lin `lin' `c'_`p'
    }
}

* Column 1: industry-year fixed effects
reghdfe var_inv_rate `core', absorb(permno sic2_year) vce(cluster permno year) version(5)
dumpcol industry_year_fe "`core'"

* Column 2: all characteristics x period, linear
reghdfe var_inv_rate `lin' `core', absorb(permno year) vce(cluster permno year) version(5)
dumpcol all_controls_linear "`lin' `core'"

* Columns 3-10: decile-period dummies, one characteristic per column
foreach spec in "q_deciles fix_var_Q_port" "logasset_deciles fix_var_logasset_port" ///
    "netinc_deciles fix_var_netinc_port" "cash_deciles fix_var_cash_port" ///
    "payout_deciles fix_var_payout_port" "booklev_deciles fix_var_booklev_port" ///
    "marketlev_deciles fix_var_marketlev_port" "logltl_deciles fix_var_logltl_port" {
    tokenize `spec'
    local key `1'
    local pref `2'
    local ports
    foreach p in before 1933 1934 after {
        forvalues dd = 1/10 {
            local ports `ports' `pref'_`dd'_`p'
        }
    }
    reghdfe var_inv_rate `ports' `core', absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `key' "`ports' `core'"
}

file close fh
