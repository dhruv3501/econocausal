# Mid-Review Evidence Pack (Week 1 + Week 2)

Project: **EconoCausal: Dynamic Pricing via Double Machine Learning** (Infotact Solutions, Data Science & ML)
Prepared: 18 Oct 2026 | Branch: `Dhruv` (Member A, Team Lead & Causal ML)
Mid Review window: 27-30 Oct 2026

All numbers below come from files already in this repo (`results/*.json`, `docs/*.md`). Everything can be regenerated with `python run_pipeline.py`.

---

## 1. Problem and causal design

- **Goal:** estimate each customer's Individual Treatment Effect (ITE) of a $10 or $20 discount on revenue, then give a budget-constrained discount plan that targets only the customers who respond.
- **Treatment:** discount level (0 / 10 / 20). **Outcome:** revenue.
- **Confounders (6):** age, income, tenure, past purchases, loyalty tier, days since last purchase.
- **Why confounding exists:** loyal, high-purchase customers are more likely to get a discount and also spend more anyway.
- **Assumptions:** unconfoundedness, positivity (group sizes 3,497 / 3,347 / 3,156), no interference.
- Details: `docs/causal_design.md`. DAG image: `docs/causal_dag.png`.

## 2. Week 1 evidence: baseline (0% vs 20% discount)

| Method | Effect on revenue |
|---|---:|
| Naive difference in means | 42.88 |
| DoWhy backdoor linear regression | 26.92 |
| True average effect (simulated) | 27.18 |

The naive estimate is biased upward by confounding. Adjusting for the six confounders gets within 0.26 of the truth.
An earlier estimate of 20.16 was wrong because the control group contained $10 customers; it was corrected to compare only the 0% and 20% groups. (`docs/week1.md`, `docs/baseline_results.md`)

## 3. Week 2 evidence: Double ML

**Setup** (`docs/dml_setup.md`): EconML `LinearDML`, discrete treatment (0/10/20), LightGBM nuisance models (regressor for revenue, classifier for discount), 5-fold cross-fitting, 80/20 split with `random_state=42`. The simulated `true_effect` column is never used as an input.

**Evaluation on the 2,000-customer hold-out** (`docs/model_eval.md`, `results/model_eval.json`):

| Metric | $10 vs $0 | $20 vs $0 |
|---|---|---|
| True ATE | 13.5878 | 27.1756 |
| DML ATE | 13.8661 | 26.6017 |
| Naive ATE | 22.9808 | 43.0177 |
| DML ATE error | 0.2783 | -0.5739 |
| Naive ATE error | 9.3930 | 15.8421 |
| DML ITE RMSE | 1.3232 | 1.4862 |
| Naive ITE RMSE | 10.1417 | 17.5918 |
| DML rank correlation (Spearman) | 0.8922 | 0.9224 |
| DML top-20% overlap with truth | 0.9325 | 0.9475 |

DML 95% CI for the ATE: $10 = [12.74, 15.00], $20 = [25.46, 27.75]. Both contain the true ATE.

**Tuning** (`docs/tuning.md`, 5-fold CV over n_estimators, learning_rate, num_leaves):

| LinearDML ($10 vs $0) | ITE RMSE vs truth | ATE bias |
|---|---|---|
| Default (200 trees, lr 0.05) | 1.323 | 0.278 |
| Tuned | 1.240 | 0.579 |

Tuning improved individual-level accuracy (ITE RMSE) but increased the average-level bias. The default model is kept for the pipeline because the ATE error is lower; this trade-off is worth stating in the viva.

## 4. Causal audit (DoWhy refutation tests)

Estimate under test: $20 vs $0 effect on revenue = **26.920** (`docs/causal_audit.md`, `results/refutation.json`).

| Test | What it checks | New effect | p-value | Passed |
|---|---|---|---|---|
| Placebo treatment (permute T) | effect should go to ~0 | -0.0164 | 0.98 | Yes |
| Random common cause | estimate should not move | 26.9188 | 0.90 | Yes |
| Data subset (80%) | estimate should be stable | 26.9164 | 0.94 | Yes |
| Unobserved common cause | how far a hidden confounder moves it | 26.9079 | n/a | Yes |
| DML placebo ($20 vs $0, 3 shuffles) | effect should go to ~0 | -0.2589 | n/a | Yes |

## 5. Early Week 3 evidence: budget optimizer

`src/optimize/optimizer.py` solves a multiple-choice knapsack with SciPy `milp`: one option from {0, $10, $20} per customer, maximize predicted incremental revenue subject to total discount spend <= budget.

Result at a **$5,000 budget** (`results/policy_eval.json`; true gain is computable because the data is synthetic):

| Policy | Spend | Customers targeted | True incremental revenue | ROI |
|---|---:|---:|---:|---:|
| Optimized (MILP) | 5,000 | 307 | 10,067.00 | 2.013 |
| Greedy $10 by ITE | 5,000 | 500 | 9,420.58 | 1.884 |
| Random $10 | 5,000 | 500 | 6,744.73 | 1.349 |

The optimizer beats greedy by about 6.9% in incremental revenue and random by about 49%, and the budget constraint holds (an assertion in the script checks it).

## 6. Status against the plan

| Plan item | Status |
|---|---|
| Causal design + DAG | Done (`docs/causal_design.md`, `docs/causal_dag.png`) |
| DoWhy baseline | Done (`src/causal/baseline.py`) |
| Mock data with known true effect | Done (`src/generate_mock_data.py`, `data/retail_mock.csv`) |
| LinearDML training, ATE + ITE | Done (`src/causal/train_dml.py`, `models/`, `results/ite_scores.csv`) |
| Evaluation vs naive and truth | Done (`src/causal/evaluate_dml.py`) |
| Nuisance-model tuning | Done (`src/causal/tune_dml.py`) |
| Refutation tests / causal audit | Done (`src/causal/refute.py`) |
| Dashboard: 3 routes, mock JSON | Done (`frontend/`) |
| SciPy optimizer (Week 3, started early) | Done (`src/optimize/optimizer.py`) |
| End-to-end runner | Done (`run_pipeline.py`) |
| Blanket-discount baseline | Open (`src/optimize/blanket_baseline.py`) |
| Optimization write-up | Open (`docs/optimization_design.md`) |
| Real dashboard data + API | Planned for 27 Oct onward |

## 7. How to reproduce

```bash
pip install -r requirements.txt
python run_pipeline.py          # full run (tuning + refutation are slow)
python run_pipeline.py --fast   # skips tuning and refutation
```

## 8. Likely viva questions (Member A)

1. What is a confounder here, and which ones did you adjust for?
2. Why is the naive estimate 42.88 when the true effect is 27.18?
3. What does Double ML do, and why cross-fit?
4. Why LightGBM for the nuisance models, and why a linear final stage?
5. What do positivity and unconfoundedness mean, and how did you check them?
6. What does the placebo refuter prove, and what does the unobserved-common-cause test tell you?
7. Why did tuning lower ITE RMSE but raise ATE bias?
8. How does the optimizer pick between $10 and $20 for one customer?
