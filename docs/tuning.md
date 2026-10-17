# Nuisance-model tuning (5-fold CV)

Grid: {'n_estimators': [100, 200, 400], 'learning_rate': [0.03, 0.05, 0.1], 'num_leaves': [15, 31]}

| Model | Best params | CV score |
|---|---|---|
| Outcome Y given X (LGBMRegressor) | {'learning_rate': 0.03, 'n_estimators': 200, 'num_leaves': 15} | RMSE 23.296 |
| Treatment T given X (LGBMClassifier) | {'learning_rate': 0.03, 'n_estimators': 100, 'num_leaves': 15} | log-loss 1.068 |

| LinearDML ($10 vs $0) | ITE RMSE vs truth | ATE bias |
|---|---|---|
| Default (200 trees, lr 0.05) | 1.323 | 0.278 |
| Tuned | 1.240 | 0.579 |
