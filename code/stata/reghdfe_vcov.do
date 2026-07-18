* Export reghdfe variance matrix for Python pyfixest alignment.
* Usage (from lib/vcov.py):
*   stata-mp -b do reghdfe_vcov.do <input.dta> <dep> <rhs> <absorb> <cluster> <vcov_out> <names_out> [winsor_vars]
version 16
set more off
args input dep rhs absorb cluster vcov_out names_out winsor_vars

* RHS, absorb, cluster, and winsor lists are pipe-delimited (see lib/vcov.py).
local rhs : subinstr local rhs "|" " ", all
local absorb : subinstr local absorb "|" " ", all
local cluster : subinstr local cluster "|" " ", all
local winsor_vars : subinstr local winsor_vars "|" " ", all

use "`input'", clear
if "`winsor_vars'" != "" {
    winsor2 `winsor_vars', replace by(year) cuts(0.5 99.5)
}

reghdfe `dep' `rhs', absorb(`absorb') vce(cluster `cluster')

local cols : colnames e(b)
local k : colsof(e(b))

tempname posth
postfile `posth' str64 name using "`names_out'", replace
foreach v of local cols {
    post `posth' ("`v'")
}
postclose `posth'

matrix V = e(V)
preserve
clear
svmat V, names(v)
save "`vcov_out'", replace
restore
