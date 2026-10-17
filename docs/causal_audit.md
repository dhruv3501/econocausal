# Causal audit (refutation tests)

Estimate under test: $20 vs $0 effect on revenue = **26.920** (DoWhy, backdoor linear regression).

| Test | Original | New effect | p-value | Passed |
|---|---|---|---|---|
| Placebo treatment (permute T) | 26.9202 | -0.0164 | 0.98 | True |
| Random common cause | 26.9202 | 26.9188 | 0.9 | True |
| Data subset (80%) | 26.9202 | 26.9164 | 0.94 | True |
| Unobserved common cause | 26.9202 | 26.9079 | None | True |
| DML placebo ($20 vs $0, 3 shuffles) | None | -0.2589 | None | True |

**How to read:** placebo should give ~0; random common cause and data subset should leave the estimate almost unchanged; the unobserved-cause test shows how much a hidden confounder moves the estimate.
