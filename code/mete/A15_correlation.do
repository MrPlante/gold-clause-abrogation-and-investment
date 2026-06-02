*******************************************************
* Correlations with d: 1926–1932 and 1932
* ρ from correlate; p-val from regress (equivalent test)
*******************************************************
version 16
set more off
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

* Ensure labels (as you specified)
label var var_Q         "Tobin's Q"
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

* Variable order exactly as requested
local vlist ///
    var_Q var_logasset var_netinc var_cash var_payout ///
    var_booklev var_marketlev var_logltl var_cbltl var_psltl var_bdltl

* Output path (Overleaf)
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_corr.tex"

* Open LaTeX file
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lcc}" _n ///
"\toprule" _n ///
" & 1926--1932 & 1932 \\" _n ///
"\midrule" _n

foreach v of local vlist {

    * Label (fallback to name) and escape % and _
    local row : variable label `v'
    if "`row'"=="" local row "`v'"
    local row = subinstr(`"`row'"', "%", "\\%", .)
    local row = subinstr(`"`row'"', "_", "\\_", .)

    * Defaults
    local sRhoA "--"
    local sPA   "--"
    local sRhoB "--"
    local sPB   "--"

    * -------- 1926–1932 --------
    capture noisily correlate `v' d if inrange(year,1926,1932)
    if (_rc==0) {
        matrix C = r(C)
        scalar rhoA = C[1,2]
        if (rhoA<.) local sRhoA : display %6.3f rhoA

        * p-value via equivalent simple regression
        quietly regress `v' d if inrange(year,1926,1932)
        test d
        scalar pA = r(p)
        if (pA<.) local sPA : display %6.4f pA
    }

    * -------- 1932 only --------
    capture noisily correlate `v' d if year==1932
    if (_rc==0) {
        matrix C = r(C)
        scalar rhoB = C[1,2]
        if (rhoB<.) local sRhoB : display %6.3f rhoB

        quietly regress `v' d if year==1932
        test d
        scalar pB = r(p)
        if (pB<.) local sPB : display %6.4f pB
    }

    * Write two lines: ρ and (p)
    file write `fh' `"`row'"' " & `sRhoA' & `sRhoB' \\" _n
    file write `fh' " & (`sPA') & (`sPB') \\" _n
}

file write `fh' "\bottomrule" _n "\end{tabular}\end{threeparttable}" _n
file close `fh'

display as res "Wrote -> `outfile'"
