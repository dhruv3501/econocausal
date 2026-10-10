import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from dowhy import CausalModel

df = pd.read_csv("data/retail_mock.csv")
conf = ["age", "income", "tenure", "past_purchases",
        "loyalty_tier", "days_since_last_purchase"]

# keep only 0 and 20 so the control group is clean
d = df[df.discount.isin([0, 20])].copy()
d["treated"] = (d.discount == 20).astype(int)

naive = d[d.treated == 1].revenue.mean() - d[d.treated == 0].revenue.mean()

model = CausalModel(data=d, treatment="treated", outcome="revenue",
                    common_causes=conf)
estimand = model.identify_effect(proceed_when_unidentifiable=True)
est = model.estimate_effect(estimand, method_name="backdoor.linear_regression")
true = df.true_effect.mean()

print(f"Naive: {naive:.2f}  DoWhy: {est.value:.2f}  True: {true:.2f}")

# DAG image for the docs
g = nx.DiGraph()
for c in conf:
    g.add_edge(c, "discount")
    g.add_edge(c, "revenue")
g.add_edge("discount", "revenue")
plt.figure(figsize=(9, 6))
nx.draw(g, nx.spring_layout(g, seed=3), with_labels=True,
        node_color="#DCE6F5", node_size=2800, font_size=8, arrows=True)
plt.savefig("docs/causal_dag.png", dpi=150, bbox_inches="tight")