set more off
display _newline(200)  
clear

cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"

*Accounting data
use A0_accounting_data.dta, clear 

merge 1:1 permno year using A1_bond_data_firmlevel.dta

drop _merge

*Market cap data (first available monthly market cap for each firm)
merge 1:1 permno year using A2_marcap.dta

replace sic = 0 if sic == . 
gen sic2 = floor(sic/100)
egen sic2_year = group(sic2 year)

*Dividend data 
drop _merge
merge 1:1 permno year using A3_dividend_annual.dta

*Net income data 
drop ni_is
drop _merge 
merge 1:1 permno year using netincome.dta 



codebook permno if inv_rate == . & fd_amount != . // 163 firms with bond but no accounting data

drop if sic2 >=40 & sic2 <= 49 // Transportation & communication & utilities
drop if sic2 >=60 & sic2 <= 69 // Finance & insurance 

*Unreliable data based on Seb's investigation
drop if permno == 11631 | permno == 15093 | permno == 15528 | permno == 24475 // unreliable data based on corrections
drop if permno == 13063 | permno == 14250 // unreliable bond data based on corrections

codebook permno if inv_rate == . & fd_amount != . & year >= 1930 & year <= 1935 // 77 firms with bond but no accounting data 
sum permno if inv_rate == . & fd_amount != . & year >= 1930 & year <= 1935 // 77 firms with bond but no accounting data 

drop if inv_rate == . // drop bond data without accounting data 

codebook permno if marcap == . // 77 firms with bond but no accounting data 

xtset permno year 


gen Q = (marcap + Lta_bs - Lbeq_bs)/Lta_bs

sum inv_rate Q if year >= 1926 & year <= 1940

keep if year >= 1926 & year <= 1940
keep if Q != .


*Definition of long-term liabilities
gen ll_bs_new = cb_bs + ps_bs + bd_bs
gen Lll_bs_new = Lcb_bs + Lps_bs + Lbd_bs

*****************
*Definition of d
*****************
replace fd_amount = 0 if fd_amount == . 
replace fd_amount_g0 = 0 if fd_amount_g0 == . 
replace fd_amount_g1 = 0 if fd_amount_g1 == . 

gen d_1930 = (fd_amount_g1)/(ll_bs_new) if year == 1930   
replace d_1930 = 0 if ll_bs_new == 0 & year == 1930  
replace d_1930 = 1 if d_1930 > 1 & d_1930 != . & year == 1930  

bys permno: egen d = mean(d_1930)


gen d_all = Lcb_bs/Lll_bs_new
replace d = d_all if year <= 1930  
replace d = 0 if d == .     // set to zero if the firm has no 1930 data

gen dd = (fd_amount_g1)/(ll_bs_new)
gen d_orig = d
replace d_orig = L.dd if year >= 1932 & year <= 1936
replace d_orig = 0 if d_orig == .     


*Interaction terms with year 
sum year 
forvalues xx = `r(min)'(1)`r(max)'{
gen year_`xx' = (year == `xx')
}
forvalues xx = 1926(1)1940{
    gen d_year_`xx' = d*year_`xx'
}

drop d_year_1932

*Interaction terms with before/after 

gen d_Before = d*(year<=1932)
gen d_1933   = d*(year==1933)
gen d_1934   = d*(year==1934)
gen d_After  = d*(year>=1935)

*Low rating indicator 
gen rating_ind2 = (rating_med <=5)  if year == 1930
*replace rating_ind2 = 1 if rating_ind2 == . & fd_amount_g1 > 0 & year == 1930
replace rating_ind2 = 0 if rating_ind2 == .  & year == 1930

bys permno: egen rating_ind = mean(rating_ind2) 
replace rating_ind = 0 if rating_ind == .  

*Interaction terms 
gen d_Before_Low = d*(year<=1932)*rating_ind
gen d_1933_Low   = d*(year==1933)*rating_ind
gen d_1934_Low   = d*(year==1934)*rating_ind
gen d_After_Low  = d*(year>=1935)*rating_ind

gen d_Low  = d*rating_ind


gen Before_Low = (year<=1932)*rating_ind
gen y1933_Low   = (year==1933)*rating_ind
gen y1934_Low   = (year==1934)*rating_ind
gen After_Low  = (year>=1935)*rating_ind


forvalues xx = 1926(1)1940{
    gen d_year_`xx'_Low = d*year_`xx'*rating_ind
}
forvalues xx = 1926(1)1940{
    gen year_`xx'_Low = year_`xx'*rating_ind
}

*****************
*Definition of bd
*****************
gen bd_1930 = (bd_bs)/(ll_bs_new) if year == 1930   
replace bd_1930 = 0 if ll_bs_new == 0 & year == 1930  
replace bd_1930 = . if bd_1930 > 1 & bd_1930 != . & year == 1930  

bys permno: egen bd = mean(bd_1930)

gen bd_all = Lbd_bs/Lll_bs_new
replace bd = bd_all if year <= 1930  
replace bd = 0 if bd == .     // set to zero if the firm has no 1930 data

*Interaction terms with year 
forvalues xx = 1926(1)1940{
    gen bd_year_`xx' = bd*year_`xx'
}


*****************
*Definition of ps
*****************
gen ps_1930 = (ps_bs)/(ll_bs_new) if year == 1930   
replace ps_1930 = 0 if ll_bs_new == 0 & year == 1930  
replace ps_1930 = . if ps_1930 > 1 & ps_1930 != . & year == 1930  

bys permno: egen ps = mean(ps_1930)

gen ps_all = Lps_bs/Lll_bs_new
replace ps = ps_all if year <= 1930  
replace ps = 0 if ps == .     // set to zero if the firm has no 1930 data

*Interaction terms with year 
forvalues xx = 1926(1)1940{
    gen ps_year_`xx' = ps*year_`xx'
}



*************************************************
*Definition of dalt (pref shares and/or bonds only)
*************************************************

/*
*Original version
gen dalt_1930 = (fd_amount_g1)/(cb_bs + ps_bs) if year == 1930   // will be missing if cs_bs and ps_bs is zero
replace dalt_1930 = 1 if dalt_1930 > 1 & dalt_1930 != . & year == 1930  

bys permno: egen dalt = mean(dalt_1930)

gen dalt_all = Lcb_bs/(Lcb_bs + Lps_bs) 
replace dalt = dalt_all if year <= 1930 // this is mainly the problem 


*Interaction terms with year 

forvalues xx = 1926(1)1940{
    gen dalt_year_`xx' = dalt*year_`xx'
}
*/


gen dalt_1930 = (fd_amount_g1)/(bd_bs + cb_bs + ps_bs) if year == 1930   // will be missing if cs_bs and ps_bs is zero
replace dalt_1930 = 1 if dalt_1930 > 1 & dalt_1930 != . & year == 1930  

bys permno: egen m_bd = mean(bd_bs)
bys permno: egen m_cb = mean(cb_bs)
bys permno: egen m_ps = mean(ps_bs)

replace dalt_1930 = 0 if dalt_1930 == . & (m_bd > 0 | m_cb > 0 | m_ps > 0) & year == 1930

bys permno: egen dalt = mean(dalt_1930)


gen dalt_all = Lcb_bs/(Lbd_bs + Lcb_bs + Lps_bs) 
replace dalt_all = 0 if dalt_all == . & (m_bd > 0 | m_cb > 0 | m_ps > 0)


replace dalt = dalt_all if year <= 1930 //& dalt_all != . // this is mainly the problem 

gen ddalt = (fd_amount_g1)/(bd_bs + cb_bs + ps_bs)
gen dalt_orig = dalt
replace dalt_orig = L.ddalt if year >= 1932 & year <= 1936
replace dalt_orig = 0 if dalt_orig == .     
gen daltind_orig = (dalt > 0)


*Interaction terms with year 

forvalues xx = 1926(1)1940{
    gen dalt_year_`xx' = dalt*year_`xx'
}

*/

***********
*Dividends 
***********
gen year2 = year if year >= 1930
bys permno: egen min_year = min(year2)

gen denom2 = cs_bs if year <= min_year
bys permno: egen denom3 = mean(denom2)
gen denom = denom3 

gen cashrat = cashdiv/denom
gen payout  = (cashdiv-netissue)/denom
gen netrep  = (-netissue)/denom

replace cashrat = 0 if cashrat == .
replace payout = 0 if payout == .
replace netrep = 0 if netrep == . 

*Variables in summary stat table 
gen var_inv_rate 	= inv_rate 
gen var_Q 			= Q
gen var_logasset 	= ln(ta_bs)
gen var_netinc   	= ni_is/ta_bs
gen var_cash     	= cash_bs/ta_bs
gen var_payout      = payout
gen var_booklev 	= (ta_bs - beq_bs)/ta_bs 
gen var_marketlev 	= (ta_bs - beq_bs)/(ta_bs - beq_bs + marcap)
gen var_logltl     	= ln(ll_bs_new)
replace var_logltl 	= 0 if ll_bs_new == 0     // replacing with zero 
gen var_cbltl 		= cb_bs/ll_bs_new 
replace var_cbltl 	= 0 if ll_bs_new == 0     // replacing with zero - these replacements will result in averages not adding up to 1
gen var_psltl 		= ps_bs/ll_bs_new 
replace var_psltl 	= 0 if ll_bs_new == 0     // replacing with zero 
gen var_bdltl 		= bd_bs/ll_bs_new 
replace var_bdltl 	= 0 if ll_bs_new == 0     // replacing with zero 
gen dind 		= (d > 0)
gen dind_orig   = (d_orig > 0)

winsor2 var_*, replace by(year) cuts(0.5 99.5)

***********************
*Controls
***********************
gen ph = . 
foreach v of varlist var_* {
drop ph 
gen ph = `v' if year == min_year // 1930 or first year
bys permno: egen fix_`v' = mean(ph)
}
foreach v of varlist var_* {
	gen `v'_before = fix_`v'*(year < 1933)
	gen `v'_1933 = fix_`v'*(year == 1933)
	gen `v'_1934 = fix_`v'*(year == 1934)
	gen `v'_after = fix_`v'*(year > 1934)
}

*Deciles 
foreach v of varlist fix_* {
astile `v'_port = `v', nq(10)	
}
foreach v of varlist fix_*port{ 
forvalues xx = 1(1)10{
gen	`v'_`xx'_before = (`v'==`xx')*(year < 1933)
gen	`v'_`xx'_1933 = (`v'==`xx')*(year == 1933)
gen	`v'_`xx'_1934 = (`v'==`xx')*(year == 1934)
gen	`v'_`xx'_after = (`v'==`xx')*(year > 1934)
}
}




save A4_merged.dta, replace


