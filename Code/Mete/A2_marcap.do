set more off
display _newline(200)  
clear

cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"

use crsp_monthly.dta, clear


rename PERMNO permno 
rename SICCD sic 
rename PRC prc 
rename SHROUT shrout 
rename CFACSHR cfacshr
rename DLPRC dlprc
rename ALTPRC altprc

replace shrout = shrout*1e3
replace prc = - prc if prc < 0

gen marcap = prc*shrout

gen month = month(date)
gen year = year(date)

sort date 
egen dateid = group(date) 

xtset permno dateid 

*Alternative 1 
*keep if month == 1

*Alternative 2 
drop if marcap == . 
bys permno year: egen min_month = min(month)
keep if month == min_month  

keep permno year min_month prc shrout marcap sic

save A2_marcap.dta, replace 