set more off
display _newline(200)  
clear


*******************************************************
* AER-style reghdfe table (final clean version)
*******************************************************
version 16
set more off
clear all

* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

***************
* Baseline
***************

winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5) 

*(1)
reghdfe payout var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo clear
eststo m1

*(2)
reghdfe cashrat var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m2

*(3)
reghdfe netrep var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m3

drop denom*
gen denom2 = netppe_bs if year <= min_year
bys permno: egen denom3 = mean(denom2)
gen denom = denom3 

gen cashppe = cash_bs/denom
gen nippe = ni_is/denom

winsor2 cashppe nippe, replace by(year) cuts(0.5 99.5) 

*(4)
reghdfe nippe var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m4

*(5)
reghdfe cashppe var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m5

*(5)
reghdfe var_booklev var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m6

*******************************************************
* Export clean AER-style table
*******************************************************
local yrs 1926 1927 1928 1929 1930 1931 1933 1934 1935 1936 1937 1938 1939 1940
local keep_list var_Q d
foreach y of local yrs {
    local keep_list `keep_list' d_year_`y'
}

local vlab var_Q "Q" d "\ensuremath{d}"
foreach y of local yrs {
    local vlab `vlab' d_year_`y' "`y' \ensuremath{\times d}"
}

* Output
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_reghdfe_others.tex"


* Main export: no redundant headers, compact spacing
esttab m1 m2 m3 m4 m5 m6 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("Payout" "Dividend" "Net rep." "Profits" "Cash" "Leverage", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nomtitles nonumber

display as res "✅ Wrote clean AER-style table -> `outfile'"




