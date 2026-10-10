# Baseline Results (0% vs 20% discount)

| Method | Effect on revenue |
|---|---:|
| Naive (difference in means) | 42.88 |
| DoWhy backdoor linear regression | 26.92 |
| True average effect (simulated) | 27.18 |

The naive estimate is biased because customers with higher loyalty tier and more past purchases are more likely to get the 20% discount and also spend more anyway. Adjusting for the six confounders brings the estimate close to the true effect.

The earlier estimate of 20.16 was biased because its control group included customers who received the 10% discount. This baseline compares only the 0% and 20% groups.