# DML Setup (12 Oct)

- Model: EconML LinearDML, discrete treatment (0 / 10 / 20 discount).
- Nuisance models: LightGBM regressor for revenue, LightGBM classifier for discount.
- Cross-fitting: 5 folds. Train/test split: 80/20, random_state=42.
- Effect modifiers and controls: age, income, tenure, past purchases, loyalty tier, days since last purchase. The simulated true_effect column is not used as an input.
- Sanity check: average effect of $20 vs $0 on the 2,000-row test set = 26.60 (DoWhy baseline 26.92, true effect 27.18).

Next: train for the $10 discount, save the model with joblib, and extract per-customer effects.