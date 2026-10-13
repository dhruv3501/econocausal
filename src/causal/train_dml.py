"""Train LinearDML, estimate ATE + per-customer ITE, save model and scores.

Run from anywhere:  python src/causal/train_dml.py
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from econml.dml import LinearDML
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "retail_mock.csv"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"
MODELS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

COVARIATES = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]

# ---- 1. load + split -------------------------------------------------------
df = pd.read_csv(DATA)
X, T, Y = df[COVARIATES], df["discount"], df["revenue"]
X_tr, X_te, T_tr, T_te, Y_tr, Y_te = train_test_split(
    X, T, Y, test_size=0.2, random_state=42)

# ---- 2. fit Double ML (cross-fitted nuisance models) -----------------------
est = LinearDML(
    model_y=LGBMRegressor(n_estimators=200, learning_rate=0.05, verbose=-1),
    model_t=LGBMClassifier(n_estimators=200, learning_rate=0.05, verbose=-1),
    discrete_treatment=True,
    cv=5,
    random_state=42,
)
est.fit(Y_tr, T_tr, X=X_tr)

# ---- 3. ATE + per-user ITE for the $10 discount (and $20 for the export) ---
ate_10 = float(est.ate(X_te, T0=0, T1=10))
lo, hi = est.ate_interval(X_te, T0=0, T1=10, alpha=0.05)
lo, hi = float(np.squeeze(lo)), float(np.squeeze(hi))
ite_10 = est.effect(X_te, T0=0, T1=10)
ite_20 = est.effect(X_te, T0=0, T1=20)

# ---- 4. check against the known truth (the data is synthetic) --------------
# revenue = baseline + true_effect * (discount / 20)  ->  $10 gives half of it
true_10 = df.loc[X_te.index, "true_effect"].to_numpy() * 10 / 20
rmse = float(np.sqrt(np.mean((ite_10 - true_10) ** 2)))
print(f"ATE $10 vs $0 : {ate_10:.3f}   95% CI [{lo:.3f}, {hi:.3f}]")
print(f"True ATE $10  : {true_10.mean():.3f}")
print(f"ITE RMSE      : {rmse:.3f}")
print(f"Rows scored   : {len(ite_10)}")

# ---- 5. save model + scores ------------------------------------------------
model_path = MODELS / "linear_dml.joblib"
joblib.dump(est, model_path)
loaded = joblib.load(model_path)
assert np.allclose(loaded.effect(X_te.head(5), T0=0, T1=10), ite_10[:5])
print("Saved model   :", model_path.relative_to(ROOT), "(reload check OK)")

pd.DataFrame({"user_id": X_te.index, "ite_10": ite_10.round(4),
              "ite_20": ite_20.round(4)}).to_csv(RESULTS / "ite_scores.csv", index=False)

with open(RESULTS / "dml_summary.json", "w") as f:
    json.dump({"model": "LinearDML", "treatment": "$10 vs $0",
               "ate_10": round(ate_10, 4), "ate_10_ci95": [round(lo, 4), round(hi, 4)],
               "true_ate_10": round(float(true_10.mean()), 4),
               "ite_rmse_10": round(rmse, 4), "n_test": int(len(ite_10))}, f, indent=2)
print("Saved scores  : results/ite_scores.csv, results/dml_summary.json")