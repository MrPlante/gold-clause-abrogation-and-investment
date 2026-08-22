* Table 4 (main investment): reghdfe estimates for all seven columns.
*
* Engine: reghdfe legacy version(5) for every column - the project uses one
* engine everywhere (D-023 addendum 3). The submitted table was a reghdfe-6
* run for columns 1-6 (four SE last digits differ, no stars); column 7 is
* degenerate under reghdfe 6 (all-missing e(V)) and version(5) is the only
* engine producing its standard errors. The published round-1 column-7 SEs
* match no reproducible vintage (D-017/D-023).
* Input:  data/processed/stata_inputs/table4_investment.dta
*         (written by analysis/tables/body/t04_investment.py; the
*         no_redemption flag is the D-017 col-4 reconstruction, dalt is
*         Mete's recovered col-5 fixed-claims exposure)
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

foreach stem in d ps bd dalt {
    local `stem'_yrs
    foreach y in 1926 1927 1928 1929 1930 1931 1933 1934 1935 1936 1937 1938 1939 1940 {
        local `stem'_yrs ``stem'_yrs' `stem'_year_`y'
    }
}

* Column 1: classic investment regression
reghdfe var_inv_rate var_Q, absorb(permno year) vce(cluster permno year) version(5)
dumpcol classic "var_Q"

* Column 2: baseline overhang
reghdfe var_inv_rate var_Q d `d_yrs', absorb(permno year) vce(cluster permno year) version(5)
dumpcol overhang "var_Q d `d_yrs'"

* Column 3: exclude firms with bonds maturing 1931-1934
reghdfe var_inv_rate var_Q d `d_yrs' if no_maturity == 1, absorb(permno year) vce(cluster permno year) version(5)
dumpcol no_maturity "var_Q d `d_yrs'"

* Column 4: exclude firms that retired gold-clause debt 1931-1935
reghdfe var_inv_rate var_Q d `d_yrs' if no_redemption == 1, absorb(permno year) vce(cluster permno year) version(5)
dumpcol no_redemption "var_Q d `d_yrs'"

* Column 5: fixed-claims exposure (Mete's original code, recovered
* 2026-08-22; D-023 addendum 2 - reproduces the published column, N=6,048).
* Level = gold-clause debt over bank debt + bonds + preferred stock in 1930
* (built by the Python builder, incl. the pre-1930 lagged-bond-share level
* that keeps the level out of the firm FE); interactions = the panel's
* firm-constant dalt_year_* columns.
reghdfe var_inv_rate var_Q dalt `dalt_yrs', absorb(permno year) vce(cluster permno year) version(5)
dumpcol fixed_claims "var_Q dalt `dalt_yrs'"

* Column 6: preferred-share placebo
reghdfe var_inv_rate var_Q ps `ps_yrs', absorb(permno year) vce(cluster permno year) version(5)
dumpcol pref_shares "var_Q ps `ps_yrs'"

* Column 7: bank-debt placebo
reghdfe var_inv_rate var_Q bd `bd_yrs', absorb(permno year) vce(cluster permno year) version(5)
dumpcol bank_debt "var_Q bd `bd_yrs'"

file close fh
