"""Table 6 sample prep and regressions (Stata A12_controls.do)."""

from __future__ import annotations

from lib.regressions import feols_clustered

MODEL_ORDER = [
    "industry_year_fe",
    "all_controls_linear",
    "q_deciles",
    "logasset_deciles",
    "netinc_deciles",
    "cash_deciles",
    "payout_deciles",
    "booklev_deciles",
    "marketlev_deciles",
    "logltl_deciles",
]

CORE_TERMS = ["var_Q", "d", "d_1933", "d_1934", "d_After"]

LINEAR_CONTROLS = [
    "var_Q_before",
    "var_Q_1933",
    "var_Q_1934",
    "var_Q_after",
    "var_logasset_before",
    "var_logasset_1933",
    "var_logasset_1934",
    "var_logasset_after",
    "var_netinc_before",
    "var_netinc_1933",
    "var_netinc_1934",
    "var_netinc_after",
    "var_cash_before",
    "var_cash_1933",
    "var_cash_1934",
    "var_cash_after",
    "var_payout_before",
    "var_payout_1933",
    "var_payout_1934",
    "var_payout_after",
    "var_booklev_before",
    "var_booklev_1933",
    "var_booklev_1934",
    "var_booklev_after",
    "var_marketlev_before",
    "var_marketlev_1933",
    "var_marketlev_1934",
    "var_marketlev_after",
    "var_logltl_before",
    "var_logltl_1933",
    "var_logltl_1934",
    "var_logltl_after",
]

PORTFOLIO_PREFIX_BY_MODEL = {
    "q_deciles": "fix_var_Q_port",
    "logasset_deciles": "fix_var_logasset_port",
    "netinc_deciles": "fix_var_netinc_port",
    "cash_deciles": "fix_var_cash_port",
    "payout_deciles": "fix_var_payout_port",
    "booklev_deciles": "fix_var_booklev_port",
    "marketlev_deciles": "fix_var_marketlev_port",
    "logltl_deciles": "fix_var_logltl_port",
}

PERIODS = ("before", "1933", "1934", "after")


def portfolio_cols(prefix: str) -> list[str]:
    return [f"{prefix}_{decile}_{period}" for period in PERIODS for decile in range(1, 11)]


def _formula(dep: str, rhs: list[str], fe: str) -> str:
    return f"{dep} ~ {' + '.join(rhs)} | {fe}"


def run_models(df) -> dict[str, object]:
    models: dict[str, object] = {}

    models["industry_year_fe"] = feols_clustered(
        _formula("var_inv_rate", CORE_TERMS, "permno + sic2_year"),
        df,
    )

    models["all_controls_linear"] = feols_clustered(
        _formula("var_inv_rate", LINEAR_CONTROLS + CORE_TERMS, "permno + year"),
        df,
    )

    for key, prefix in PORTFOLIO_PREFIX_BY_MODEL.items():
        models[key] = feols_clustered(
            _formula("var_inv_rate", portfolio_cols(prefix) + CORE_TERMS, "permno + year"),
            df,
        )

    return models
