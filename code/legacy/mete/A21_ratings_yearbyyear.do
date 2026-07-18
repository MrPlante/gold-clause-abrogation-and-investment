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

winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5) 

* ---------- Run regressions ----------
eststo clear

*Demean d
sum d if d > 0, d
replace d = d - `r(mean)'

replace d_Low  = d*rating_ind

forvalues xx = 1926(1)1940{
replace d_year_`xx' = d*year_`xx'
}

forvalues xx = 1926(1)1940{
replace d_year_`xx'_Low = d*year_`xx'*rating_ind
}

drop d_year_1932_Low
drop year_1932_Low

reghdfe var_inv_rate ///
    var_Q d d_Low d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m1
	
	
reghdfe payout ///
    var_Q d d_Low d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m2

reghdfe cashrat ///
    var_Q d d_Low d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)
eststo m3

*******************************************************
* Export clean AER-style table
*******************************************************
local yrs 1926 1927 1928 1929 1930 1931 1933 1934 1935 1936 1937 1938 1939 1940
local keep_list var_Q d d_Low
foreach y of local yrs {
    local keep_list `keep_list' d_year_`y'
}
foreach y of local yrs {
    local keep_list `keep_list' year_`y'_Low
}
foreach y of local yrs {
    local keep_list `keep_list' d_year_`y'_Low
}

local vlab var_Q "Q" d "\ensuremath{d}" d_Low "Low rating"
foreach y of local yrs {
    local vlab `vlab' d_year_`y' "`y' \ensuremath{\times d}"
}
foreach y of local yrs {
    local vlab `vlab' year_`y'_Low "`y' \ensuremath{\times} Low rating"
}
foreach y of local yrs {
    local vlab `vlab' d_year_`y'_Low "`y' \ensuremath{\times d \times} Low rating"
}

* Output
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_ratings_year.tex"



* Main export: no redundant headers, compact spacing
esttab m1 m2 m3 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("Net investment" "Payout" "Dividend", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nomtitles nonumber












