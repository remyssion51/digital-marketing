import streamlit as st, pandas as pd, numpy as np
from datetime import timedelta
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from helpers import load_orders

st.title("🧩 Segments & Scoring (RFM + KMeans)")

orders = load_orders()
max_date = orders["date"].max()

# RFM per pseudo-customer
orders["_cust"] = (orders["country"] + "_" + orders["channel"]).astype(str) + "_" + (orders["order_id"]%2000).astype(str)
rfm = orders.groupby("_cust").agg(
    recency=("date", lambda x: (max_date - x.max()).days),
    frequency=("order_id", "count"),
    monetary=("revenue", "sum")
).reset_index()

st.write("Aperçu RFM", rfm.head())

k = st.slider("Nombre de clusters (KMeans)", 2, 8, 4)
features = rfm[["recency","frequency","monetary"]].copy()
scaler = StandardScaler()
X = scaler.fit_transform(features)
km = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(X)
rfm["cluster"] = km.labels_

st.subheader("Distribution par cluster")
fig = px.scatter_3d(rfm, x="recency", y="frequency", z="monetary", color="cluster", opacity=0.7)
st.plotly_chart(fig, use_container_width=True)

st.subheader("KPIs par cluster")
summary = rfm.groupby("cluster").agg(
    clients=("cluster","count"),
    recency_avg=("recency","mean"),
    freq_avg=("frequency","mean"),
    monetary_avg=("monetary","mean"),
    monetary_sum=("monetary","sum")
).round(2).reset_index()
st.dataframe(summary)