import streamlit as st, pandas as pd, numpy as np
import plotly.express as px

from helpers import load_orders

st.title("👥 Cohortes & Rétention")

orders = load_orders()

# Simplification: 1er achat = date de cohort
first = orders.groupby("country")  # just to avoid warning; we compute globally
first_purchase = orders.groupby("country")  # placeholder

# Cohorte globale
first_purchase = orders.groupby("order_id").agg({"date":"min"})  # each order is unique; we need per customer id in real life
# For demo: we'll simulate a customer id by hashing (channel, country) buckets + noise
orders["_cust"] = (orders["country"] + "_" + orders["channel"]).astype(str) + "_" + (orders["order_id"]%2000).astype(str)
cust_first = orders.groupby("_cust")["date"].min().rename("cohort_date")
orders2 = orders.join(cust_first, on="_cust")
orders2["cohort_month"] = orders2["cohort_date"].dt.to_period("M").astype(str)
orders2["order_month"] = orders2["date"].dt.to_period("M").astype(str)

# Build retention table: unique customers per cohort & months since cohort
def retention_table(df):
    # Clients actifs par cohorte et mois de commande
    active = df.groupby(["cohort_month", "order_month"])["_cust"].nunique().reset_index()
    sizes = df.groupby("cohort_month")["_cust"].nunique().rename("cohort_size")
    active = active.join(sizes, on="cohort_month")

    # Calcul de l'index de période (écart en mois entre la commande et la cohorte)
    order_idx = pd.PeriodIndex(active["order_month"], freq="M")
    cohort_idx = pd.PeriodIndex(active["cohort_month"], freq="M")
    active["period_index"] = (12 * (order_idx.year - cohort_idx.year) + (order_idx.month - cohort_idx.month)).astype(int)

    # Pivot pour heatmap
    ret = active.pivot_table(index="cohort_month", columns="period_index", values="_cust", aggfunc="sum").fillna(0)
    ret = ret.div(sizes, axis=0).round(3)
    return ret

ret = retention_table(orders2)
st.subheader("Heatmap de rétention par cohorte (mois depuis 1er achat)")
fig = px.imshow(ret, aspect="auto", labels=dict(x="Mois depuis cohorte", y="Cohorte", color="Rétention"),
                color_continuous_scale="Blues")
st.plotly_chart(fig, use_container_width=True)
st.caption("NB : Dans la vraie vie, utilisez un identifiant client stable. Ici, nous en simulons un pour la démo.")