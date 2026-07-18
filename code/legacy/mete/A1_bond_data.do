set more off
display _newline(200)  
clear


***********************
*Bond data 
***********************
*just do amount outstanding now. Later: maturity date, ratings
*cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Feb 2025 Mete\Mete\Data\corrections"
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Feb 2025\data"

import excel "gold_clauses.xlsx", sheet("REAL ENTRY") firstrow clear

rename PERMNO permno

*permno 25822 entered as 25822_, only nonnumeric characters in permno
gen permno_end = substr(permno, 6, 1)
replace permno = substr(permno, 1, 5) if permno_end != ""

*make permno numeric
destring permno, replace 

*Issuance year 
gen iss_year = substr(Dated, 1, 4)
destring iss_year, replace force

*Due year
gen due_year = substr(Due, 1, 4)
destring due_year, replace force

*Typo in manual year (6 observations)
replace ManualYear = 1936 if ManualYear == 1036

*Manual reports last year's bonds
gen year = ManualYear -1 
gen dify = iss_year - year 

*drop foreign currency denominated bonds
drop if NotesonCurrency != ""

**Make AmountOutstanding numeric
*There is an entry "$2,755,500 (extended) $203,100(not extended)" for permno 25822, ManualYear 1935.
*We replace that with 2755500 which seems more consistent with the values before/after. 
replace AmountOutstanding = "2755500" if permno == 25822 & ManualYear == 1935
destring AmountOutstanding, replace 

**Reported Debt and Gold indicators
codebook FundedDebt Gold
gen debt_ind = (FundedDebt == "Reported") 
gen gold_ind = (Gold == "Reported") 

keep if debt_ind == 1    				// keep firms with reported debt 
keep if AmountOutstanding != .			// keep those with available AmountOutstanding (e.g., permno 11041 has missings)
*drop if dify > 1 // This filter led to some bonds being dropped because issuance year was not available


cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"

gen ind_3134 = (due_year >= 1931 & due_year <= 1934) //(due_year == 1933 | due_year == 1934)

rename Rating rating
gen rating2 = . 
replace rating2 = 1 if rating == "C"
replace rating2 = 2 if rating == "Ca"
replace rating2 = 3 if rating == "Caa"
replace rating2 = 4 if rating == "B"
replace rating2 = 5 if rating == "Ba"
replace rating2 = 6 if rating == "Baa"
replace rating2 = 7 if rating == "A"
replace rating2 = 8 if rating == "Aa"
replace rating2 = 9 if rating == "Aaa"

bys permno year: egen rating_med = median(rating2)

keep permno ManualYear gold_ind AmountOutstanding debt_ind year ind_3134 rating_med
sort permno year 
bys permno year: gen bondnum = _n

**Total identified gold vs non-gold debt
gen AO_g0 = AmountOutstanding*(1-gold_ind)
gen AO_g1 = AmountOutstanding*(gold_ind)


*Save bond level data for all firms with reported bonds and available AmountOutstanding 
save A1_bond_data_bondlevel.dta, replace

*Total identified funded debt firm x manual year
bys permno ManualYear: egen fd_amount = sum(AmountOutstanding)

bys permno ManualYear: egen fd_amount_g0 = sum(AO_g0)
bys permno ManualYear: egen fd_amount_g1 = sum(AO_g1)

replace ind_3134 = 0 if ind_3134 == .
bys permno: egen ind_3134_max = max(ind_3134)

duplicates drop permno ManualYear, force 

keep permno ManualYear fd_amount* debt_ind year ind_3134_max rating_med

*Save firm level data for all firms with reported bonds and available AmountOutstanding 
save A1_bond_data_firmlevel.dta, replace