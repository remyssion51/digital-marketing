import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_orders

st.title("👥 Cohortes & Rétention")

orders = load_orders().copy()

orders["_cust"] = (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders["order_id"]%2000).astype(str)) if "order_id" in orders.columns else                   (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders.index%2000).astype(str))

orders["cohort_month"] = orders.groupby("_cust")["date"].transform("min").dt.to_period("M").astype(str)
orders["order_month"]  = orders["date"].dt.to_period("M").astype(str)

def retention_table(df):
    active = df.groupby(["cohort_month","order_month"])["_cust"].nunique().reset_index()
    sizes = df.groupby("cohort_month")["_cust"].nunique().rename("cohort_size")
    active = active.join(sizes, on="cohort_month")
    order_idx = pd.PeriodIndex(active["order_month"], freq="M")
    cohort_idx = pd.PeriodIndex(active["cohort_month"], freq="M")
    active["period_index"] = (12*(order_idx.year - cohort_idx.year) + (order_idx.month - cohort_idx.month)).astype(int)
    ret = active.pivot_table(index="cohort_month", columns="period_index", values="_cust", aggfunc="sum").fillna(0)
    ret = ret.div(sizes, axis=0).round(3)
    return ret

ret = retention_table(orders)

st.subheader("Heatmap de rétention (0 = mois de cohorte)")
fig = px.imshow(ret, aspect="auto", labels=dict(x="Mois depuis cohorte", y="Cohorte", color="Rétention"),
                color_continuous_scale="Blues")
st.plotly_chart(fig, use_container_width=True)
st.caption("NB : identifiant client pseudo. Remplacez-le par un vrai `user_id` si disponible.")
