set more off
display _newline(200)  
clear

version 16
set more off
clear all

* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

*Total investment rate 
bys year: egen sumk = sum(netppe)
gen Lnetppe_new = netppe/(1+var_inv_rate)
bys year: egen Lsumk = sum(Lnetppe_new)
gen total_inv_rate = sumk/Lsumk - 1

*Panel A: All firms
*Total net investment in %
sum total_inv_rate if year == 1933 
sum total_inv_rate if year == 1934 
sum total_inv_rate if year >= 1935 

*Gold clause effect in %
reghdfe var_inv_rate var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
*******************************************************
* Aggregate investment from TIME-VARYING effect of d only
* (relative to omitted year 1932)
*******************************************************

* 1) Capital-weighted exposure term: sum_j d_jt*K_{j,t-1} / sum_j K_{j,t-1}
gen double dKlag = d * Lnetppe_new

bysort year: egen double sum_dKlag = total(dKlag)
bysort year: egen double sum_Klag  = total(Lnetppe_new)

gen double w_d = sum_dKlag / sum_Klag

* 2) Time-varying coefficient component beta_t:
*    = _b[d_year_t] when it exists; = 0 in 1932 (omitted); missing if dropped
gen double beta_tv = .
replace beta_tv = 0 if year == 1932

forvalues y = 1926/1940 {
    capture replace beta_tv = _b[d_year_`y'] if year == `y'
    * if coefficient doesn't exist (dropped), capture fails and beta_tv stays missing
}

* 3) Aggregate investment attributable to TIME-VARYING effect only
gen double agg_inv_d_tv = beta_tv * w_d


*Gold clause effect in % (with rating)
*Demean d
sum d if d > 0, d
*replace d = d - `r(mean)'

replace d_Low  = d*rating_ind

forvalues xx = 1926(1)1940{
replace d_year_`xx' = d*year_`xx'
}

forvalues xx = 1926(1)1940{
replace d_year_`xx'_Low = d*year_`xx'*rating_ind
}

drop d_year_1932_Low
drop year_1932_Low


*******************************************************
* Aggregate investment from TIME-VARYING effects with Low split
* Uses UNIQUE variable names (prefix: tvR_)
* Omitted year: 1932 => set beta and gamma to 0 in 1932
*******************************************************

* (A) Capital-weighted exposure terms (overall denom = sum K_{t-1})
gen double tvR_dK          = d * Lnetppe_new
gen double tvR_dK_Low      = d * rating_ind * Lnetppe_new

bysort year: egen double tvR_sum_dK      = total(tvR_dK)
bysort year: egen double tvR_sum_dK_Low  = total(tvR_dK_Low)
bysort year: egen double tvR_sum_K       = total(Lnetppe_new)

gen double tvR_w_d     = tvR_sum_dK     / tvR_sum_K
gen double tvR_w_dLow  = tvR_sum_dK_Low / tvR_sum_K

* (B) Time-varying coefficients: beta_t (base) and gamma_t (Low increment)
gen double tvR_beta  = .
gen double tvR_gamma = .

replace tvR_beta  = 0 if year == 1932
replace tvR_gamma = 0 if year == 1932

reghdfe var_inv_rate ///
    var_Q d d_Low d_year_1926-d_year_1940 year_1926_Low-year_1940_Low d_year_1926_Low-d_year_1940_Low, ///
    absorb(permno year) vce(cluster permno year)


forvalues y = 1926/1940 {
    capture replace tvR_beta  = _b[d_year_`y']     if year == `y'
    capture replace tvR_gamma = _b[d_year_`y'_Low] if year == `y'
}

* (C) Aggregate investment attributable to TIME-VARYING effects only
* High path: beta_t; Low path: beta_t + gamma_t
gen double tvR_agg_inv_tv = tvR_beta*tvR_w_d + tvR_gamma*tvR_w_dLow

bys year: sum tvR_agg_inv_tv

*******************************************************
* SIZE (Small) with 4 time bins: <1933, 1933, 1934, >1934
* Produces tvSB_agg_inv (yearly series) where "After" effect
* comes directly from the estimated >1934 coefficient.
*******************************************************

* --- define min year correctly ---
quietly summarize year, meanonly
local tvSB_min_year = r(min)

* --- define small based on median var_logasset in min year among d>0 ---
quietly summarize var_logasset if year == `tvSB_min_year' & d > 0, detail
local tvSB_p50 = r(p50)

gen byte tvSB_small2 = (var_logasset < `tvSB_p50') if !missing(var_logasset)
bys permno: egen double tvSB_small_mean = mean(tvSB_small2)
gen byte tvSB_small = (tvSB_small_mean >= 0.5) if !missing(tvSB_small_mean)
drop tvSB_small2 tvSB_small_mean

* --- time-bin dummies ---
gen byte tvSB_pre33   = (year < 1933)
gen byte tvSB_y33     = (year == 1933)
gen byte tvSB_y34     = (year == 1934)
gen byte tvSB_post34  = (year > 1934)

* sanity: exactly one bin per obs (optional)
* assert tvSB_pre33 + tvSB_y33 + tvSB_y34 + tvSB_post34 == 1

* --- interactions: d with bins; and (d*small) with bins ---
gen double tvSB_d_pre33   = d * tvSB_pre33
gen double tvSB_d_33      = d * tvSB_y33
gen double tvSB_d_34      = d * tvSB_y34
gen double tvSB_d_post34  = d * tvSB_post34

gen double tvSB_ds_pre33   = d * tvSB_small * tvSB_pre33
gen double tvSB_ds_33      = d * tvSB_small * tvSB_y33
gen double tvSB_ds_34      = d * tvSB_small * tvSB_y34
gen double tvSB_ds_post34  = d * tvSB_small * tvSB_post34

*******************************************************
* Regression:
* - Keep "d" and "d*small" (your unconditional components)
* - Include 4-bin interactions EXCEPT omit one bin as baseline.
*   Choose <1933 as baseline, so coefficients are directly:
*     beta_33, beta_34, beta_post34  (relative to <1933)
*   and similarly gamma_33, gamma_34, gamma_post34 for small increment.
*******************************************************

reghdfe var_inv_rate ///
    var_Q d ///
    c.d#c.tvSB_small ///
    tvSB_d_33 tvSB_d_34 tvSB_d_post34 ///
    tvSB_ds_33 tvSB_ds_34 tvSB_ds_post34, ///
    absorb(permno year) vce(cluster permno year)

*******************************************************
* Aggregate investment attributable to TIME-BIN effects only
* (relative to <1933 baseline), economy-weighted each year.
*******************************************************

* weights each year (same as before)
gen double tvSB_dK_all    = d * Lnetppe_new
gen double tvSB_dK_small  = d * tvSB_small * Lnetppe_new

bysort year: egen double tvSB_sum_dK_all    = total(tvSB_dK_all)
bysort year: egen double tvSB_sum_dK_small  = total(tvSB_dK_small)
bysort year: egen double tvSB_sum_K_all     = total(Lnetppe_new)

gen double tvSB_w_all   = tvSB_sum_dK_all   / tvSB_sum_K_all
gen double tvSB_w_small = tvSB_sum_dK_small / tvSB_sum_K_all

* assign bin-level coefficients to each year
gen double tvSB_beta_bin  = 0   // base effect relative to <1933
gen double tvSB_gamma_bin = 0   // small increment relative to <1933

replace tvSB_beta_bin  = _b[tvSB_d_33]     if year == 1933
replace tvSB_beta_bin  = _b[tvSB_d_34]     if year == 1934
replace tvSB_beta_bin  = _b[tvSB_d_post34] if year >  1934

replace tvSB_gamma_bin = _b[tvSB_ds_33]     if year == 1933
replace tvSB_gamma_bin = _b[tvSB_ds_34]     if year == 1934
replace tvSB_gamma_bin = _b[tvSB_ds_post34] if year >  1934

* aggregate contribution from bin effects only
gen double tvSB_agg_inv = tvSB_beta_bin*tvSB_w_all + tvSB_gamma_bin*tvSB_w_small

* quick summaries (your three columns)
bys year: egen double tvS_agg_inv_year = mean(tvSB_agg_inv)   // constant within year
sum tvS_agg_inv_year if year == 1933
sum tvS_agg_inv_year if year == 1934
sum tvS_agg_inv_year if year >  1934

*******************************************************
* Collapse to year-level series needed for the table
*******************************************************

preserve

* Keep only variables we need
keep year total_inv_rate agg_inv_d_tv tvR_agg_inv_tv tvS_agg_inv_year

* Keep one observation per year
bys year: keep if _n == 1
sort year

*******************************************************
* Column values: 1933, 1934, After (year >= 1935)
*******************************************************

* ---------- Total net investment ----------
quietly summarize total_inv_rate if year == 1933
local T_1933 = r(mean)*100

quietly summarize total_inv_rate if year == 1934
local T_1934 = r(mean)*100

quietly summarize total_inv_rate if year >= 1935
local T_after = r(mean)*100


* ---------- Gold clause effect (baseline) ----------
quietly summarize agg_inv_d_tv if year == 1933
local G_1933 = r(mean)*100

quietly summarize agg_inv_d_tv if year == 1934
local G_1934 = r(mean)*100

quietly summarize agg_inv_d_tv if year >= 1935
local G_after = r(mean)*100


* ---------- Gold clause effect (with rating) ----------
quietly summarize tvR_agg_inv_tv if year == 1933
local GR_1933 = r(mean)*100

quietly summarize tvR_agg_inv_tv if year == 1934
local GR_1934 = r(mean)*100

quietly summarize tvR_agg_inv_tv if year >= 1935
local GR_after = r(mean)*100


* ---------- Gold clause effect (with size) ----------
quietly summarize tvS_agg_inv_year if year == 1933
local GS_1933 = r(mean)*100

quietly summarize tvS_agg_inv_year if year == 1934
local GS_1934 = r(mean)*100

quietly summarize tvS_agg_inv_year if year >= 1935
local GS_after = r(mean)*100

*******************************************************
* Display table
*******************************************************

display as text "--------------------------------------------------------------"
display as text "Aggregate Investment Effects (Percent)"
display as text "--------------------------------------------------------------"
display as text "                           1933     1934     After"
display as text "--------------------------------------------------------------"

display as text "Total net investment (%)        " ///
    %6.2f `T_1933' "  " %6.2f `T_1934' "  " %6.2f `T_after'

display as text "Gold clause effect (%)           " ///
    %6.2f `G_1933' "  " %6.2f `G_1934' "  " %6.2f `G_after'

display as text "Gold clause effect (%) (rating)  " ///
    %6.2f `GR_1933' "  " %6.2f `GR_1934' "  " %6.2f `GR_after'

display as text "Gold clause effect (%) (size)    " ///
    %6.2f `GS_1933' "  " %6.2f `GS_1934' "  " %6.2f `GS_after'

display as text "--------------------------------------------------------------"


