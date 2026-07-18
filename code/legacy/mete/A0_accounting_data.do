set more off
display _newline(200)  
clear


***********************
*Accounting data 
***********************

cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Feb 2025\data"
import delimited "accounting_data.csv"

*Unreliable data based on Seb's investigation
drop if permno == 11631 | permno == 15093 | permno == 15528 | permno == 24475 // unreliable data based on corrections
drop if permno == 13063 | permno == 14250 // unreliable bond data based on corrections

sort permno manual_year year 
*Unique permno-manual year combinations
egen permno_man = group(permno manual_year)

*There are sum permno x manual year x year duplicates. For all, ppe_bs is missing from one of them. 
bys permno_man year: egen cc = count(year)
list permno year manual_year ppe_bs cc if cc > 1 

*Require netppe_bs to be available 
drop if ppe_bs == . 
drop cc
bys permno_man year: egen cc = count(year)
list permno year manual_year cc if cc > 1 // no more duplicates 

*Declare panel data 
xtset permno_man year 
sum netppe_bs, d 
*There are several 0 and 3 negative observations for netppe_bs. We cannot denominate by them, and cannot use negative in numerator. 
gen inv_rate = netppe_bs/L.netppe_bs - 1 if netppe_bs >= 0 & L.netppe_bs > 0

*Create lagged version of each bs and is variable from the same manual 
ds *_bs

foreach v in `r(varlist)'  {
    gen L`v' = L.`v'
}

ds *_is

foreach v in `r(varlist)'  {
    gen L`v' = L.`v'
}


**Keep later manual among non-missing investment rate values: // was keeping min(inv_rate) to drop missing but that is not always droping missings
drop if inv_rate == . 

bys permno year: egen max_manual = max(manual_year) 
keep if manual_year == max_manual


cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
save A0_accounting_data.dta, replace