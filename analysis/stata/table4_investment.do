* Table 4 (main investment): reghdfe estimates for all seven columns.
*
* Engine: current reghdfe (6.13.1) for columns 1-6, matching the vintage of
* the submitted table. Column 7 (bank-debt placebo) is the one spec where
* reghdfe 6 returns an all-missing e(V) ("variance matrix is nonsymmetric or
* highly singular"); it runs under the legacy version(5) engine, the only
* reghdfe code path that produces standard errors for it. The published
* round-1 column-7 SEs match no reproducible vintage (DISCREPANCIES.md
* D-017/D-023).
* Input:  data/processed/stata_inputs/table4_investment.dta
*         (written by analysis/tables/body/t04_investment.py; sample flags
*         no_redemption / positive_ltl are the D-017 reconstructions)
* Output: analysis/stata/results/table4_investment_results.csv
* Run:    stata-mp -b do analysis/stata/table4_investment.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/table4_investment.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/table4_investment_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

foreach stem in d ps bd {
    local `stem'_yrs
    foreach y in 1926 1927 1928 1929 1930 1931 1933 1934 1935 1936 1937 1938 1939 1940 {
        local `stem'_yrs ``stem'_yrs' `stem'_year_`y'
    }
}

* Column 1: classic investment regression
reghdfe var_inv_rate var_Q, absorb(permno year) vce(cluster permno year)
dumpcol classic "var_Q"

* Column 2: baseline overhang
reghdfe var_inv_rate var_Q d `d_yrs', absorb(permno year) vce(cluster permno year)
dumpcol overhang "var_Q d `d_yrs'"

* Column 3: exclude firms with bonds maturing 1931-1934
reghdfe var_inv_rate var_Q d `d_yrs' if no_maturity == 1, absorb(permno year) vce(cluster permno year)
dumpcol no_maturity "var_Q d `d_yrs'"

* Column 4: exclude firms that retired gold-clause debt 1931-1935
reghdfe var_inv_rate var_Q d `d_yrs' if no_redemption == 1, absorb(permno year) vce(cluster permno year)
dumpcol no_redemption "var_Q d `d_yrs'"

* Column 5: firms with positive long-term liabilities in 1930
reghdfe var_inv_rate var_Q d `d_yrs' if positive_ltl == 1, absorb(permno year) vce(cluster permno year)
dumpcol positive_ltl "var_Q d `d_yrs'"

* Column 6: preferred-share placebo
reghdfe var_inv_rate var_Q ps `ps_yrs', absorb(permno year) vce(cluster permno year)
dumpcol pref_shares "var_Q ps `ps_yrs'"

* Column 7: bank-debt placebo - legacy engine (see header)
reghdfe var_inv_rate var_Q bd `bd_yrs', absorb(permno year) vce(cluster permno year) version(5)
dumpcol bank_debt "var_Q bd `bd_yrs'"

file close fh
