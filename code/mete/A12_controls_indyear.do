/*
Robustness: Table 6 columns 2-10 with industry-year FEs.
R6 Comment 2: re-run columns 2-10 with absorb(permno sic2_year) instead of
absorb(permno year), so all specifications share the same FE structure as col 1.
No user-written packages required.
*/
set more off
clear all
version 16

local data_dir "/project7/splante/git/gold-clause-abrogation-and-investment/data"
use "`data_dir'/A4_merged.dta", clear

local out_dir "/project7/splante/git/gold-clause-abrogation-and-investment/output/tables"
cap mkdir "`out_dir'"
local outcsv "`out_dir'/t6_indyear_robustness.csv"

* Write CSV header
file open fh using "`outcsv'", write replace
file write fh "col,term,coef,se,pval,N" _n

local terms    "var_Q d d_1933 d_1934 d_After"
local colnames "all_controls_linear q_deciles logasset_deciles netinc_deciles cash_deciles payout_deciles booklev_deciles marketlev_deciles logltl_deciles"

*------------------------------------------------------
* (2) All controls linear, absorb(permno sic2_year)
*------------------------------------------------------
display _newline "Running col 2: all_controls_linear with sic2_year..."
reghdfe var_inv_rate ///
    var_Q_before var_Q_1933 var_Q_1934 var_Q_after ///
    var_logasset_before var_logasset_1933 var_logasset_1934 var_logasset_after ///
    var_netinc_before var_netinc_1933 var_netinc_1934 var_netinc_after ///
    var_cash_before var_cash_1933 var_cash_1934 var_cash_after ///
    var_payout_before var_payout_1933 var_payout_1934 var_payout_after ///
    var_booklev_before var_booklev_1933 var_booklev_1934 var_booklev_after ///
    var_marketlev_before var_marketlev_1933 var_marketlev_1934 var_marketlev_after ///
    var_logltl_before var_logltl_1933 var_logltl_1934 var_logltl_after ///
    var_Q d d_1933 d_1934 d_After, absorb(permno sic2_year) vce(cluster permno year)

local colname : word 1 of `colnames'
local n = e(N)
foreach term of local terms {
    local b  = _b[`term']
    local se = _se[`term']
    local p  = 2 * ttail(e(df_r), abs(`b'/`se'))
    file write fh "`colname',`term'," (`b') "," (`se') "," (`p') ",`n'" _n
}

*------------------------------------------------------
* (3)-(10) Decile portfolio controls, absorb(permno sic2_year)
*------------------------------------------------------
local prefixes "Q logasset netinc cash payout booklev marketlev logltl"
local colidx = 2

foreach pfx of local prefixes {
    local colname : word `colidx' of `colnames'
    display _newline "Running col `colidx': `colname' with sic2_year..."
    reghdfe var_inv_rate fix_var_`pfx'_port_1_before-fix_var_`pfx'_port_10_after ///
        var_Q d d_1933 d_1934 d_After, absorb(permno sic2_year) vce(cluster permno year)
    local n = e(N)
    foreach term of local terms {
        local b  = _b[`term']
        local se = _se[`term']
        local p  = 2 * ttail(e(df_r), abs(`b'/`se'))
        file write fh "`colname',`term'," (`b') "," (`se') "," (`p') ",`n'" _n
    }
    local colidx = `colidx' + 1
}

file close fh
display as res _newline "Wrote CSV -> `outcsv'"
