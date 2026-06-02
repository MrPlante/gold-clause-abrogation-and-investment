The goal of the file @Code/quarterly_div.py is to do a higher frequency analysis of the dividend response around the significant events related to the abrogation of the gold clause.

This analysis will use the data in @Data/monthly_div.dta.

Below is the message that my coauthor who generated the data (and the wrote the code for the annual analysis) sent me (with some of my comments in parentheses):

"
    Hi Sebastien, 

    Attached you will find a monthly dividend data set. (He is referring to the data in monthly_div.dta)  

    Let me first explain the annual variables: payout, cashrat, netrep. These are the dependent variables of regressions 1-3 in Table 5. They correspond to total payout, cash dividend, net repurchase divided by book common stock in 1930 or the earliest year available after 1930. Payout, cashrat, netrep are already winsorized by year using "winsor2 payout cashrat netrep, replace by(year) cuts(0.5 99.5)". If the common stock in the denominator is zero which happens in very few cases, these ratios are set to zero as well. If you drop duplicates by permno and year, results in columns 1-3 of Table 5 are obtained with the following regressions: 

    reghdfe payout var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
    reghdfe cashrat var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)
    reghdfe netrep var_Q d d_year_1926-d_year_1940, absorb(permno year) vce(cluster permno year)

    In the attached monthly data, you will find cashdiv and netissue at the monthly frequency. Annual cash dividends are the sum of monthly dividends, and annual net repurchase is the sum of negative net issuance every month. These are dollar amounts and are not winsorized. I also saved the variable "denom" which varies at the annual frequency and is the denominator (common stock) used when calculating the annual quantities.
    
    Attachment file type: unknown
    monthly_div.dta
    8.33 MB
"

The analysis should focus on cash dividend only. You should use share repurchases and total payout as dependent variables.

The code you use should be written in Python while implementing the Stata regression specified above. 


