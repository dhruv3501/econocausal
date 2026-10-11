# Week 1 Summary

## Goal
Define the causal design for the dynamic pricing problem and get a first, honest estimate of the discount effect.

## What was done
- Causal design (docs/causal_design.md): treatment = discount level (0 / 10 / 20), outcome = revenue, six confounders (age, income, tenure, past purchases, loyalty tier, days since last purchase).
- Causal DAG built with DoWhy/networkx (docs/causal_dag.png).
- Backdoor identification and a baseline estimate (src/causal/baseline.py).
- Mock retail dataset generator (src/generate_mock_data.py) with a known true effect.

## Baseline results (0% vs 20% discount)
| Method | Effect on revenue |
|---|---:|
| Naive difference in means | 42.88 |
| DoWhy backdoor linear regression | 26.92 |
| True average effect (simulated) | 27.18 |

## Key finding
The naive estimate is biased because loyal, high-purchase customers are more likely to get the 20% discount and also spend more anyway. Adjusting for the six confounders brings the estimate close to the true effect.

## Correction
An earlier estimate of 20.16 was biased because the control group included customers who got the 10% discount. The corrected baseline compares only the 0% and 20% groups.

## Assumptions
Unconfoundedness, positivity (group sizes 3,497 / 3,347 / 3,156), and no interference.

## Next (Week 2)
EconML Double ML (LinearDML / CausalForestDML), per-user ITE, evaluation against the known true effect, and DoWhy refutation tests.