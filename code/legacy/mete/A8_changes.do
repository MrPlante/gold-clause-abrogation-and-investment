set more off
display _newline(200)  
clear

* Load data
cd "I:\KP Financial Dropbox\Mete Kilic\GKP Analysis Oct 2025 Mete\Data"
use A4_merged.dta, clear

xtset permno year
foreach v of varlist var_* {
	gen d_`v' = `v' - L4.`v' if year == 1930
    replace d_`v' = L.d_`v' if year == 1931      // do it based on the constant d after 1930?
}

* ---- Keep only 1931 rows (where the change variables live) ----
keep if year==1931

* ---- Overleaf output (absolute path) ----
local OL "I:\KP Financial Dropbox\Mete Kilic\Apps\Overleaf\Leverage Risk 2025 - Oct 2025"
cap mkdir "`OL'\Tables"
local outfile "`OL'\Tables\tab_changes_1926_1930.tex"

* ---- CHANGE VARIABLES (edit this list to your names) ----
* Example names assuming you created: d_var_* = var - L4.var at year==1930
local ylist d_var_inv_rate ///
d_var_Q ///
d_var_logasset ///
d_var_netinc ///
d_var_cash ///
d_var_payout ///
d_var_booklev ///
d_var_marketlev ///
d_var_logltl ///
d_var_cbltl ///
d_var_psltl /// 
d_var_bdltl 

* Labels
label var d_var_inv_rate  "Net investment"
label var d_var_Q		  "Tobin's Q"
label var d_var_logasset  "log(Assets)"
label var d_var_netinc    "Net income/assets"
label var d_var_cash      "Cash/assets"
label var d_var_payout    "Payout/common stock"
label var d_var_booklev   "Book leverage"
label var d_var_marketlev "Market leverage"
label var d_var_logltl    "log(LTL)"
label var d_var_cbltl     "Corp. bonds/LTL"
label var d_var_psltl     "Pref. share/LTL"
label var d_var_bdltl     "Bank debt/LTL"          

* ---- Sanity check: variables exist ----
foreach v of local ylist {
    capture confirm variable `v'
    if _rc {
        di as error "Variable not found: `v'"
        exit 198
    }
}
capture confirm variable dind
if _rc {
    di as error "Indicator variable dind not found"
    exit 198
}

* ---- Write LaTeX header ----
tempname fh
file open `fh' using "`outfile'", write replace text
file write `fh' ///
"\begin{threeparttable}" _n ///
"\begin{tabular}{lrrrrr}" _n ///
"\toprule" _n ///
"Variable & \ensuremath{d=0} & \ensuremath{d>0} & p-val. & Coef. on \ensuremath{d} & p-val. \\" _n ///
"\midrule" _n
file close `fh'

* ---- Build table rows ----
foreach v of local ylist {
    * Row label
    local row = "`: variable label `v''"
    if `"`row'"' == "" local row "`v'"
    local row = subinstr(`"`row'"', "%", "\\%", .)
    local row = subinstr(`"`row'"', "&", "\\&", .)

    * t-test by dind: means and p-value of difference
    capture ttest `v', by(dind)
    if _rc==0 {
        local m0 = r(mu_1)   // dind==0
        local m1 = r(mu_2)   // dind==1
        local ptt = r(p)
    }
    else {
        local m0 = .
        local m1 = .
        local ptt = .
    }

    * OLS: `v' on dind → coefficient and p-value
    capture regress `v' d
    if _rc==0 {
        local b = _b[d]
        local t = _b[d]/_se[d]
        local p = 2*ttail(e(df_r), abs(`t'))
    }
    else {
        local b = .
        local p = .
    }

    * Format
    local s0 = string(`m0', "%9.2f")
    local s1 = string(`m1', "%9.2f")
    local sp = string(`ptt',"%9.2f")
    local sb = string(`b',  "%9.2f")
    local spb= string(`p',  "%9.2f")

    * Write row
    tempname fh2
    file open `fh2' using "`outfile'", write append text
    file write `fh2' "`row' & `s0' & `s1' & `sp' & `sb' & `spb' \\" _n
    file close `fh2'
}

* ---- Footer ----
tempname fhz
file open `fhz' using "`outfile'", write append text
file write `fhz' "\bottomrule\end{tabular}\end{threeparttable}" _n
file close `fhz'

di as res "Wrote -> `outfile'"
