**EconoCausal – Day 3 Log**

**Objective**
To improve the causal analysis of the effect of customer discounts on revenue through visualization, propensity score weighting, and customer-balance checks.

**1. Discount Group Analysis**
Reviewed the number of customers receiving 0%, 10%, and 20% discounts and calculated average revenue for each discount group.

**2. Revenue Visualization**
Created a bar chart showing average revenue at each discount level.
The chart helps compare revenue across discount groups. However, differences in average revenue alone do not establish causation.

**3. Customer Group Comparison**
Created a binary treatment variable named "discount_20".
- 0: Customers who received a 0% or 10% discount.
- 1: Customers who received a 20% discount.
Compared income, past purchases, loyalty tier, days since last purchase, age, and tenure between the groups.

**4. Propensity Score Weighting**
Used logistic regression to estimate the probability of receiving a 20% discount based on observed customer characteristics.
Inverse probability weighting (IPW) was used to estimate the difference in revenue between the weighted treatment and comparison groups.
IPW estimate: 19.43

**5. Comparison of Estimates**
Method| Estimated Effect
Naive comparison| 42.88
DoWhy linear regression| 20.16
IPW weighting| 19.43
The adjusted estimates are closer to each other than to the naive estimate. This suggests that accounting for customer characteristics changes the estimated relationship between discounts and revenue.
These results do not, by themselves, prove that either adjusted estimate is unbiased.

**6. Customer Balance Check**
Calculated weighted average customer characteristics for the treatment and comparison groups to assess whether IPW made the observed groups more comparable.

**Day 3 Status:**
-Discount groups reviewed
-Average revenue visualized
-Customer characteristics compared
-IPW causal estimate calculated
-Estimates compared visually
-Weighted customer characteristics checked
-Results documented
