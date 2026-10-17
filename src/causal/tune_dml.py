"""Tune the DML nuisance models (outcome model + treatment model) with CV.

Idea: DML only needs good predictions of Y|X and T|X, so we tune each model on
its own CV loss, then refit LinearDML and check ITE error vs the known truth.

Run  :  python src/causal/tune_dml.py       (takes a few minutes)
Writes: results/tuning.json, docs/tuning.md, models/linear_dml_tuned.joblib
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from econml.dml import LinearDML
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import GridSearchCV, train_test_split

ROOT = Path(__file__).resolve().parents[2]
COVARIATES = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]

df = pd.read_csv(ROOT / "data" / "retail_mock.csv")
X, T, Y = df[COVARIATES], df["discount"], df["revenue"]
X_tr, X_te, T_tr, T_te, Y_tr, Y_te = train_test_split(
    X, T, Y, test_size=0.2, random_state=42)

GRID = {"n_estimators": [100, 200, 400],
        "learning_rate": [0.03, 0.05, 0.1],
        "num_leaves": [15, 31]}

# ---- 1. tune each nuisance model on its own CV loss ------------------------
y_search = GridSearchCV(LGBMRegressor(verbose=-1, random_state=42, n_jobs=1),
                        GRID, cv=5, scoring="neg_root_mean_squared_error", n_jobs=-1)
y_search.fit(X_tr, Y_tr)

t_search = GridSearchCV(LGBMClassifier(verbose=-1, random_state=42, n_jobs=1),
                        GRID, cv=5, scoring="neg_log_loss", n_jobs=-1)
t_search.fit(X_tr, T_tr)

print("Outcome model best :", y_search.best_params_, "CV RMSE", -y_search.best_score_)
print("Treatment model best:", t_search.best_params_, "CV logloss", -t_search.best_score_)


# ---- 2. refit LinearDML: default vs tuned, compare to the truth ------------
def fit_and_score(model_y, model_t):
    est = LinearDML(model_y=model_y, model_t=model_t,
                    discrete_treatment=True, cv=5, random_state=42)
    est.fit(Y_tr, T_tr, X=X_tr)
    ite = est.effect(X_te, T0=0, T1=10)
    true = df.loc[X_te.index, "true_effect"].to_numpy() * 10 / 20
    return est, float(np.sqrt(np.mean((ite - true) ** 2))), float(ite.mean() - true.mean())


_, rmse_def, bias_def = fit_and_score(
    LGBMRegressor(n_estimators=200, learning_rate=0.05, verbose=-1),
    LGBMClassifier(n_estimators=200, learning_rate=0.05, verbose=-1))
est_tuned, rmse_tun, bias_tun = fit_and_score(
    LGBMRegressor(**y_search.best_params_, verbose=-1, random_state=42),
    LGBMClassifier(**t_search.best_params_, verbose=-1, random_state=42))

print(f"Default: ITE RMSE {rmse_def:.3f}  ATE bias {bias_def:.3f}")
print(f"Tuned  : ITE RMSE {rmse_tun:.3f}  ATE bias {bias_tun:.3f}")

# ---- 3. save ---------------------------------------------------------------
out = {
    "grid": GRID,
    "outcome_model": {"best_params": y_search.best_params_, "cv_rmse": round(-y_search.best_score_, 4)},
    "treatment_model": {"best_params": t_search.best_params_, "cv_logloss": round(-t_search.best_score_, 4)},
    "default": {"ite_rmse_10": round(rmse_def, 4), "ate_bias_10": round(bias_def, 4)},
    "tuned": {"ite_rmse_10": round(rmse_tun, 4), "ate_bias_10": round(bias_tun, 4)},
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "models").mkdir(exist_ok=True)
(ROOT / "docs").mkdir(exist_ok=True)
with open(ROOT / "results" / "tuning.json", "w") as f:
    json.dump(out, f, indent=2)
joblib.dump(est_tuned, ROOT / "models" / "linear_dml_tuned.joblib")

md = f"""# Nuisance-model tuning (5-fold CV)

Grid: {GRID}

| Model | Best params | CV score |
|---|---|---|
| Outcome Y given X (LGBMRegressor) | {y_search.best_params_} | RMSE {-y_search.best_score_:.3f} |
| Treatment T given X (LGBMClassifier) | {t_search.best_params_} | log-loss {-t_search.best_score_:.3f} |

| LinearDML ($10 vs $0) | ITE RMSE vs truth | ATE bias |
|---|---|---|
| Default (200 trees, lr 0.05) | {rmse_def:.3f} | {bias_def:.3f} |
| Tuned | {rmse_tun:.3f} | {bias_tun:.3f} |
"""
(ROOT / "docs" / "tuning.md").write_text(md, encoding="utf-8")
print("Wrote results/tuning.json, docs/tuning.md, models/linear_dml_tuned.joblib")
