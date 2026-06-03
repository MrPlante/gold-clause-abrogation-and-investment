# Local logs

Stata batch runs write `.log` files here (not versioned).

| Path | Source |
|------|--------|
| `stata/export_regressions.log` | `compare/run_compare.sh` |
| `stata/*.log` | Other batch jobs via `code/refactor/scripts/run_stata_do.sh` |

Run Stata from the repo root:

```bash
bash code/refactor/scripts/run_stata_do.sh code/refactor/compare/export_regressions.do
bash code/refactor/scripts/run_stata_do.sh code/refactor/stata/export_parallel_trend_figure.do
```

The wrapper `cd`s into `logs/stata/` and passes the repository root as the first argument to the `.do` file.
