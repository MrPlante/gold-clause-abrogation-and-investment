* Export parallel-trend coefficient figure (matches A9_inv_results.do gold_coeffs block).
version 16
set more off
args repo
if "`repo'" == "" {
    local repo "/project/splante/git/gold-clause-abrogation-and-investment"
}

use "`repo'/data/A4_merged.dta", clear
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, ///
    absorb(permno year) vce(cluster permno year)

matrix b = e(b)
matrix V = e(V)

local vars d_year_1926 d_year_1927 d_year_1928 d_year_1929 d_year_1930 ///
    d_year_1931 d_year_1933 d_year_1934 d_year_1935 d_year_1936 d_year_1937 ///
    d_year_1938 d_year_1939 d_year_1940

clear
set obs 15
gen year = 1926 + _n - 1
gen double beta = .
gen double se = .

foreach v of local vars {
    local yr = real(substr("`v'", length("`v'")-3, 4))
    quietly replace beta = b[1,"`v'"] if year == `yr'
    quietly replace se = sqrt(V["`v'","`v'"]) if year == `yr'
}
replace beta = 0 if year == 1932
replace se = 0 if year == 1932
gen double upper = beta + 1.96*se
gen double lower = beta - 1.96*se

twoway ///
    (rcap upper lower year, lcolor(black) lwidth(thin)) ///
    (scatter beta year, mcolor(black) msymbol(O)), ///
    yline(0, lpattern(dash) lcolor(black)) ///
    xtitle("Year") ytitle("Coefficient on Year x d") ///
    xlabel(1926(1)1940, angle(45)) ///
    graphregion(color(white)) legend(off)

local out "`repo'/manuscript/figures/body"
cap mkdir "`out'"
graph export "`out'/parallel_trend_plot_stata.pdf", replace
