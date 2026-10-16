****Causal Forest Evaluation and Customer Ranking****

****Objective****
Train a Causal Forest model to estimate individual treatment effects (ITE) and identify customers who are predicted to respond more strongly to a 20% discount compared with a 0% discount.

****Work Completed****
- Prepared a binary treatment dataset containing only customers who received 0% or 20% discounts.
- Split the dataset into training and testing sets using an 80:20 ratio.
- Trained a Causal Forest model using EconML.
- Generated individual treatment effect predictions for 1,331 test customers.
- Compared predicted ITE values with the synthetic dataset's known treatment effects.
- Ranked customers by predicted ITE and saved the results as CSV files.
- Calculated prediction error metrics and Spearman rank correlation.

****Results****
Metric| Result
Test customers| 1,331
Average estimated ITE| 26.19
Average true effect| 27.20
MAE| 2.21
RMSE| 2.81
Spearman rank correlation| 0.869

****Interpretation****
The model's average estimated treatment effect was close to the average true effect in the synthetic test data. The Spearman correlation of 0.869 indicates strong agreement between the predicted and true customer rankings.
These results are preliminary synthetic-data results and do not establish performance on real customer data.

****Output Files****
- "week2_validation_summary.csv"
- "corrected_causal_forest_results.csv"
- "ranked_customer_ite_corrected.csv"
- ****Next Steps****
- Review the causal modeling assumptions and validation results.
- Integrate validated model outputs into the React dashboard.
- Update the project documentation and test the end-to-end workflow.
