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

keep permno year payout cashrat netrep var_Q d d_year_1926-d_year_1940

merge 1:1 permno year using denom_div.dta

drop _merge
merge 1:m permno year using A3_dividend_monthly.dta
keep if _merge == 3
drop _merge

save monthly_div.dta, replace

duplicates drop year permno, force
reghdfe payout var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
reghdfe cashrat var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
reghdfe netrep var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)


/*
replace cashdiv = 0 if cashdiv == .
replace netissue = 0 if netissue == .


bys permno year: egen cashdiv_ann = sum(cashdiv)
gen cashrat_ann2 = cashdiv_ann/denom
replace cashrat_ann2 = 0 if cashrat_ann2 == .
keep if cashrat_ann2 != .
*/

/*
duplicates drop year permno, force

winsor2 cashrat_ann2, replace by(year) cuts(0.5 99.5) 

reghdfe payout var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
reghdfe cashrat var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
reghdfe cashrat_ann2 var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)

reghdfe netrep var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
*/