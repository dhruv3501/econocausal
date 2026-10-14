Day 4 Log — Propensity Score Matching

****Objective****
Evaluate covariate balance after matching customers based on their estimated propensity scores.

****Method****
- Estimated propensity scores using logistic regression.
- Matched each customer in the 20% discount treatment group to the nearest customer in the control group.
- Calculated Standardized Mean Differences (SMD) for numerical customer characteristics after matching.

****Results****
Feature| SMD| Absolute SMD
Age| 0.025074| 0.025074
Income| 0.015166| 0.015166
Tenure| -0.028560| 0.028560
Past purchases| 0.039362| 0.039362
Days since last purchase| 0.014493| 0.014493

****Interpretation****
All five evaluated numerical features have absolute SMD values below 0.1 after matching, indicating good balance on these measured features.

****Limitation****
The current balance table does not include the categorical variable "loyalty_tier". The results assess only the listed numerical features.

****Next Steps****
- Compare covariate balance before and after matching.
- Evaluate the matching-based treatment effect.
- Continue the remaining causal analysis tasks.
