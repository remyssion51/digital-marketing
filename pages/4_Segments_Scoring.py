import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from helpers import load_orders

st.title("🧩 Segments & Scoring")

st.markdown("""
On utilise la méthode RFM. Son intérêt est de segmenter les clients selon leur comportement d’achat :

- **R (Recency)** : depuis combien de temps le client n’a pas acheté
- **F (Frequency)** : à quelle fréquence il achète
- **M (Monetary)** : combien il dépense

Ces trois indicateurs résument très bien la **valeur marketing d’un client**.

L’objectif est de regrouper les clients ayant des comportements similaires
afin d’adapter les actions marketing (emails, promos, relances, fidélisation…).

On choisit volontairement un petit nombre de groupes car cela permet une segmentation
simple, lisible et exploitable par une équipe marketing, en plus de donner des clusters interprétables facilement.
""")


orders = load_orders().copy()
max_date = orders["date"].max()

orders["_cust"] = (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders["order_id"]%2000).astype(str)) if "order_id" in orders.columns else                   (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders.index%2000).astype(str))

rfm = orders.groupby("_cust").agg(
    recency=("date", lambda x: (max_date - x.max()).days),
    frequency=("revenue", "count"),
    monetary=("revenue", "sum")
).reset_index()

k = st.slider("Nombre de clusters (KMeans)", 2, 8, 4)
X = rfm[["recency","frequency","monetary"]].values
X = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(X)
rfm["cluster"] = km.labels_

st.subheader("Scatter 3D des clients par cluster")
st.plotly_chart(px.scatter_3d(rfm, x="recency", y="frequency", z="monetary", color="cluster", opacity=0.8),
                use_container_width=True)

st.subheader("KPIs par cluster")
summary = rfm.groupby("cluster").agg(
    clients=("cluster","count"),
    recency_avg=("recency","mean"),
    freq_avg=("frequency","mean"),
    monetary_avg=("monetary","mean"),
    monetary_sum=("monetary","sum")
).round(2).reset_index()
st.dataframe(summary, use_container_width=True)
