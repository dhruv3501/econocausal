"""20 Oct (Member A, Week 3): dose-response + heterogeneity check for the DML model.

Part 1  Is the $10 vs $20 effect curve sensible?   (dose-response)
Part 2  Which customer features drive the ITE?     (heterogeneity)

Needs models/linear_dml.joblib from train_dml.py.
Run from anywhere:  python src/causal/dose_response.py
Writes: docs/dose_response.md, docs/dose_response.png,
        docs/heterogeneity.png, results/dose_response.csv
"""
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "retail_mock.csv"
MODEL = ROOT / "models" / "linear_dml.joblib"
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
DOCS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

COVARIATES = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]
DOSES = (10, 20)

# ---- 0. reproduce the SAME test split used in train_dml.py -----------------
df = pd.read_csv(DATA)
X, T, Y = df[COVARIATES], df["discount"], df["revenue"]
_, X_te, _, _, _, _ = train_test_split(X, T, Y, test_size=0.2, random_state=42)
est = joblib.load(MODEL)

# data is synthetic: revenue = ... + true_effect * (discount / 20)
truth = df.loc[X_te.index, "true_effect"].to_numpy()
true_ite = {d: truth * d / 20 for d in DOSES}
ite = {d: est.effect(X_te, T0=0, T1=d) for d in DOSES}

# ============================================================================
# PART 1 - DOSE-RESPONSE
# ============================================================================
rows = [dict(discount=0, est_ate=0.0, ci_low=0.0, ci_high=0.0,
             true_ate=0.0, ite_rmse=0.0)]
for d in DOSES:
    lo, hi = est.ate_interval(X_te, T0=0, T1=d, alpha=0.05)
    rows.append(dict(
        discount=d,
        est_ate=float(ite[d].mean()),
        ci_low=float(np.squeeze(lo)),
        ci_high=float(np.squeeze(hi)),
        true_ate=float(true_ite[d].mean()),
        ite_rmse=float(np.sqrt(np.mean((ite[d] - true_ite[d]) ** 2))),
    ))
dose = pd.DataFrame(rows).round(3)
dose.to_csv(RESULTS / "dose_response.csv", index=False)
print("\n=== Dose-response (test set) ===")
print(dose.to_string(index=False))

ate10, ate20 = dose.loc[1, "est_ate"], dose.loc[2, "est_ate"]
checks = {
    "ATE($20) > ATE($10) > 0": bool(ate20 > ate10 > 0),
    "ATE($20) / ATE($10) (truth = 2.0)": round(ate20 / ate10, 2),
    "Extra gain of 2nd $10 (ATE20 - ATE10)": round(ate20 - ate10, 3),
    "Share of users with ITE20 > ITE10": round(float((ite[20] > ite[10]).mean()), 3),
    "Corr(ITE10, ITE20)": round(float(np.corrcoef(ite[10], ite[20])[0, 1]), 3),
}
print("\n=== Sanity checks ===")
for k, v in checks.items():
    print(f"{k:42s}: {v}")

fig, ax = plt.subplots(figsize=(6, 4))
ax.errorbar(dose["discount"], dose["est_ate"],
            yerr=[dose["est_ate"] - dose["ci_low"], dose["ci_high"] - dose["est_ate"]],
            marker="o", capsize=4, label="DML estimate (95% CI)")
ax.plot(dose["discount"], dose["true_ate"], "--s", label="True effect (synthetic)")
ax.set_xticks([0, 10, 20])
ax.set_xlabel("Discount ($)")
ax.set_ylabel("Average effect on revenue ($)")
ax.set_title("Dose-response: effect of discount level")
ax.legend()
fig.tight_layout()
fig.savefig(DOCS / "dose_response.png", dpi=150)
plt.close(fig)

# ============================================================================
# PART 2 - HETEROGENEITY (what drives the ITE?)
# ============================================================================
# LinearDML's final model is linear in X, so its coefficients ARE the drivers.
coef = {}
for d in DOSES:
    try:
        coef[d] = np.asarray(est.coef_(d)).ravel()
    except Exception:  # fallback: ITE is linear in X, so a regression recovers it
        coef[d] = LinearRegression().fit(X_te, ite[d]).coef_

drivers = pd.DataFrame({"feature": COVARIATES})
for d in DOSES:
    drivers[f"coef_{d}"] = coef[d]
    # standardised = effect change per 1 std-dev of the feature -> comparable
    drivers[f"std_effect_{d}"] = coef[d] * X_te.std().to_numpy()
drivers = drivers.round(4).sort_values("std_effect_20", key=abs, ascending=False)
print("\n=== Feature drivers of the ITE ===")
print(drivers.to_string(index=False))

by_tier = (pd.DataFrame({"loyalty_tier": X_te["loyalty_tier"].to_numpy(),
                         "est_ite_10": ite[10], "true_ite_10": true_ite[10],
                         "est_ite_20": ite[20], "true_ite_20": true_ite[20]})
           .groupby("loyalty_tier").mean().round(2))
print("\n=== Mean ITE by loyalty tier ===")
print(by_tier.to_string())

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
order = drivers.sort_values("std_effect_20", key=abs)
axes[0].barh(order["feature"], order["std_effect_20"])
axes[0].set_title("Drivers of ITE ($20): effect per 1 std-dev")
axes[0].set_xlabel("Change in ITE ($)")
w = 0.35
idx = np.arange(len(by_tier))
axes[1].bar(idx - w / 2, by_tier["est_ite_20"], w, label="Estimated")
axes[1].bar(idx + w / 2, by_tier["true_ite_20"], w, label="True")
axes[1].set_xticks(idx)
axes[1].set_xticklabels(by_tier.index)
axes[1].set_xlabel("Loyalty tier")
axes[1].set_ylabel("Mean ITE for $20 ($)")
axes[1].set_title("ITE by loyalty tier")
axes[1].legend()
fig.tight_layout()
fig.savefig(DOCS / "heterogeneity.png", dpi=150)
plt.close(fig)


# ============================================================================
# WRITE THE DOC
# ============================================================================
def md_table(frame, index=False):
    frame = frame.reset_index() if index else frame
    head = "| " + " | ".join(map(str, frame.columns)) + " |"
    sep = "|" + "---|" * len(frame.columns)
    body = ["| " + " | ".join(map(str, r)) + " |" for r in frame.itertuples(index=False)]
    return "\n".join([head, sep, *body])


check_lines = "\n".join(f"- {k}: **{v}**" for k, v in checks.items())

doc = f"""# Dose-response and heterogeneity check (20 Oct)

Model: LinearDML (cross-fitted LightGBM nuisance models). Test rows: {len(X_te)}.

## 1. Dose-response ($0 / $10 / $20)

{md_table(dose)}

![dose-response](dose_response.png)

Sanity checks:

{check_lines}

**Interpretation (edit me):** the effect should rise with the discount. In the
synthetic data the true effect is linear in the discount ($20 = 2 x $10), so the
ratio should be close to 2 and the second $10 should add about as much as the first.

## 2. What drives the individual effect?

{md_table(drivers)}

`std_effect_*` = change in ITE for a 1 standard-deviation increase in the feature.

### Mean ITE by loyalty tier

{md_table(by_tier, index=True)}

![heterogeneity](heterogeneity.png)

**Interpretation (edit me):** the data generator sets
`true_effect = 20 + 10*loyalty_tier + 0.05*past_purchases`, so loyalty_tier should
dominate, past_purchases should be tiny, and age/income/tenure/recency should be
near zero. If the DML coefficients agree, the model has recovered the true
heterogeneity. Any large coefficient on a feature with no true effect is noise.

## 3. Implication for the optimizer

Higher loyalty tiers have larger ITE, so the budget optimizer should favour them
(check this in the 21 Oct ROI policy evaluation).
"""
(DOCS / "dose_response.md").write_text(doc, encoding="utf-8")
print("\nSaved: docs/dose_response.md, docs/dose_response.png, docs/heterogeneity.png")