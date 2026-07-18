set more off
display _newline(200)
clear all
version 16

* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

*******************************************************
* Construct aggregate investment rate objects (full sample)
*******************************************************
bys year: egen double sumk = total(netppe)
gen double Lnetppe_new = netppe/(1+var_inv_rate)
bys year: egen double Lsumk = total(Lnetppe_new)
gen double total_inv_rate = sumk/Lsumk - 1


/********************************************************
(1) FULL-SAMPLE REGRESSION COEFFICIENTS (store in locals)
********************************************************/

*******************************************************
* Baseline: year-by-year time-varying effect
*******************************************************
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)

* store beta_y = _b[d_year_y], with 1932 omitted => beta_1932 = 0
forvalues y = 1926/1940 {
    local b_base_`y' = .
    capture local b_base_`y' = _b[d_year_`y']
}
local b_base_1932 = 0


*******************************************************
* With rating: year-by-year base + Low increment
*******************************************************
replace d_Low = d*rating_ind

forvalues xx = 1926/1940 {
    replace d_year_`xx'      = d*year_`xx'
    replace d_year_`xx'_Low  = d*year_`xx'*rating_ind
}
capture drop d_year_1932_Low
capture drop year_1932_Low

reghdfe var_inv_rate ///
    var_Q d d_Low d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)

forvalues y = 1926/1940 {
    local b_rat_`y' = .
    local g_rat_`y' = .
    capture local b_rat_`y' = _b[d_year_`y']
    capture local g_rat_`y' = _b[d_year_`y'_Low]
}
local b_rat_1932 = 0
local g_rat_1932 = 0


*******************************************************
* With size: 4 time bins (<1933 baseline) base + small increment
*******************************************************

* define small (firm-level) using median log assets in min year among d>0
quietly summarize year, meanonly
local min_year = r(min)

quietly summarize var_logasset if year == `min_year' & d > 0, detail
local p50 = r(p50)

gen byte tvSB_small2 = (var_logasset < `p50') if !missing(var_logasset)
bys permno: egen double tvSB_small_mean = mean(tvSB_small2)
gen byte tvSB_small = (tvSB_small_mean >= 0.5) if !missing(tvSB_small_mean)
drop tvSB_small2 tvSB_small_mean

* time-bin dummies
gen byte tvSB_pre33  = (year < 1933)
gen byte tvSB_y33    = (year == 1933)
gen byte tvSB_y34    = (year == 1934)
gen byte tvSB_post34 = (year > 1934)

* interactions (omit pre33 to be the baseline)
gen double tvSB_d_33     = d * tvSB_y33
gen double tvSB_d_34     = d * tvSB_y34
gen double tvSB_d_post34 = d * tvSB_post34

gen double tvSB_ds_33     = d * tvSB_small * tvSB_y33
gen double tvSB_ds_34     = d * tvSB_small * tvSB_y34
gen double tvSB_ds_post34 = d * tvSB_small * tvSB_post34

reghdfe var_inv_rate ///
    var_Q d c.d#c.tvSB_small ///
    tvSB_d_33 tvSB_d_34 tvSB_d_post34 ///
    tvSB_ds_33 tvSB_ds_34 tvSB_ds_post34, ///
    absorb(permno year) vce(cluster permno year)

* store bin coefficients (relative to pre33 baseline)
local b_sz_33     = _b[tvSB_d_33]
local b_sz_34     = _b[tvSB_d_34]
local b_sz_post34 = _b[tvSB_d_post34]

local g_sz_33     = _b[tvSB_ds_33]
local g_sz_34     = _b[tvSB_ds_34]
local g_sz_post34 = _b[tvSB_ds_post34]


/********************************************************
(2) RESTRICT TO d>0 ONLY FOR AGGREGATION (KEEP COEFS)
********************************************************/
preserve
keep if d > 0

*******************************************************
* Total investment within d>0 (but this is NOT using coefs)
*******************************************************
bys year: egen double dpos_sumk  = total(netppe)
bys year: egen double dpos_sumkL = total(Lnetppe_new)
gen double dpos_total_inv_rate = dpos_sumk/dpos_sumkL - 1

*******************************************************
* Baseline aggregation within d>0 using FULL-SAMPLE betas
*******************************************************
gen double dpos_dK_base = d * Lnetppe_new
bys year: egen double dpos_sum_dK_base = total(dpos_dK_base)
bys year: egen double dpos_sum_K_base  = total(Lnetppe_new)
gen double dpos_w_base = dpos_sum_dK_base / dpos_sum_K_base

gen double dpos_beta_base = .
replace dpos_beta_base = 0 if year == 1932
forvalues y = 1926/1940 {
    capture replace dpos_beta_base = `b_base_`y'' if year == `y'
}
gen double dpos_agg_base = dpos_beta_base * dpos_w_base


*******************************************************
* Rating aggregation within d>0 using FULL-SAMPLE betas
*******************************************************
gen double dpos_dK_all  = d * Lnetppe_new
gen double dpos_dK_low  = d * rating_ind * Lnetppe_new

bys year: egen double dpos_sum_dK_all = total(dpos_dK_all)
bys year: egen double dpos_sum_dK_low = total(dpos_dK_low)
bys year: egen double dpos_sum_K_all  = total(Lnetppe_new)

gen double dpos_w_all = dpos_sum_dK_all / dpos_sum_K_all
gen double dpos_w_low = dpos_sum_dK_low / dpos_sum_K_all

gen double dpos_beta_rat  = .
gen double dpos_gamma_rat = .
replace dpos_beta_rat  = 0 if year == 1932
replace dpos_gamma_rat = 0 if year == 1932

forvalues y = 1926/1940 {
    capture replace dpos_beta_rat  = `b_rat_`y'' if year == `y'
    capture replace dpos_gamma_rat = `g_rat_`y'' if year == `y'
}

gen double dpos_agg_rating = dpos_beta_rat*dpos_w_all + dpos_gamma_rat*dpos_w_low


*******************************************************
* Size-bin aggregation within d>0 using FULL-SAMPLE bin betas
*******************************************************
gen double dpos_dK_sz_all   = d * Lnetppe_new
gen double dpos_dK_sz_small = d * tvSB_small * Lnetppe_new

bys year: egen double dpos_sum_dK_sz_all   = total(dpos_dK_sz_all)
bys year: egen double dpos_sum_dK_sz_small = total(dpos_dK_sz_small)
bys year: egen double dpos_sum_K_sz_all    = total(Lnetppe_new)

gen double dpos_w_sz_all   = dpos_sum_dK_sz_all   / dpos_sum_K_sz_all
gen double dpos_w_sz_small = dpos_sum_dK_sz_small / dpos_sum_K_sz_all

gen double dpos_beta_sz  = 0
gen double dpos_gamma_sz = 0

replace dpos_beta_sz  = `b_sz_33'     if year == 1933
replace dpos_beta_sz  = `b_sz_34'     if year == 1934
replace dpos_beta_sz  = `b_sz_post34' if year >  1934

replace dpos_gamma_sz = `g_sz_33'     if year == 1933
replace dpos_gamma_sz = `g_sz_34'     if year == 1934
replace dpos_gamma_sz = `g_sz_post34' if year >  1934

gen double dpos_agg_size = dpos_beta_sz*dpos_w_sz_all + dpos_gamma_sz*dpos_w_sz_small


/********************************************************
(3) COLLAPSE TO YEAR AND BUILD THE SAME 3-COLUMN TABLE
********************************************************/

keep year dpos_total_inv_rate dpos_agg_base dpos_agg_rating dpos_agg_size
bys year: keep if _n==1
sort year

* locals for 1933, 1934, After (>=1935). Multiply by 100 for percent.
quietly summarize dpos_total_inv_rate if year == 1933
local T33 = r(mean)*100
quietly summarize dpos_total_inv_rate if year == 1934
local T34 = r(mean)*100
quietly summarize dpos_total_inv_rate if year >= 1935
local TA  = r(mean)*100

quietly summarize dpos_agg_base if year == 1933
local G33 = r(mean)*100
quietly summarize dpos_agg_base if year == 1934
local G34 = r(mean)*100
quietly summarize dpos_agg_base if year >= 1935
local GA  = r(mean)*100

quietly summarize dpos_agg_rating if year == 1933
local R33 = r(mean)*100
quietly summarize dpos_agg_rating if year == 1934
local R34 = r(mean)*100
quietly summarize dpos_agg_rating if year >= 1935
local RA  = r(mean)*100

quietly summarize dpos_agg_size if year == 1933
local S33 = r(mean)*100
quietly summarize dpos_agg_size if year == 1934
local S34 = r(mean)*100
quietly summarize dpos_agg_size if year >= 1935
local SA  = r(mean)*100

* print LaTeX rows only
display "Total net investment (\%)            & " string(`T33',"%6.2f") " & " string(`T34',"%6.2f") " & " string(`TA',"%6.2f") " \\\\"
display "Gold clause effect (\%)              & " string(`G33',"%6.2f") " & " string(`G34',"%6.2f") " & " string(`GA',"%6.2f") " \\\\"
display "Gold clause effect (\%) (rating)     & " string(`R33',"%6.2f") " & " string(`R34',"%6.2f") " & " string(`RA',"%6.2f") " \\\\"
display "Gold clause effect (\%) (size)       & " string(`S33',"%6.2f") " & " string(`S34',"%6.2f") " & " string(`SA',"%6.2f") " \\\\"

restore
