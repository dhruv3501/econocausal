# Policy Evaluation (21 Oct)

## Goal
Compare the expected ROI of the optimized discount plan against greedy, random and blanket targeting on held-out customers.

## Method
- Evaluated on the 2,000 held-out customers in results/ite_scores.csv.
- Budget: $5,000 for optimized, greedy and random; blanket policies ignore the budget.
- True gain = true_effect * discount / 20 (possible because the data is synthetic).
- ROI = incremental revenue per discount dollar. Net ROI = ROI - 1.
- Random targeting is the mean of 200 seeds.

## Results
| Policy | Spend | Targeted | True incremental revenue | ROI |
|---|---:|---:|---:|---:|
| Optimized (MILP) | 5,000 | 307 | 10,067.00 | 2.013 |
| Greedy $10 by ITE | 5,000 | 500 | 9,420.58 | 1.884 |
| Random $10 (mean of 200 seeds) | 5,000 | 500 | 6,790.98 | 1.358 (std 0.016) |
| Blanket $10 (no budget limit) | 20,000 | 2,000 | 27,175.60 | 1.359 |
| Blanket $20 (no budget limit) | 40,000 | 2,000 | 54,351.20 | 1.359 |

## Findings
- Optimized has the highest ROI at the same spend as greedy and random.
- Blanket policies earn more total revenue only because they spend 4x to 8x more; per dollar they return less.
- Random targeting lands at the average effect per dollar (about 1.36), as expected.

## Limitations
- Synthetic data; real data would need an A/B test or off-policy evaluation.
- The optimizer uses point estimates of ITE and ignores their uncertainty.

## Reproduce
    python src/optimize/policy_evaluation.py --budget 5000