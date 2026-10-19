# Optimization Design (Week 3)

## Problem
For each customer we have predicted ITEs for a $10 and a $20 discount (from LinearDML).
Choose at most one discount per customer so that predicted incremental revenue is
maximised and total discount spend stays within a fixed budget.

## Formulation (multiple-choice knapsack)
Binary variables: x[i,10], x[i,20] = 1 if customer i gets that discount.

    maximise    sum_i  margin * ( ITE_10[i] * x[i,10] + ITE_20[i] * x[i,20] )
    subject to  x[i,10] + x[i,20] <= 1           for every customer i
                sum_i ( 10 * x[i,10] + 20 * x[i,20] ) <= budget
                x[i,.] in {0, 1}

Implementation: `scipy.optimize.milp` (HiGHS solver) in `src/optimize/optimizer.py`,
2n binary variables, n+1 constraints, `mip_rel_gap = 1e-4`, 60 s time limit.
`margin` defaults to 1.0 (revenue is treated as the gain; use a value below 1 for profit).

## Baselines
| Policy | Rule | Source |
|---|---|---|
| Greedy $10 by ITE | $10 to the highest predicted-ITE customers until the budget runs out | `optimizer.py` |
| Random $10 | $10 to randomly chosen customers until the budget runs out | `optimizer.py` |
| Blanket $10 / $20 | Same discount to every customer, budget ignored | `blanket_baseline.py` |

## Results at a $5,000 budget (2,000 hold-out customers)
| Policy | Spend | Customers targeted | True incremental revenue | ROI |
|---|---:|---:|---:|---:|
| Optimized (MILP) | 5,000 | 307 | 10,067.00 | 2.013 |
| Greedy $10 by ITE | 5,000 | 500 | 9,420.58 | 1.884 |
| Random $10 | 5,000 | 500 | 6,744.73 | 1.349 |
| Blanket $10 (no budget limit) | 20,000 | 2,000 | 27,175.60 | 1.359 |
| Blanket $20 (no budget limit) | 40,000 | 2,000 | 54,351.20 | 1.359 |

- The optimizer beats greedy by about 6.9% and random by about 49% in incremental revenue.
- Blanket ROI (1.359) equals the average effect per dollar (27.18 / 20). It is the same for
  $10 and $20 because the simulated effect is linear in the discount. Random $10 lands at
  about the same ROI (1.349) because random targeting just reproduces the average.
- Blanket policies earn more total revenue only because they spend 4x to 8x more. Per dollar,
  targeting is clearly better: 2.013 vs 1.359 is about 48% more revenue per dollar.
- The optimizer spends the same $5,000 on fewer customers (307 vs 500), so the average
  discount per targeted customer is higher (about $16).
- Split of the optimizer's discounts (`results/allocation.csv`): 193 customers get $20
  ($3,860 of spend) and 114 get $10 ($1,140); the other 1,693 get no discount.

## Budget sensitivity (`src/optimize/budget_sweep.py`, `results/budget_sweep.csv`)
ROI (true incremental revenue per discount dollar):

| Budget | Optimized (MILP) | Greedy $10 | Random $10 |
|---:|---:|---:|---:|
| 2,500 | 2.015 | 2.013 | 1.355 |
| 5,000 | 2.013 | 1.884 | 1.349 |
| 10,000 | 1.885 | 1.690 | 1.351 |
| 20,000 | 1.695 | 1.359 | 1.359 |

Total true incremental revenue of the optimizer vs greedy:

| Budget | Optimized (MILP) | Greedy $10 | Optimizer advantage |
|---:|---:|---:|---:|
| 2,500 | 5,036.60 | 5,033.05 | +0.1% |
| 5,000 | 10,067.00 | 9,420.58 | +6.9% |
| 10,000 | 18,849.38 | 16,899.22 | +11.5% |
| 20,000 | 33,905.18 | 27,175.60 | +24.8% |

- ROI falls as the budget grows, because the best responders are served first and the budget
  then reaches weaker responders (diminishing returns).
- With a very small budget, greedy is almost as good as the optimizer: both can pick only the
  strongest responders.
- The optimizer's advantage grows with the budget. At $20,000 (the cost of a blanket $10 for
  everyone) it earns 33,905 vs 27,176 for the blanket policy (about +25%) while discounting
  only 1,023 of the 2,000 customers.
- At $20,000, greedy and random both end up giving $10 to all 2,000 customers, which is
  exactly the blanket $10 policy.

## Why the optimizer wins
Greedy ranks customers by the $10 effect only. The MILP compares the return per dollar of
both options for every customer and trades them off jointly under the shared budget, so it
does not simply give every selected customer the same discount.

## How the gain is measured
The optimizer maximises *predicted* gain. The reported gain is the *true* gain,
`true_effect * discount / 20`, which is only possible because the data is synthetic.
It assumes the effect is linear in the discount, which matches the true ATEs (13.59 vs 27.18).
Because the evaluation uses truth rather than predictions, the policy comparison is fair.

## Limitations
- Synthetic data. On real data, true gain is unknown and would need an A/B test or off-policy evaluation.
- The optimizer trusts the point estimates of ITE and ignores their uncertainty
  (ITE RMSE is 1.32 for $10 and 1.49 for $20).
- Only one constraint (total budget). No minimum reach, per-segment caps or fairness rules.

## Reproduce
    python src/optimize/optimizer.py --budget 5000
    python src/optimize/blanket_baseline.py
    python src/optimize/budget_sweep.py
