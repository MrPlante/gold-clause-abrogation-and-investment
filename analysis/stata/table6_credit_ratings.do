* Table 6 / IA.9 (credit ratings): reghdfe estimates for the three models.
* Body Table 6 shows the net-investment and dividend columns; IA.9 shows all
* three in full.
*
* Engine: reghdfe legacy version(5) - one engine everywhere (D-023
* addendum 3). Vs the submitted (reghdfe-6) tables this moves ~21 SE last
* digits and strengthens three uncited stars in IA.9's payout column.
* Input:  data/processed/stata_inputs/table6_credit_ratings.dta
*         (written by analysis/tables/body/t06_credit_ratings.py per
*         A21_ratings_yearbyyear.do: payout/cashrat winsorized, d demeaned
*         among d>0 firms, interaction terms rebuilt)
* Output: analysis/stata/results/table6_credit_ratings_results.csv
* Run:    stata-mp -b do analysis/stata/table6_credit_ratings.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/table6_credit_ratings.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/table6_credit_ratings_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local dy
local yl
local dyl
foreach y in 1926 1927 1928 1929 1930 1931 1933 1934 1935 1936 1937 1938 1939 1940 {
    local dy `dy' d_year_`y'
    local yl `yl' year_`y'_Low
    local dyl `dyl' d_year_`y'_Low
}
local rhs var_Q d d_Low `dy' `yl' `dyl'

foreach dep in var_inv_rate payout cashrat {
    reghdfe `dep' `rhs', absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `dep' "`rhs'"
}

file close fh
