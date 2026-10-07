import numpy as np
import pandas as pd
np.random.seed(42)
n = 10000
# Customer features
age = np.random.randint(18, 70, n)
income = np.random.normal(50000, 15000, n).clip(15000, 100000)
tenure = np.random.randint(1, 10, n)
past_purchases = np.random.poisson(5, n)
loyalty_tier = np.random.choice([0, 1, 2], n, p=[0.5, 0.3, 0.2])
days_since_last_purchase = np.random.randint(1, 180, n)
# Discount treatment: 0, 10 or 20
score = (
    0.3 * loyalty_tier
    + 0.1 * past_purchases
    + np.random.normal(0, 1, n)
)
discount = np.where(score > 1.2, 20,
           np.where(score > 0.3, 10, 0))
# True individual treatment effect
true_effect = 20 + 10 * loyalty_tier + 0.05 * past_purchases
# Customer outcome
baseline = (
    100
    + 0.002 * income
    + 8 * past_purchases
    + 15 * loyalty_tier
    - 0.2 * days_since_last_purchase
)
noise = np.random.normal(0, 20, n)
revenue = baseline + true_effect * (discount / 20) + noise
data = pd.DataFrame({
    "age": age,
    "income": income.round(2),
    "tenure": tenure,
    "past_purchases": past_purchases,
    "loyalty_tier": loyalty_tier,
    "days_since_last_purchase": days_since_last_purchase,
    "discount": discount,
    "revenue": revenue.round(2),
    "true_effect": true_effect.round(2)
})
data.to_csv("data/retail_mock.csv", index=False)
print("Dataset created successfully!")
print(data.head())
print("Shape:", data.shape)
