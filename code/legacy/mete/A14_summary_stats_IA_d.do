set more off
display _newline(200)  
clear

* --- Load your data ---
cd "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

*******************************************************
* Three-panel Summary Statistics -> LaTeX (single file)
* Format: Variable | Firms N Mean SD 5% 25% 50% 75% 95%
*******************************************************
version 15


********************************************************************
********************************************************************
*d > 0 firms
********************************************************************
********************************************************************
preserve 
keep if d_orig > 0

* ---------- USER INPUTS ----------
* Overleaf-linked Dropbox folder
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cd "`OL'"
cap mkdir "Tables"
local outfile "Tables/tab_summary_d1_dorig.tex"

* Panel identifier used for "Firms"
local idvar permno

* Variables to report (extend vlist as needed)
* Variables to report (extend vlist as needed)
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
local vlist_AB `vbase' d_orig dind_orig d dind
local vlist_C  `vbase' d dind

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
label var dind_orig     "\ensuremath{I_{d>0}}"     
label var d			    "\ensuremath{\tilde{d}}"
label var dind          "\ensuremath{I_{\tilde{d}>0}}"

* Panel definitions
local pA_cond year>=1926 & year<=1932
local pB_cond year>=1933 & year<=1934
local pC_cond year>=1935 & year<=1940

* ---------- Write table header (no midrule here) ----------
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lrrrrrrrrr}" _n ///
"\toprule" _n ///
"Variable & Firms & N & Mean & SD & 5\% & 25\% & 50\% & 75\% & 95\% \\" _n
file close `fh'

*******************************************************
* Helper: append one panel (centered header + midrules)
*******************************************************
capture program drop _append_panel
program define _append_panel
    // args: panel_title , condition , idvar , vlist , outfile
    args panel_title cond idvar vlist outfile

    * Panel header: centered, with \midrule above & below
    tempname fh
    file open `fh' using "`outfile'", write append text
    file write `fh' ///
        "\midrule" _n ///
        "\multicolumn{10}{c}{\textit{`panel_title'}} \\" _n ///
        "\midrule" _n
    file close `fh'

    * Mark panel observations
    tempvar use tag
    gen byte `use' = (`cond')

    * Firms = distinct idvar among panel obs
    egen byte `tag' = tag(`idvar') if `use'
    quietly count if `tag'
    scalar __Firms = r(N)

    * Loop variables and print rows
    foreach v of local vlist {
        * Row label from variable label (fallback to name)
        local row = "`: variable label `v''"
        if `"`row'"' == "" local row "`v'"

        * ---- SAFE MATH LABELS ($ ... $) & basic escaping ----
        * escape % in label
        local row = subinstr(`"`row'"', "%", "\\%", .)
        * temporarily replace $ with a placeholder so Stata won't treat $... as globals
        local row_safe = subinstr(`"`row'"', "$", "{DOLLAR}", .)
        * (optional) if your labels include raw &_# outside math, you can also do:
        * local row_safe = subinstr("`row_safe'","&","\&",.)
        * local row_safe = subinstr("`row_safe'","_","\_",.)

        quietly count if `use' & !missing(`v')
        local N = r(N)

        quietly summarize `v' if `use', detail

        * Format numbers: Firms/N with commas; stats 2 decimals
        local sFirms = string(__Firms,"%9.0gc")
        local sN     = string(`N',  "%9.0gc")
        local sMean  = string(r(mean),"%9.2f")
        local sSD    = string(r(sd),  "%9.2f")
        local sP5    = string(r(p5),  "%9.2f")
        local sP25   = string(r(p25), "%9.2f")
        local sP50   = string(r(p50), "%9.2f")
        local sP75   = string(r(p75), "%9.2f")
        local sP95   = string(r(p95), "%9.2f")

        tempname fh2
        file open `fh2' using "`outfile'", write append text
        * Substitute safely before writing (avoids Stata interpreting label text)
local row_print = subinstr("`row_safe'","{DOLLAR}",char(36),.)

file write `fh2' ///
    `"`row_print'"' " & " ///
    "`sFirms'" " & " ///
    "`sN'"     " & " ///
    "`sMean'"  " & " ///
    "`sSD'"    " & " ///
    "`sP5'"    " & " ///
    "`sP25'"   " & " ///
    "`sP50'"   " & " ///
    "`sP75'"   " & " ///
    "`sP95'"   " \\" _n

        file close `fh2'
    }
end

*******************************************************
* Append three panels
*******************************************************
quietly _append_panel "Panel A: 1926--1932" "`pA_cond'" `idvar' "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel B: 1933--1934" "`pB_cond'" `idvar' "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel C: 1935--1940" "`pC_cond'" `idvar' "`vlist_C'"  "`outfile'"
*******************************************************
* Close table
*******************************************************
tempname fhZ
file open `fhZ' using "`outfile'", write append text
file write `fhZ' "\bottomrule\end{tabular}\end{threeparttable}" _n
file close `fhZ'

display as res "Wrote -> `outfile'"

restore

********************************************************************
********************************************************************
*d == 0 firms
********************************************************************
********************************************************************
preserve 
keep if d_orig == 0

* ---------- USER INPUTS ----------
* Overleaf-linked Dropbox folder
local OL "C:\Users\mete_\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cd "`OL'"
cap mkdir "Tables"
local outfile "Tables/tab_summary_d0_dorig.tex"

* Panel identifier used for "Firms"
local idvar permno

* Variables to report (extend vlist as needed)
* Variables to report (extend vlist as needed)
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
local vlist_AB `vbase' d_orig dind_orig d dind
local vlist_C  `vbase' d dind

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
label var dind_orig     "\ensuremath{I_{d>0}}"     
label var d			    "\ensuremath{\tilde{d}}"
label var dind          "\ensuremath{I_{\tilde{d}>0}}"

* Panel definitions
local pA_cond year>=1926 & year<=1932
local pB_cond year>=1933 & year<=1934
local pC_cond year>=1935 & year<=1940

* ---------- Write table header (no midrule here) ----------
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lrrrrrrrrr}" _n ///
"\toprule" _n ///
"Variable & Firms & N & Mean & SD & 5\% & 25\% & 50\% & 75\% & 95\% \\" _n
file close `fh'

*******************************************************
* Helper: append one panel (centered header + midrules)
*******************************************************
capture program drop _append_panel
program define _append_panel
    // args: panel_title , condition , idvar , vlist , outfile
    args panel_title cond idvar vlist outfile

    * Panel header: centered, with \midrule above & below
    tempname fh
    file open `fh' using "`outfile'", write append text
    file write `fh' ///
        "\midrule" _n ///
        "\multicolumn{10}{c}{\textit{`panel_title'}} \\" _n ///
        "\midrule" _n
    file close `fh'

    * Mark panel observations
    tempvar use tag
    gen byte `use' = (`cond')

    * Firms = distinct idvar among panel obs
    egen byte `tag' = tag(`idvar') if `use'
    quietly count if `tag'
    scalar __Firms = r(N)

    * Loop variables and print rows
    foreach v of local vlist {
        * Row label from variable label (fallback to name)
        local row = "`: variable label `v''"
        if `"`row'"' == "" local row "`v'"

        * ---- SAFE MATH LABELS ($ ... $) & basic escaping ----
        * escape % in label
        local row = subinstr(`"`row'"', "%", "\\%", .)
        * temporarily replace $ with a placeholder so Stata won't treat $... as globals
        local row_safe = subinstr(`"`row'"', "$", "{DOLLAR}", .)
        * (optional) if your labels include raw &_# outside math, you can also do:
        * local row_safe = subinstr("`row_safe'","&","\&",.)
        * local row_safe = subinstr("`row_safe'","_","\_",.)

        quietly count if `use' & !missing(`v')
        local N = r(N)

        quietly summarize `v' if `use', detail

        * Format numbers: Firms/N with commas; stats 2 decimals
        local sFirms = string(__Firms,"%9.0gc")
        local sN     = string(`N',  "%9.0gc")
        local sMean  = string(r(mean),"%9.2f")
        local sSD    = string(r(sd),  "%9.2f")
        local sP5    = string(r(p5),  "%9.2f")
        local sP25   = string(r(p25), "%9.2f")
        local sP50   = string(r(p50), "%9.2f")
        local sP75   = string(r(p75), "%9.2f")
        local sP95   = string(r(p95), "%9.2f")

        tempname fh2
        file open `fh2' using "`outfile'", write append text
        * Substitute safely before writing (avoids Stata interpreting label text)
local row_print = subinstr("`row_safe'","{DOLLAR}",char(36),.)

file write `fh2' ///
    `"`row_print'"' " & " ///
    "`sFirms'" " & " ///
    "`sN'"     " & " ///
    "`sMean'"  " & " ///
    "`sSD'"    " & " ///
    "`sP5'"    " & " ///
    "`sP25'"   " & " ///
    "`sP50'"   " & " ///
    "`sP75'"   " & " ///
    "`sP95'"   " \\" _n

        file close `fh2'
    }
end

*******************************************************
* Append three panels
*******************************************************
quietly _append_panel "Panel A: 1926--1932" "`pA_cond'" `idvar' "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel B: 1933--1934" "`pB_cond'" `idvar' "`vlist_AB'" "`outfile'"
quietly _append_panel "Panel C: 1935--1940" "`pC_cond'" `idvar' "`vlist_C'"  "`outfile'"
*******************************************************
* Close table
*******************************************************
tempname fhZ
file open `fhZ' using "`outfile'", write append text
file write `fhZ' "\bottomrule\end{tabular}\end{threeparttable}" _n
file close `fhZ'

display as res "Wrote -> `outfile'"

restore