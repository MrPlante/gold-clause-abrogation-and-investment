version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5) 

*1932 dividend indicator 
gen divind2 = (cashrat > 0) if year == 1932 
bys permno: egen divind = mean(divind2)  

*Dividend growth 
gen divgr = cashdiv/L.cashdiv  - 1
replace divgr = 0 if L.cashdiv == 0 & cashdiv == 0

gen divbeq = (cashdiv-netissue)/Lbeq_bs

gen marcap2 = marcap if year == min_year
bys permno: egen marcap_base = mean(marcap2)
gen divy = (cashdiv-netissue)/marcap_base

xtset permno year

gen divshare = (cashdiv-netissue)/ni_is if  ni_is > cashdiv
winsor2 divgr divbeq divy divshare, replace by(year) cuts(0.5 99.5) 

eststo clear

*A1
reghdfe cashrat var_Q d d_1933 d_1934 d_After if L.cashrat > 0, absorb(permno year) vce(cluster permno year)
eststo m1
*A2
reghdfe cashrat var_Q d d_1933 d_1934 d_After if L.cashrat == 0, absorb(permno year) vce(cluster permno year)
eststo m2
*A3
reghdfe cashrat var_Q d d_1933 d_1934 d_After if divind == 1, absorb(permno year) vce(cluster permno year)
eststo m3
*A4
reghdfe cashrat var_Q d d_1933 d_1934 d_After if divind == 0, absorb(permno year) vce(cluster permno year)
eststo m4

*A5
reghdfe divgr var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m5
*A6
reghdfe divbeq var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m6
*A7
reghdfe divy var_Q d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m7
*A8
reghdfe divshare Q  d d_1933 d_1934 d_After, absorb(permno year) vce(cluster permno year)
eststo m8

* ---------- Keep/order & labels ----------
local keep_list d_1933 d_1934 d_After
local vlab ///
    d_1933  "1933 \ensuremath{\times d}" ///
    d_1934  "1934 \ensuremath{\times d}" ///
    d_After "After \ensuremath{\times d}"

* ---------- Output path ----------
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_adddiv.tex"

esttab m1 m2 m3 m4 m5 m6 m7 m8 using "`outfile'", replace ///
    booktabs label nonotes nodepvars ///
    collabels(none) nomtitles ///
    mlabels("(1)" "(2)" "(3)" "(4)" "(5)" "(6)" "(7)" "(8)", span prefix("\multicolumn{1}{c}{") suffix("}")) ///
    cells("b(star fmt(3))" "se(par fmt(3))") ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    keep(`keep_list') order(`keep_list') ///
    varlabels(`vlab') ///
    stats(r2 N, labels("\ensuremath{R^2}" "Observations") fmt(3 %9.0gc)) ///
    alignment(D{.}{.}{-1})     noobs nomtitles nonumber

di as res "Wrote -> `outfile'"