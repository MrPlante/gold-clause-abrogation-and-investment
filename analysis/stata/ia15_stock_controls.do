* IA.17 (stock-market-based controls): reghdfe estimates, six columns.
*
* Engine: reghdfe legacy version(5) - the vintage of the submitted table
* (DISCREPANCIES.md D-023). Note the ret_sd decile column (column 4 in the
* manuscript layout) is degenerate under reghdfe 6 (all-missing e(V));
* version(5) is the only engine that produces its standard errors. Column 1
* includes the five raw contemporaneous ann_* variables alongside the
* characteristic-period interactions, reproducing round-1's A20 `ann*`
* wildcard exactly (N 7,033; decision 2026-08-29). A handful of
* decile-column coefficients differ in the last printed digit vs round 1 -
* lost-state fossils, engine-independent (D-022).
* Input:  data/processed/stata_inputs/ia15_stock_controls.dta
*         (written by analysis/tables/appendix/ia15_stock_controls.py per
*         A20_retcontrols.do: chars_annual merge, characteristic-period
*         linears and decile-period dummies)
* Output: analysis/stata/results/ia15_stock_controls_results.csv
* Run:    stata-mp -b do analysis/stata/ia15_stock_controls.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia15_stock_controls.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia15_stock_controls_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local core var_Q d d_1933 d_1934 d_After
local lin
foreach c in var_Q var_logasset var_netinc var_cash var_payout var_booklev var_marketlev var_logltl {
    foreach p in before 1933 1934 after {
        local lin `lin' `c'_`p'
    }
}
local annlin
foreach c in ann_ret_mean ann_ret_sd ann_beta_mktrf ann_beta_smb ann_beta_hml {
    local annlin `annlin' `c'
    foreach p in before 1933 1934 after {
        local annlin `annlin' `c'_`p'
    }
}

* Column 1: all characteristic-period and return-based linear controls
* (raw ann_* included: round-1 A20's `ann*` wildcard)
reghdfe var_inv_rate `lin' `annlin' `core', absorb(permno year) vce(cluster permno year) version(5)
dumpcol linear_ann "`lin' `annlin' `core'"

* Columns 2-6: return-based decile-period dummies
foreach spec in "ret_mean_deciles fix_ann_ret_mean_port" "ret_sd_deciles fix_ann_ret_sd_port" ///
    "beta_mktrf_deciles fix_ann_beta_mktrf_port" "beta_smb_deciles fix_ann_beta_smb_port" ///
    "beta_hml_deciles fix_ann_beta_hml_port" {
    tokenize `spec'
    local key `1'
    local pref `2'
    local ports
    foreach p in before 1933 1934 after {
        forvalues dd = 1/10 {
            local ports `ports' `pref'_`dd'`p'
        }
    }
    reghdfe var_inv_rate `ports' `core', absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `key' "`ports' `core'"
}

file close fh
