# Model evaluation: DML vs naive baseline vs known truth

Test set: 2000 customers (20% hold-out, random_state=42). Data is synthetic, so the true individual effect is known.

| Metric | $10 vs $0 | $20 vs $0 |
|---|---|---|
| True ATE | 13.5878 | 27.1756 |
| DML ATE | 13.8661 | 26.6017 |
| Naive ATE | 22.9808 | 43.0177 |
| DML ATE error | 0.2783 | -0.5739 |
| Naive ATE error | 9.393 | 15.8421 |
| DML ITE RMSE | 1.3232 | 1.4862 |
| Naive ITE RMSE | 10.1417 | 17.5918 |
| DML rank corr. (Spearman) | 0.8922 | 0.9224 |
| DML top-20% overlap with truth | 0.9325 | 0.9475 |

DML 95% CI for ATE: $10 = [12.7362, 14.9961], $20 = [25.4551, 27.7483]

**Reading it:** the naive difference is biased because high-loyalty customers were both more likely to get discounts and spend more. DML adjusts for the confounders, so its ATE error and ITE RMSE should be much smaller.
