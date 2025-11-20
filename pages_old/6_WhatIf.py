import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend

st.title("🔧 What-if — Budget / Prix / Conversion")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

min_d, max_d = sessions["date"].min(), sessions["date"].max()
with st.sidebar:
    st.header("Périmètre")
    d1, d2 = st.date_input("Période", [min_d, max_d])

sess_f = sessions[sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
ord_f  = orders[orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
spend_f = spend[spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]

base_sessions = int(sess_f["sessions"].sum())
base_orders = len(ord_f)
base_revenue = float(ord_f["revenue"].sum())
base_spend = float(spend_f["spend"].sum())
base_cr = base_orders / base_sessions if base_sessions>0 else 0
base_aov = base_revenue / base_orders if base_orders>0 else 0

st.subheader("Hypothèses")
col1, col2, col3 = st.columns(3)
with col1:
    spend_delta = st.slider("Budget Marketing (Δ%)", -50, 100, 10, step=5)
with col2:
    price_delta = st.slider("Prix moyen / AOV (Δ%)", -20, 20, 0, step=1)
with col3:
    conv_delta = st.slider("Taux de conversion (Δ%)", -50, 50, 5, step=1)

# Simple response functions
new_spend = base_spend * (1 + spend_delta/100)
# Assume elasticity: sessions respond +0.6 to spend change
new_sessions = int(base_sessions * (1 + 0.6*spend_delta/100))
new_cr = base_cr * (1 + conv_delta/100)
new_orders = int(new_sessions * new_cr)
new_aov = base_aov * (1 + price_delta/100)
new_revenue = new_orders * new_aov

base = pd.DataFrame({
    "metric":["Sessions","Commandes","CA","Dépenses","ROAS"],
    "value":[base_sessions, base_orders, base_revenue, base_spend, (base_revenue/base_spend if base_spend>0 else None)]
})
scen = pd.DataFrame({
    "metric":["Sessions","Commandes","CA","Dépenses","ROAS"],
    "value":[new_sessions, new_orders, new_revenue, new_spend, (new_revenue/new_spend if new_spend>0 else None)]
})
comp = base.merge(scen, on="metric", suffixes=("_base","_scen"))
comp["delta"] = comp["value_scen"] - comp["value_base"]
comp["delta_pct"] = np.where(comp["value_base"]!=0, comp["delta"]/comp["value_base"]*100, np.nan)

st.subheader("Impact du scénario")
st.dataframe(comp)

fig = px.bar(comp, x="metric", y="delta_pct", text_auto=".1f", title="Δ% vs baseline")
st.plotly_chart(fig, use_container_width=True)