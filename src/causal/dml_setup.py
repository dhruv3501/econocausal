import pandas as pd
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor, LGBMClassifier
from econml.dml import LinearDML

df = pd.read_csv("data/retail_mock.csv")
covariates = ["age", "income", "tenure", "past_purchases",
              "loyalty_tier", "days_since_last_purchase"]

X = df[covariates]
T = df["discount"]      # 0 / 10 / 20
Y = df["revenue"]

X_tr, X_te, T_tr, T_te, Y_tr, Y_te = train_test_split(
    X, T, Y, test_size=0.2, random_state=42)

est = LinearDML(
    model_y=LGBMRegressor(n_estimators=200, learning_rate=0.05, verbose=-1),
    model_t=LGBMClassifier(n_estimators=200, learning_rate=0.05, verbose=-1),
    discrete_treatment=True,
    cv=5,                # cross-fitting folds
    random_state=42,
)
est.fit(Y_tr, T_tr, X=X_tr)

# sanity check: effect of $20 vs $0 on the test set
ite_20 = est.effect(X_te, T0=0, T1=20)
print("Average effect, $20 vs $0 (test):", ite_20.mean())
print("Rows scored:", len(ite_20))