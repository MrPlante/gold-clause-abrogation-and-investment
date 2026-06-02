set more off
display _newline(200)  
clear


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
rename CFACPR cfacpr 
rename RET ret
rename RETX retx

drop if prc == 0

replace shrout = shrout*1e3
replace prc = - prc if prc < 0

gen month = month(date)
gen year = year(date)


sort year month 
egen timeid = group(year month)

xtset permno timeid
replace cfacshr = L.cfacshr if cfacshr == 0 
replace cfacpr = L.cfacpr if cfacpr == 0 

*Cash dividend 
gen cashdiv = L.shrout*L.prc*(ret-retx)

*Net issuance
gen netissue = (shrout*cfacshr - L.shrout*L.cfacshr)*(prc/cfacpr + L.prc/L.cfacpr)/2 // Michael Roberts paper

keep permno year month cashdiv netissue 

save A3_dividend_monthly.dta, replace 

collapse (sum) cashdiv netissue, by(permno year)


save A3_dividend_annual.dta, replace






















