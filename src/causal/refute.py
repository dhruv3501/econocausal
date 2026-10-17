"""Causal audit: DoWhy refutation tests (+ a placebo test on the real DML model).

Run  :  python src/causal/refute.py
Writes: results/refutation.json, docs/causal_audit.md
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from dowhy import CausalModel
from econml.dml import LinearDML
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
COVARIATES = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]
N_SIM = 100          # lower to 30 if you are short on time

df = pd.read_csv(ROOT / "data" / "retail_mock.csv")

# ---------------------------------------------------------------------------
# A. DoWhy refuters (same setup as baseline.py: $20 vs $0, linear backdoor)
# ---------------------------------------------------------------------------
d = df[df.discount.isin([0, 20])].copy()
d["treated"] = (d.discount == 20).astype(int)

model = CausalModel(data=d, treatment="treated", outcome="revenue",
                    common_causes=COVARIATES)
estimand = model.identify_effect(proceed_when_unidentifiable=True)
estimate = model.estimate_effect(estimand, method_name="backdoor.linear_regression")
print("Original estimate:", estimate.value)


def p_value(res):
    r = getattr(res, "refutation_result", None)
    if isinstance(r, dict):
        return r.get("p_value")
    return None


tests = [
    ("Placebo treatment (permute T)", "placebo_treatment_refuter",
     dict(placebo_type="permute", num_simulations=N_SIM)),
    ("Random common cause", "random_common_cause", dict(num_simulations=N_SIM)),
    ("Data subset (80%)", "data_subset_refuter",
     dict(subset_fraction=0.8, num_simulations=N_SIM)),
    # unobserved-confounder sensitivity (also used for the 22 Oct Week-3 task)
    ("Unobserved common cause", "add_unobserved_common_cause",
     dict(confounders_effect_on_treatment="linear", confounders_effect_on_outcome="linear",
          effect_strength_on_treatment=0.01, effect_strength_on_outcome=0.02)),
]

rows = []
for name, method, kw in tests:
    try:
        res = model.refute_estimate(estimand, estimate, method_name=method, **kw)
        new, p = float(res.new_effect), p_value(res)
        if method == "placebo_treatment_refuter":
            ok = abs(new) < 0.05 * abs(estimate.value) if p is None else p > 0.05
        else:
            ok = abs(new - estimate.value) / abs(estimate.value) < 0.05
        rows.append({"test": name, "original": round(float(estimate.value), 4),
                     "new_effect": round(new, 4),
                     "p_value": None if p is None else round(float(p), 4),
                     "passed": bool(ok)})
    except Exception as e:                      # keep going if one refuter breaks
        rows.append({"test": name, "error": str(e)[:120], "passed": None})
    print(rows[-1])

# ---------------------------------------------------------------------------
# B. Placebo on the REAL estimator (LinearDML): shuffle T -> ATE must be ~ 0
# ---------------------------------------------------------------------------
X, T, Y = df[COVARIATES], df["discount"], df["revenue"]
X_tr, X_te, T_tr, _, Y_tr, _ = train_test_split(X, T, Y, test_size=0.2, random_state=42)
rng = np.random.default_rng(0)
placebo_ates = []
for _ in range(3):
    est = LinearDML(model_y=LGBMRegressor(n_estimators=200, learning_rate=0.05, verbose=-1),
                    model_t=LGBMClassifier(n_estimators=200, learning_rate=0.05, verbose=-1),
                    discrete_treatment=True, cv=5, random_state=42)
    est.fit(Y_tr, rng.permutation(T_tr.to_numpy()), X=X_tr)
    placebo_ates.append(float(est.ate(X_te, T0=0, T1=20)))
rows.append({"test": "DML placebo ($20 vs $0, 3 shuffles)",
             "original": None, "new_effect": round(float(np.mean(placebo_ates)), 4),
             "p_value": None, "passed": bool(abs(np.mean(placebo_ates)) < 2.0)})
print(rows[-1])

(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "docs").mkdir(exist_ok=True)
with open(ROOT / "results" / "refutation.json", "w") as f:
    json.dump(rows, f, indent=2)

md = ["# Causal audit (refutation tests)\n",
      f"Estimate under test: $20 vs $0 effect on revenue = **{estimate.value:.3f}** "
      "(DoWhy, backdoor linear regression).\n",
      "| Test | Original | New effect | p-value | Passed |", "|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['test']} | {r.get('original')} | {r.get('new_effect', r.get('error'))} "
              f"| {r.get('p_value')} | {r['passed']} |")
md += ["", "**How to read:** placebo should give ~0; random common cause and data subset "
       "should leave the estimate almost unchanged; the unobserved-cause test shows how much "
       "a hidden confounder moves the estimate.", ""]
(ROOT / "docs" / "causal_audit.md").write_text("\n".join(md), encoding="utf-8")
print("Wrote results/refutation.json and docs/causal_audit.md")
