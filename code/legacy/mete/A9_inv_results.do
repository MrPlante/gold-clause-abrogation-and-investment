set more off
display _newline(200)  
clear

/*
* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

**************
*Baseline 
*************
*(1)
reghdfe var_inv_rate var_Q, absorb(permno year) vce(cluster permno year)
*(2)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
*(6)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if ind_3134 != 1, absorb(permno year) vce(cluster permno year)

drop d d_year_1926-d_year_1940
*************************************************
*Definition of dalt (pref shares and/or bonds only)
*************************************************
gen d = dalt 
*Interaction terms with year 
forvalues xx = 1926(1)1940{
    gen d_year_`xx' = dalt_year_`xx'
}
drop d_year_1932

*(3)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)


drop d d_year_1926-d_year_1940
*****************
*Definition of bd
*****************
gen d = bd
*Interaction terms with year 
forvalues xx = 1926(1)1940{
    gen d_year_`xx' = bd_year_`xx'
}
drop d_year_1932

*(4)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)


drop d d_year_1926-d_year_1940
*****************
*Definition of ps
*****************
gen d = ps
*Interaction terms with year 
forvalues xx = 1926(1)1940{
    gen d_year_`xx' = ps_year_`xx'
}
drop d_year_1932

*(5)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
*/

*******************************************************
* AER-style reghdfe table (final clean version)
*******************************************************
version 16
set more off
clear all

* Load data
*cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

***************
* Baseline
***************
*(1)
reghdfe var_inv_rate var_Q, absorb(permno year) vce(cluster permno year)
eststo clear
eststo m1

*(2)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m2

*(6)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940 if ind_3134 != 1, absorb(permno year) vce(cluster permno year)
eststo m6

*************************************************
* Definition of dalt
*************************************************
drop d d_year_*
gen d = dalt
forvalues yy = 1926(1)1940 {
    gen d_year_`yy' = dalt_year_`yy'
}
drop d_year_1932

*(3)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
eststo m3

*****************
* Definition of bd
*****************
drop d d_year_*
gen d = bd
forvalues yy = 1926(1)1940 {
    gen d_year_`yy' = bd_year_`yy'
}
drop d_year_1932

*(4)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno)
eststo m5

*****************
* Definition of ps
*****************
drop d d_year_*
gen d = ps
forvalues yy = 1926(1)1940 {
    gen d_year_`yy' = ps_year_`yy'
}
drop d_year_1932

*(5)
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
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
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_reghdfe_main.tex"


* Main export: no redundant headers, compact spacing
esttab m1 m2 m3 m4 m5 m6 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("(1)" "(2)" "(3)" "(4)" "(5)" "(6)", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1}) ///
    noobs nomtitles nonumber

display as res "✅ Wrote clean AER-style table -> `outfile'"



**************************************************************************
*Figures:Gold coefs
**************************************************************************
* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear
*Figure				  
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)

* Store results
matrix b = e(b)
matrix V = e(V)

* List of your interaction variables (1932 omitted)
local vars d_year_1926 d_year_1927 d_year_1928 ///
           d_year_1929 d_year_1930 d_year_1931 ///
           d_year_1933 d_year_1934 ///
           d_year_1935 d_year_1936 d_year_1937 ///
           d_year_1938 d_year_1939 d_year_1940

* Create dataset scaffold: 1926–1940
clear
set obs 15
gen year  = 1926 + _n - 1
gen double beta  = .
gen double se    = .

* Fill betas/SEs by matching year parsed from variable names
foreach v of local vars {
    local yr = real(substr("`v'", length("`v'")-3, 4))
    quietly replace beta = b[1,"`v'"]           if year == `yr'
    quietly replace se   = sqrt(V["`v'","`v'"]) if year == `yr'
}

* Omitted category: set 1932 to 0 with no SE
replace beta = 0 if year == 1932
replace se   = 0 if year == 1932

* Confidence intervals
gen double upper = beta + 1.96*se
gen double lower = beta - 1.96*se

* Plot: CI caps + point estimates

twoway ///
    (rcap upper lower year, lcolor(black) lwidth(thin)) ///
    (scatter beta year, mcolor(black) msymbol(O)), ///
    yline(0, lpattern(dash) lcolor(black)) ///
    xtitle("Year") ytitle("Coefficient on Year x d") ///
    xlabel(1926(1)1940, angle(45)) ///
    graphregion(color(white)) legend(off)


* Output
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025\Figures"
graph export "gold_coeffs.pdf", replace


**************************************************************************
*Figures: Average investment
**************************************************************************
* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear


keep if year >= 1930 & year < = 1940

/*
*Remove FE
bys permno: egen av_inv = mean(var_inv_rate) 
sum av_inv
replace var_inv_rate = var_inv_rate - av_inv + `r(mean)'
*/
/*
*Only long-term liability > 0
keep if ll_bs_new > 0
*/

gen avinv = . 
gen avinv_d0 = . 
gen avinv_d1 = . 


forvalues xx = 1930(1)1940{
    sum var_inv_rate if year == `xx',d
	replace avinv = `r(mean)' if year == `xx'
	sum var_inv_rate if year == `xx' & d == 0,d
	replace avinv_d0 = `r(mean)' if year == `xx'
	sum var_inv_rate if year == `xx' & d > 0,d
	replace avinv_d1 = `r(mean)' if year == `xx'
}
*/

/*
*Median instead of mean
forvalues xx = 1930(1)1940{
    sum var_inv_rate if year == `xx',d
	replace avinv = `r(p50)' if year == `xx'
	sum var_inv_rate if year == `xx' & d == 0,d
	replace avinv_d0 = `r(p50)' if year == `xx'
	sum var_inv_rate if year == `xx' & d > 0,d
	replace avinv_d1 = `r(p50)' if year == `xx'
}
*/


duplicates drop year, force
twoway ///
    (line avinv     year, lcolor(black) lpattern(solid)     lwidth(medium)) ///
    (line avinv_d0  year, lcolor(black) lpattern(dash)      lwidth(medium)) ///
    (line avinv_d1  year, lcolor(black) lpattern(dot)       lwidth(medium)) ///
    , ///
    xscale(range(1930 1940)) ///
    xlabel(1930(1)1940, angle(45)) ///
    xtitle("Year") ///
    ytitle("Average investment rate") ///
    legend(order(1 "All" 2 "d = 0" 3 "d > 0") rows(1) ) ///
    graphregion(color(white))

* Output
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025\Figures"
graph export "average_inv.pdf", replace













