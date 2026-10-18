# Optimization design: budget-constrained discount allocation

Code: `src/optimize/optimizer.py` | Baseline: `src/optimize/blanket_baseline.py` | Results: `results/policy_eval.json`, `results/blanket_eval.json`

## Problem

Given a predicted ITE for each customer from the DML model, choose **one** discount from {$0, $10, $20} per customer so that expected incremental revenue is as high as possible without spending more than the discount budget.

## Formulation (multiple-choice knapsack)

For customer *i* in 1..n:

- Decision variables: `x_i10`, `x_i20` in {0, 1}. Choosing neither means no discount.
- Objective: maximize `margin * sum_i ( ITE_i,10 * x_i10 + ITE_i,20 * x_i20 )`
- One choice per customer: `x_i10 + x_i20 <= 1` for every *i*
- Budget: `sum_i ( 10 * x_i10 + 20 * x_i20 ) <= B`

`ITE_i,10` and `ITE_i,20` come from `results/ite_scores.csv` (LinearDML, hold-out customers). `margin` defaults to 1.0 (`--margin`), so the objective is predicted incremental revenue.

## Solver

`scipy.optimize.milp` (HiGHS) with integer variables bounded in [0, 1], a 60 s time limit and a relative gap of 1e-4. The two constraint blocks are built as sparse matrices, so the problem scales to many thousands of customers. If the solver returns no solution the script raises an error instead of returning a silent fallback. After solving, an assertion checks that spend does not exceed the budget.

## Baselines

| Policy | Rule |
|---|---|
| Greedy $10 by ITE | Give $10 to the customers with the highest predicted ITE until the budget runs out (only if ITE is positive) |
| Random $10 | Give $10 to randomly chosen customers until the budget runs out |
| Blanket $10 / $20 | Give every customer the same discount, ignoring the budget (`blanket_baseline.py`) |

## How policies are scored

The data is synthetic, so the real effect of a discount on each customer is known. `true_gain()` sums `true_effect * discount / 20` over the chosen customers (the generator makes the effect scale with the discount). ROI = true incremental revenue / spend. This is a validation step that is only possible on simulated data.

## Results at a $5,000 budget

| Policy | Spend | Customers targeted | True incremental revenue | ROI |
|---|---:|---:|---:|---:|
| Optimized (MILP) | 5,000 | 307 | 10,067.00 | 2.013 |
| Greedy $10 by ITE | 5,000 | 500 | 9,420.58 | 1.884 |
| Random $10 | 5,000 | 500 | 6,744.73 | 1.349 |

Blanket $10 and $20 numbers are produced by `python src/optimize/blanket_baseline.py` and written to `results/blanket_eval.json`; add them to this table after running it.

Why MILP beats greedy: greedy can only hand out $10 discounts, so it reaches 500 customers. The MILP is free to give $20 to customers whose extra response justifies the extra cost, so it reaches fewer customers (307) and still earns more.

## Limitations

- The objective uses revenue uplift only. With a real margin below 1, pass `--margin` so the plan reflects profit, not revenue.
- The plan is only as good as the ITE estimates (DML ITE RMSE on the hold-out is about 1.3 for $10 and 1.5 for $20).
- The true-gain scoring relies on the synthetic data. On real data you would score with a held-out experiment or an uplift/Qini curve.
- Customers are treated independently (no interference), the same assumption as the causal design.

## Next

- Run the budget sweep ($1k to $10k) and export the efficiency-curve data (22 Oct item).
- Connect `results/allocation.csv` to the dashboard's Allocation Matrix page.
