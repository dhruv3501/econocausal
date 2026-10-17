"""Evaluate saved LinearDML vs a naive baseline vs the known true effect.

Needs:  python src/causal/train_dml.py   (creates models/linear_dml.joblib)
Run  :  python src/causal/evaluate_dml.py
Writes: results/model_eval.json  and  docs/model_eval.md
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
COVARIATES = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]

df = pd.read_csv(ROOT / "data" / "retail_mock.csv")
X, T, Y = df[COVARIATES], df["discount"], df["revenue"]
# SAME split as train_dml.py (random_state=42) so the test rows are unseen
X_tr, X_te, T_tr, T_te, Y_tr, Y_te = train_test_split(
    X, T, Y, test_size=0.2, random_state=42)

est = joblib.load(ROOT / "models" / "linear_dml.joblib")


def rmse(a):
    return float(np.sqrt(np.mean(np.square(a))))


def top_quintile_overlap(pred, true):
    """Share of the model's top-20% customers that are truly in the top 20%."""
    k = max(1, int(0.2 * len(pred)))
    p_top = set(np.argsort(-pred)[:k])
    t_top = set(np.argsort(-true)[:k])
    return len(p_top & t_top) / k


results = {}
for d in (10, 20):
    ite = est.effect(X_te, T0=0, T1=d)
    true = df.loc[X_te.index, "true_effect"].to_numpy() * d / 20  # effect scales with discount
    lo, hi = est.ate_interval(X_te, T0=0, T1=d, alpha=0.05)

    # naive = plain difference in mean revenue (ignores confounding)
    naive = float(Y_te[T_te == d].mean() - Y_te[T_te == 0].mean())

    results[f"${d}"] = {
        "true_ate": round(float(true.mean()), 4),
        "dml_ate": round(float(ite.mean()), 4),
        "dml_ate_ci95": [round(float(np.squeeze(lo)), 4), round(float(np.squeeze(hi)), 4)],
        "naive_ate": round(naive, 4),
        "dml_ate_error": round(float(ite.mean() - true.mean()), 4),
        "naive_ate_error": round(naive - float(true.mean()), 4),
        "dml_ite_rmse": round(rmse(ite - true), 4),
        # a naive method gives ONE number for everybody -> its ITE error is this:
        "naive_ite_rmse": round(rmse(naive - true), 4),
        "dml_spearman_vs_true": round(float(spearmanr(ite, true)[0]), 4),
        "dml_top20_overlap": round(top_quintile_overlap(ite, true), 4),
    }

(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "docs").mkdir(exist_ok=True)
with open(ROOT / "results" / "model_eval.json", "w") as f:
    json.dump({"n_test": int(len(X_te)), **results}, f, indent=2)

# ---- markdown for the Mid-Review pack -------------------------------------
rows = [("True ATE", "true_ate"), ("DML ATE", "dml_ate"), ("Naive ATE", "naive_ate"),
        ("DML ATE error", "dml_ate_error"), ("Naive ATE error", "naive_ate_error"),
        ("DML ITE RMSE", "dml_ite_rmse"), ("Naive ITE RMSE", "naive_ite_rmse"),
        ("DML rank corr. (Spearman)", "dml_spearman_vs_true"),
        ("DML top-20% overlap with truth", "dml_top20_overlap")]
md = ["# Model evaluation: DML vs naive baseline vs known truth\n",
      f"Test set: {len(X_te)} customers (20% hold-out, random_state=42). "
      "Data is synthetic, so the true individual effect is known.\n",
      "| Metric | $10 vs $0 | $20 vs $0 |", "|---|---|---|"]
for label, key in rows:
    md.append(f"| {label} | {results['$10'][key]} | {results['$20'][key]} |")
md += ["", "DML 95% CI for ATE: "
       f"$10 = {results['$10']['dml_ate_ci95']}, $20 = {results['$20']['dml_ate_ci95']}", "",
       "**Reading it:** the naive difference is biased because high-loyalty customers "
       "were both more likely to get discounts and spend more. DML adjusts for the "
       "confounders, so its ATE error and ITE RMSE should be much smaller.", ""]
(ROOT / "docs" / "model_eval.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(results, indent=2))
print("Wrote results/model_eval.json and docs/model_eval.md")
