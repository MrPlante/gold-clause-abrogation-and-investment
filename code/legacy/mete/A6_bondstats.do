set more off
display _newline(200)  
clear

* --- Load your data ---
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

keep if year >= 1930 & year <= 1935 
replace fd_amount = 0 if fd_amount == . 
replace fd_amount_g0 = 0 if fd_amount_g0 == . 
replace fd_amount_g1 = 0 if fd_amount_g1 == . 

*Sample of firms with bonds in 1930 & still in the data in 1935 
*gen bond_1930  = (fd_amount_g1 > 0 & ll_bs_new > 0) if year == 1930 
gen bond_1930  = (fd_amount > 0) if year == 1930 

xtset permno year 
tsfill
order permno year 

gen there_1935 = (inv_rate != .) if year == 1935 

bys permno: egen ind_bond_1930  = mean(bond_1930)
bys permno: egen ind_there_1935 = mean(there_1935)

keep if ind_bond_1930 == 1 & ind_there_1935 == 1

drop if fd_amount == 0 | fd_amount == . 

drop _merge
merge 1:m permno year using A1_bond_data_bondlevel.dta
drop if inv_rate == .

*Year-specific d at the firm level
gen d_year = fd_amount_g1/ll_bs_new
replace d_year = 1 if d_year > 1
replace d_year = 0 if ll_bs_new == 0 

*#bonds in a year 
gen num_bonds = .
forvalues xx = 1930(1)1935{
	sum Amount if year == `xx'
	replace num_bonds = `r(N)' if year == `xx'
}
gen num_bonds_g1 = .
forvalues xx = 1930(1)1935{
	sum Amount if year == `xx' & gold_ind == 1
	replace num_bonds_g1 = `r(N)' if year == `xx'
}

gen gold_ratio = num_bonds_g1/num_bonds
drop d_1*

*drop if permno == 15149 | permno==17734 | permno ==24512 | permno == 25435

duplicates drop permno year, force

*Table 
*******************************************************
* Year table -> LaTeX (Overleaf)
* Columns:
* Year | # Firms | # Firms with d_year>0 | # Bonds | % gold bonds
*      | Mean d_year | Median d_year | Corr with d_1930
*******************************************************
version 15
set more off

* ---------- USER INPUTS (EDIT THESE) ----------
* 1) Overleaf-linked Dropbox project folder
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"

* 2) Variable names for bonds and % gold bonds (same across permnos within a year)
*    Example guesses — change to your actual variable names:
local nbonds_var   num_bonds        // "# Bonds" per year
local pgold_var    gold_ratio     // "% gold bonds" per year

* 3) Is % gold stored as a fraction (0–1) or percent (0–100)?
local pgold_is_fraction 1             // set to 0 if already 0–100

* Build baseline d_1930 per permno (to use in correlations)
gen double _d1930_tmp = d_year if year==1930
bysort permno: egen double d_1930 = max(_d1930_tmp)
drop _d1930_tmp

* Get list of years (or hardcode: local ylist 1930 1931 1932 1933 1934 1935)
levelsof year, local(ylist)

* ---------- Output path ----------
cd "`OL'"
cap mkdir "Tables"
local outfile "Tables/tab_bonds_1930_1935.tex"

* ---------- Write LaTeX header (with midrule) ----------
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lccccccc}" _n ///
"\toprule" _n ///
"Year & \# Firms & \# Firms with \ensuremath{d_t>0} & \# Bonds & \% gold bonds & Mean \ensuremath{d_t} & Median \ensuremath{d_t} & Corr with \ensuremath{d_{1930}} \\" _n ///
"\midrule" _n
file close `fh'

* ---------- Build rows year by year ----------
foreach y of local ylist {
    preserve
        keep if year==`y'

        * # Firms (distinct permno)
        tempvar tag
        bysort permno: gen byte `tag' = (_n==1)
        quietly count if `tag'
        local nfirms = r(N)

        * # Firms with d_year > 0
        quietly count if d_year>0 & !missing(d_year)
        local npos = r(N)

        * Mean / Median of d_year
        quietly summarize d_year, detail
        local mean = r(mean)
        local med  = r(p50)

        * Corr(d_year, d_1930) across firms in this year
        * (no extra qualifiers; corr drops missings pairwise)
        capture corr d_year d_1930
        if _rc==0 {
            matrix C = r(C)
            local rho = C[1,2]
        }
        else local rho = .

        * Per-year totals
        quietly summarize `nbonds_var'
        local nbonds = r(mean)

        quietly summarize `pgold_var'
        local pgold = r(mean)
        if `pgold_is_fraction' & !missing(`pgold') local pgold = 100*`pgold'

        * Format strings
        local sYear  = "`y'"
        local sNFirm = string(`nfirms', "%9.0gc")
        local sNPos  = string(`npos',   "%9.0gc")
        local sBond  = string(`nbonds', "%9.0gc")
        local sPGold = string(`pgold',  "%9.2f")
        local sMean  = string(`mean',   "%9.2f")
        local sMed   = string(`med',    "%9.2f")
        local sCorr  = string(`rho',    "%9.2f")

        * Write one row
        tempname fh2
        file open `fh2' using "`outfile'", write append text
        file write `fh2' "`sYear' & `sNFirm' & `sNPos' & `sBond' & `sPGold' & `sMean' & `sMed' & `sCorr' \\" _n
        file close `fh2'
    restore
}

* ---------- Close table ----------
tempname fhz
file open `fhz' using "`outfile'", write append text
file write `fhz' "\bottomrule\end{tabular}\end{threeparttable}" _n
file close `fhz'

display as res "Wrote -> `outfile'"







