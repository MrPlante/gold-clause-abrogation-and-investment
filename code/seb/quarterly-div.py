"""
Quarterly dividend analysis around gold clause events.

Runs four separate annual regressions (same spec as Table 5), each using
data from a different quarter of the year. This tests whether seasonal
patterns drive the results.

Regression specification (same for all four):
    cashrat_q ~ var_Q + d + d_year_* | permno_id + year_int
    cluster(permno_id)

Each regression: Q1 uses only Q1 firm-years, Q2 only Q2, etc.
Reference year: 1932.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*ChainedAssignment.*")
warnings.filterwarnings("ignore", message=".*DataFrame is highly fragmented.*")

import pandas as pd
import numpy as np
import pyfixest as pf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

DATA_PATH = "data/monthly_div.dta"
OUTPUT_DIR = "code/seb"

OMITTED_YEAR = 1932
WINSOR_CUTS = (0.005, 0.995)

QUARTER_MIDPOINTS = {1: 2, 2: 5, 3: 8, 4: 11}

def stars(p):
    if np.isnan(p):
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def stars_tex(p):
    """LaTeX superscript stars for regression tables."""
    if np.isnan(p):
        return ""
    return "\\sym{***}" if p < 0.01 else "\\sym{**}" if p < 0.05 else "\\sym{*}" if p < 0.1 else ""


def yq_to_date(yq):
    y, q = divmod(yq, 10)
    return datetime(y, QUARTER_MIDPOINTS[q], 15)


def yq_label(yq):
    y, q = divmod(yq, 10)
    return f"{y}Q{q}"


# ═════════════════════════════════════════════════════════════════════════════
# 1. Load data and build quarterly panel
# ═════════════════════════════════════════════════════════════════════════════

df = pd.read_stata(DATA_PATH)

df["year_int"] = df["year"].astype(int)
df["month_int"] = df["month"].astype(int)
df["quarter"] = (df["month_int"] - 1) // 3 + 1
df["yq"] = df["year_int"] * 10 + df["quarter"]
df["permno_id"] = df["permno"].astype(int)

quarterly = (
    df.groupby(["permno_id", "year_int", "quarter", "yq"])
    .agg(
        cashdiv_q=("cashdiv", "sum"),
        netissue_q=("netissue", "sum"),
        denom=("denom", "first"),
        d=("d", "first"),
        var_Q=("var_Q", "first"),
        cashrat=("cashrat", "first"),
        payout=("payout", "first"),
        netrep=("netrep", "first"),
    )
    .reset_index()
)

d_year_cols = [c for c in df.columns if c.startswith("d_year_")]
annual_dvars = (
    df.drop_duplicates(subset=["permno_id", "year_int"])[
        ["permno_id", "year_int"] + d_year_cols
    ]
)
quarterly = quarterly.merge(annual_dvars, on=["permno_id", "year_int"], how="left")

pos_denom = quarterly["denom"] > 0
quarterly["cashrat_q"] = np.where(
    pos_denom, quarterly["cashdiv_q"] / quarterly["denom"], 0.0
)

# Winsorize by year-quarter
quarterly["cashrat_q"] = quarterly.groupby("yq")["cashrat_q"].transform(
    lambda x: x.clip(x.quantile(WINSOR_CUTS[0]), x.quantile(WINSOR_CUTS[1]))
)

# Quarter-of-year × d controls (Q4 = base)
for q in [1, 2, 3]:
    quarterly[f"q{q}_d"] = quarterly["d"] * (quarterly["quarter"] == q)

qreg = quarterly.dropna(subset=["cashrat_q", "var_Q", "d"]).copy()

print(
    f"Quarterly panel: {len(qreg):,} firm-quarters | "
    f"{qreg['permno_id'].nunique()} firms | "
    f"{qreg['yq'].nunique()} year-quarters"
)


# ═════════════════════════════════════════════════════════════════════════════
# 2. Create year-quarter × d interaction dummies (omit all of 1932)
# ═════════════════════════════════════════════════════════════════════════════

all_yqs = sorted(qreg["yq"].unique())
omitted_yqs = [yq for yq in all_yqs if yq // 10 == OMITTED_YEAR]
interact_yqs = [yq for yq in all_yqs if yq not in omitted_yqs]

interact_cols = {}
for yq in interact_yqs:
    interact_cols[f"d_yq{yq}"] = qreg["d"].values * (qreg["yq"].values == yq)

qreg = pd.concat(
    [qreg, pd.DataFrame(interact_cols, index=qreg.index)], axis=1
)

d_yq_vars = [f"d_yq{yq}" for yq in interact_yqs]
d_yq_formula = " + ".join(d_yq_vars)

print(
    f"Interaction terms: {len(d_yq_vars)} year-quarter dummies "
    f"(omitting all of {OMITTED_YEAR})"
)


# ═════════════════════════════════════════════════════════════════════════════
# 3. Validate: replicate annual regressions (Table 5, cols 1-3)
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  VALIDATION: Annual regression replication (Table 5, cols 1-3)")
print("=" * 70)

df_annual = qreg.drop_duplicates(subset=["permno_id", "year_int"]).copy()
d_year_incl = [c for c in sorted(d_year_cols) if c != f"d_year_{OMITTED_YEAR}"]
d_year_str = " + ".join(d_year_incl)

annual_fits = {}
for depvar, label in [
    ("payout", "Payout"),
    ("cashrat", "Dividend"),
    ("netrep", "Net rep."),
]:
    fml = f"{depvar} ~ var_Q + d + {d_year_str} | permno_id + year_int"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = pf.feols(fml, data=df_annual, vcov={"CRV1": "permno_id"})
    annual_fits[depvar] = fit
    coefs, se, pv = fit.coef(), fit.se(), fit.pvalue()
    print(f"\n{label} ({depvar}): N={fit._N}, R²={fit._r2:.3f}")
    for v in ["var_Q", "d", "d_year_1933", "d_year_1934"]:
        if v in coefs.index:
            se_str = f"({se[v]:.3f})" if not np.isnan(se[v]) else "(—)"
            print(f"  {v:>15s}: {coefs[v]:8.3f}{stars(pv[v]):4s} {se_str}")


# ═════════════════════════════════════════════════════════════════════════════
# 4. Four quarter-specific annual regressions
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  QUARTER-SPECIFIC ANNUAL REGRESSIONS (same spec, different quarter data)")
print("=" * 70)

d_year_str = " + ".join(d_year_incl)
fml_annual = f"cashrat_q ~ var_Q + d + {d_year_str} | permno_id + year_int"

quarterly_fits = {}
for q in [1, 2, 3, 4]:
    qdf = qreg[qreg["quarter"] == q].drop_duplicates(
        subset=["permno_id", "year_int"]
    ).copy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        quarterly_fits[q] = pf.feols(fml_annual, data=qdf, vcov={"CRV1": "permno_id"})
    coefs, se, pv = (
        quarterly_fits[q].coef(),
        quarterly_fits[q].se(),
        quarterly_fits[q].pvalue(),
    )
    print(f"\nQ{q} cash dividend: N={quarterly_fits[q]._N}, R²={quarterly_fits[q]._r2:.3f}")
    for v in ["var_Q", "d", "d_year_1933", "d_year_1934"]:
        if v in coefs.index:
            se_str = f"({se[v]:.3f})" if not np.isnan(se[v]) else "(—)"
            print(f"  {v:>15s}: {coefs[v]:8.3f}{stars(pv[v]):4s} {se_str}")


# ═════════════════════════════════════════════════════════════════════════════
# 5. Coefficient plot (Q2 only)
# ═════════════════════════════════════════════════════════════════════════════

def extract_d_year_coefs(fit, year_cols, omitted_year=1932):
    """Extract d_year_* coefficients from annual regression for plotting."""
    coefs, se = fit.coef(), fit.se()
    years = sorted(int(c.split("_")[-1]) for c in year_cols)
    if omitted_year not in years:
        years = sorted(set(years) | {omitted_year})
    rows = []
    for yr in years:
        vname = f"d_year_{yr}"
        c = 0.0 if yr == omitted_year else (coefs[vname] if vname in coefs.index else np.nan)
        s = 0.0 if yr == omitted_year else (se[vname] if vname in se.index else np.nan)
        rows.append({"year": yr, "coef": c, "se": s})
    out = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
    out["date"] = out["year"].apply(lambda y: datetime(y, 1, 1))
    out["ci_lo"] = out["coef"] - 1.96 * out["se"]
    out["ci_hi"] = out["coef"] + 1.96 * out["se"]
    return out


LITIGATION_START = datetime(1933, 4, 1)
LITIGATION_END = datetime(1935, 3, 31)

fig, ax = plt.subplots(figsize=(8, 5))

cdf = extract_d_year_coefs(
    quarterly_fits[2], d_year_cols, omitted_year=OMITTED_YEAR
)

ax.axvspan(LITIGATION_START, LITIGATION_END, alpha=0.06, color="grey")

valid = ~cdf["se"].isna()
cdf_ci = cdf[valid]
ax.fill_between(
    cdf_ci["date"], cdf_ci["ci_lo"], cdf_ci["ci_hi"],
    alpha=0.2, color="steelblue",
)
ax.plot(
    cdf["date"], cdf["coef"], "-o",
    color="steelblue", linewidth=1.5, markersize=4,
)
ax.axhline(0, color="black", linewidth=0.5)

ax.set_ylabel(r"$\gamma_{\mathrm{year}}$", fontsize=11)
ax.set_xlabel("Year", fontsize=11)
ax.tick_params(labelsize=9)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

max_abs = cdf["coef"].abs().quantile(0.95) * 2.5
ax.set_ylim(-max_abs, max_abs)

fig.suptitle(
    r"$\tilde{d}$ $\times$ year coefficients (Q2): Cash dividend (annual spec)"
    f"\n(reference: {OMITTED_YEAR})",
    fontsize=13, fontweight="bold", y=1.02,
)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/quarterly-div-coefficients.pdf", bbox_inches="tight", dpi=300)
fig.savefig(f"{OUTPUT_DIR}/quarterly-div-coefficients.png", bbox_inches="tight", dpi=300)
print(f"\nFigure saved to {OUTPUT_DIR}/quarterly-div-coefficients.{{pdf,png}}")


# ═════════════════════════════════════════════════════════════════════════════
# 6. Regression table (Table 5 style)
# ═════════════════════════════════════════════════════════════════════════════

def fmt_cell(coef, se, pv):
    c = coef if not np.isnan(coef) else 0.0
    s = se if not np.isnan(se) and se > 0 else 0.0
    return f"{c:.3f}{stars(pv)}", f"({s:.3f})"


def fmt_cell_tex(coef, se, pv):
    c = coef if not np.isnan(coef) else 0.0
    s = se if not np.isnan(se) and se > 0 else 0.0
    return f"{c:.3f}{stars_tex(pv)}", f"({s:.3f})"

table_fits = [annual_fits["cashrat"]] + [quarterly_fits[q] for q in [1, 2, 3, 4]]
d_years = sorted(int(c.split("_")[-1]) for c in d_year_incl)


def get_vals(fit, vname, is_omitted=False):
    if is_omitted:
        return "0.000", "(—)"
    coefs, ses, pvs = fit.coef(), fit.se(), fit.pvalue()
    return fmt_cell_tex(
        coefs.get(vname, np.nan), ses.get(vname, np.nan), pvs.get(vname, 1.0)
    )

tex_rows = []
c_vals = [get_vals(f, "var_Q")[0] for f in table_fits]
s_vals = [get_vals(f, "var_Q")[1] for f in table_fits]
tex_rows.append(f"        Q                           & {' & '.join(f'{v:>12}' for v in c_vals)} \\\\")
tex_rows.append(f"                                    & {' & '.join(f'{v:>12}' for v in s_vals)} \\\\")

c_vals = [get_vals(f, "d")[0] for f in table_fits]
s_vals = [get_vals(f, "d")[1] for f in table_fits]
tex_rows.append(f"        \\ensuremath{{\\tilde{{d}}}}              & {' & '.join(f'{v:>12}' for v in c_vals)} \\\\")
tex_rows.append(f"                                    & {' & '.join(f'{v:>12}' for v in s_vals)} \\\\")

for yr in d_years:
    vname = f"d_year_{yr}" if yr != OMITTED_YEAR else None
    c_vals = [get_vals(f, vname, is_omitted=(yr == OMITTED_YEAR))[0] for f in table_fits]
    s_vals = [get_vals(f, vname, is_omitted=(yr == OMITTED_YEAR))[1] for f in table_fits]
    tex_rows.append(f"        \\ensuremath{{\\text{{{yr}}} \\times \\tilde{{d}}}}  & {' & '.join(f'{v:>12}' for v in c_vals)} \\\\")
    tex_rows.append(f"                                    & {' & '.join(f'{v:>12}' for v in s_vals)} \\\\")

tex_rows.append(f"        \\midrule")
r2_vals = [f"{f._r2:.3f}" for f in table_fits]
tex_rows.append(f"        \\ensuremath{{R^2}}    & {' & '.join(f'{v:>12}' for v in r2_vals)} \\\\")
n_vals = [f"\\multicolumn{{1}}{{r}}{{{f._N:,}$\\phantom{{000}}$}}" for f in table_fits]
tex_rows.append(f"        Observations        & {' & '.join(n_vals)}\\\\")

tex_content = r"""
\begin{table}[p]\centering
\caption{\\ Quarter-specific dividend regressions (annual specification)}
\scriptsize
\label{tab:quarterly_div}
\renewcommand{\arraystretch}{1.2}{
    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}
    \begin{tabular}{l*{5}{D{.}{.}{-1}}}
        \toprule
                            &\multicolumn{1}{c}{Annual}&\multicolumn{1}{c}{Q1}&\multicolumn{1}{c}{Q2}&\multicolumn{1}{c}{Q3}&\multicolumn{1}{c}{Q4}\\
                            &\multicolumn{1}{c}{(1)}&\multicolumn{1}{c}{(2)}&\multicolumn{1}{c}{(3)}&\multicolumn{1}{c}{(4)}&\multicolumn{1}{c}{(5)}\\
        \midrule
""" + "\n".join(tex_rows) + r"""
        \bottomrule
    \end{tabular}
}\\

\vspace*{3mm} \justifying \noindent
\scriptsize{\textit{Notes.} This table reports results from panel regressions of cash dividends on $Q$, gold clause exposure $\tilde{d}$, and year $\times$ $\tilde{d}$ interactions, where 1932 is the omitted category. Column 1 replicates the annual dividend specification (Table 5, column 2). Columns 2--5 use the same specification but restrict the sample to firm-years with data from Q1, Q2, Q3, or Q4 only; the dependent variable is quarterly cash dividend (sum of monthly dividends in that quarter) normalized by book common stock. All regressions include firm and year fixed effects. Standard errors in parentheses are clustered by firm. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}
\end{table}
"""

regtable_path = f"{OUTPUT_DIR}/quarterly-div-regtable.tex"
regtable_appendix = "manuscript/tables/online-appendix/11_quarterly_div.tex"
with open(regtable_path, "w") as f:
    f.write(tex_content)
# Write appendix version with tabapp label
tex_appendix = tex_content.replace(r"\label{tab:quarterly_div}", r"\label{tabapp:quarterly_div}")
with open(regtable_appendix, "w") as f:
    f.write(tex_appendix)
print(f"\nTable saved to {regtable_path} and {regtable_appendix}")
