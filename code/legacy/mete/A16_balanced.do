version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

*Balanced 
*1930-1936 (7 years)
gen b1 = 1 if year >= 1930 & year <= 1936
bys permno: egen b1s = sum(b1) 

*1929-1940 (12 years)
gen b2 = 1 if year >= 1929 & year <= 1940
bys permno: egen b2s = sum(b2)

*1926-1940 (15 years) 
gen b3 = 1 if year >= 1926 & year <= 1940
bys permno: egen b3s = sum(b3)

*Repay gold clause debt 
xtset permno year 
gen repay2 = 1 if d == 0 & L.d > 0 & year >= 1931 & year <= 1935
bys permno: egen repay = mean(repay2) 
replace repay = 0 if repay == . 

*(1)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if repay == 0, absorb(permno year) vce(cluster permno year)
eststo m1
*(2)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if b1s == 7, absorb(permno year) vce(cluster permno year)
eststo m2
*(3)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if b2s == 12, absorb(permno year) vce(cluster permno year)
eststo m3
*(4)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if b3s == 15, absorb(permno year) vce(cluster permno year)
eststo m4

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
local outfile "`OL'\Tables\tab_balanced.tex"


* Main export: no redundant headers, compact spacing
esttab m1 m2 m3 m4 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("Omit repayer" "1930--1936" "1929--1940" "1926--1940", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nomtitles nonumber

display as res "✅ Wrote clean AER-style table -> `outfile'"