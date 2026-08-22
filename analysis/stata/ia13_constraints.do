* IA.13 (financial-constraint triple interactions): reghdfe estimates.
*
* Engine: reghdfe legacy version(5) (DISCREPANCIES.md D-023). Five printed
* cells of the round-1 table (three coefficients, two SEs) match no
* reproducible state under any engine - fossils of a lost intermediate run
* (D-022 addendum); this do-file's output is the adopted reproducible
* version.
* Input:  data/processed/stata_inputs/ia13_constraints.dta
*         (written by analysis/tables/appendix/ia13_constraints.py: the
*         three A17_sizecashlev.do model panels stacked with mkey =
*         small / lowcash / highlev, interactions prebuilt per model)
* Output: analysis/stata/results/ia13_constraints_results.csv
* Run:    stata-mp -b do analysis/stata/ia13_constraints.do [project_root]
version 16
set more off
args root
if "`root'" == "" local root .

use "`root'/data/processed/stata_inputs/ia13_constraints.dta", clear

capture program drop dumpcol
program define dumpcol
    args col terms
    foreach x of local terms {
        file write fh "`col',`x'," %20.0g (_b[`x']) "," %20.0g (_se[`x']) "," %20.0g (e(df_r)) "," %20.0g (e(r2)) "," %20.0g (e(N)) _n
    }
end

file open fh using "`root'/analysis/stata/results/ia13_constraints_results.csv", write replace
file write fh "col,term,b,se,df,r2,N" _n

local rhs var_Q d d_x y1933_x y1934_x After_x d_1933 d_1934 d_After d_1933_x d_1934_x d_After_x

foreach m in small lowcash highlev {
    reghdfe var_inv_rate `rhs' if mkey == "`m'", absorb(permno year) vce(cluster permno year) version(5)
    dumpcol `m' "`rhs'"
}

file close fh
