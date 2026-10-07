# EconoCausal – Day 1 Log

## Objective
To understand the basic concept of causal inference and analyze the effect of discounts on customer revenue.

## Dataset
A synthetic retail customer dataset containing 10,000 records was generated.
The dataset contains:
- Age
- Income
- Tenure
- Past Purchases
- Loyalty Tier
- Days Since Last Purchase
- Discount
- Revenue
- True Effect

## Data Analysis
The dataset was checked for:
- Dataset shape
- Column names
- Missing values
- Discount distribution
- Average revenue by discount level
- Customer characteristics across discount groups
No missing values were found.

## Causal Analysis
A causal DAG was created using DoWhy.
The customer characteristics used for adjustment were:
- Income
- Past Purchases
- Loyalty Tier
- Days Since Last Purchase
- Age
- Tenure

## Results
The naive comparison between customers receiving 20% discount and 0% discount produced an estimated effect of:
**42.88**

A binary treatment variable was then created for customers receiving a 20% discount.
Using DoWhy with a backdoor linear regression estimator, the estimated causal effect was:
**20.16**

The average true treatment effect in the simulated data was approximately:
**22**

**CONCLUSION:**
The naive estimate was considerably higher than the causal estimate.
After adjusting for customer characteristics using causal inference, the estimated effect became much closer to the true simulated treatment effect.
This demonstrates how confounding can create bias in a simple comparison and how causal inference can help estimate a more reliable treatment effect.

## Day 1 Status
- Dataset generated✔️
- Data quality checked✔️
- Discount groups analyzed✔️
- Naive effect calculated✔️
- Causal DAG created✔️
- Dowhy estimand identified✔️
- Causal effect estimated✔️
- Results visualized✔️
- Day 1 analysis completed✔️
