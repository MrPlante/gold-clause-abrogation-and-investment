set more off
display _newline(200)  
clear

*******************************************************
* Table: Average characteristics for d=0 and d>0 firms
* Columns: Variable | d=0 | d>0 | p-value
* Panels: 1926–1932, 1933–1934, 1935–1940
*******************************************************
version 15
set more off



* ---------- USER INPUTS ----------
* Overleaf-linked Dropbox folder
* Path to your Overleaf project
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"

* Ensure the Tables subfolder exists
cap mkdir "`OL'\Tables"

* Define the full output path (absolute, not relative)
local outfile "`OL'\Tables\tab_d_groups_dorig.tex"

* Load data
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

* Panel definitions
local pA year>=1926 & year<=1932
local pB year>=1933 & year<=1934
local pC year>=1935 & year<=1940

* Variables to report (extend as needed)
local vbase var_inv_rate ///
var_Q ///
var_logasset ///
var_netinc ///
var_cash ///
var_payout ///
var_booklev ///
var_marketlev ///
var_logltl ///
var_cbltl ///
var_psltl ///
var_bdltl

* Panel-specific lists
local vlist_AB `vbase' d_orig d 
local vlist_C  `vbase' d 

* Labels
label var var_inv_rate  "Net investment"
label var var_Q		    "Tobin's Q"
label var var_logasset  "log(Assets)"
label var var_netinc    "Net income/assets"
label var var_cash      "Cash/assets"
label var var_payout    "Payout/common stock"
label var var_booklev   "Book leverage"
label var var_marketlev "Market leverage"
label var var_logltl    "log(LTL)"
label var var_cbltl     "Corp. bonds/LTL"
label var var_psltl     "Pref. share/LTL"
label var var_bdltl     "Bank debt/LTL"  
label var d_orig	    "\ensuremath{d}"        
label var d			    "\ensuremath{\tilde{d}}"

* ---------- Write LaTeX header ----------
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lrrr}" _n ///
"\toprule" _n ///
"Variable & \ensuremath{d=0} & \ensuremath{d>0} & p-val. \\" _n 
file close `fh'

*******************************************************
* Helper: append one panel
*******************************************************
capture program drop _append_panel
program define _append_panel
    // args: panel_title , condition , vlist , outfile
    args title cond vlist outfile

    * Panel header
    tempname fh
    file open `fh' using "`outfile'", write append text
    file write `fh' "\midrule" _n ///
                     "\multicolumn{4}{c}{\textit{`title'}} \\" _n ///
                     "\midrule" _n
    file close `fh'

    preserve
        keep if `cond'

        foreach v of local vlist {
            local row = "`: variable label `v''"
            if `"`row'"' == "" local row "`v'"
            local row = subinstr(`"`row'"', "%", "\\%", .)
            local row = subinstr(`"`row'"', "&", "\\&", .)

            * Means by group
            quietly summarize `v' if dind_orig==0, meanonly
            if r(N)>0 local m0 = r(mean)
            else local m0 = .

            quietly summarize `v' if dind_orig==1, meanonly
            if r(N)>0 local m1 = r(mean)
            else local m1 = .

            * t-test using existing indicator
            capture ttest `v', by(dind_orig) uneq
            if _rc==0 local p = r(p)
            else local p = .

            * Format and write row
            local s0 = string(`m0', "%9.2f")
            local s1 = string(`m1', "%9.2f")
            local sp = string(`p' , "%9.2f")

            tempname fh2
            file open `fh2' using "`outfile'", write append text
            file write `fh2' "`row' & `s0' & `s1' & `sp' \\" _n
            file close `fh2'
        }
    restore
end

*******************************************************
* Run for three panels
*******************************************************
/*
quietly _append_panel "Panel A: 1926--1932" "`pA'" "`vlist'" "`outfile'"
quietly _append_panel "Panel B: 1933--1934" "`pB'" "`vlist'" "`outfile'"
quietly _append_panel "Panel C: 1935--1940" "`pC'" "`vlist'" "`outfile'"



quietly _append_panel "Panel A: 1926--1932" "`pA_cond'" `idvar' "`vlist'" "`outfile'"
quietly _append_panel "Panel B: 1933--1934" "`pB_cond'" `idvar' "`vlist'" "`outfile'"
quietly _append_panel "Panel C: 1935--1940" "`pC_cond'" `idvar' "`vlist'" "`outfile'"
*/
quietly _append_panel "Panel A: 1926--1932" "`pA'" "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel B: 1933--1934" "`pB'" "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel C: 1935--1940" "`pC'" "`vlist_C'"  "`outfile'"

*******************************************************
* Close table
*******************************************************
tempname fhZ
file open `fhZ' using "`outfile'", write append text
file write `fhZ' "\bottomrule\end{tabular}\end{threeparttable}" _n
file close `fhZ'

display as res "Wrote -> `outfile'"