# EconoCausal – Day 2 Log
## Objective
To analyze customer differences across discount groups and estimate the causal effect of a 20% discount on revenue.

## Treatment Analysis
The discount variable contains three levels:
- 0% discount
- 10% discount
- 20% discount
A binary treatment variable named `discount_20` was created.
- 0 = Customer did not receive a 20% discount
- 1 = Customer received a 20% discount

## Customer Characteristics
Customer characteristics were compared across treatment groups, including:
- Age
- Income
- Tenure
- Past Purchases
- Loyalty Tier
- Days Since Last Purchase
These comparisons help identify differences between customers receiving different discount levels.

## Causal Estimation
DoWhy was used to estimate the causal effect of a 20% discount on revenue.
The backdoor linear regression estimator was used to adjust for customer characteristics.

## Results
| Method | Effect |
|---|---:|
| Naive Effect | 42.88 |
| Causal Effect | 20.16 |
| True Effect | 27.18 |

## Interpretation
The naive estimate was 42.88, while the DoWhy causal estimate was 20.16.
The difference shows that a simple comparison between discount groups can be affected by differences in customer characteristics.
Causal inference provides an adjusted estimate by accounting for these characteristics.

## Day 2 Status
-Treatment distribution analyzed
-Customer characteristics compared
-Binary 20% treatment created
-Causal effect estimated
-Naive, causal, and true effects compared
-Results documented
