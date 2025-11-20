import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend

st.title("🔧 What-if — Budget / Prix / Conversion")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

dmin, dmax = sessions["date"].min(), sessions["date"].max()
with st.sidebar:
    st.header("Périmètre")
    d1, d2 = st.date_input("Période", [pd.to_datetime(dmin), pd.to_datetime(dmax)])

sess_f = sessions[sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
ord_f  = orders[orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
spend_f= spend[spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]

base_sessions = int(sess_f["sessions"].sum())
base_orders   = int(len(ord_f))
base_revenue  = float(ord_f["revenue"].sum())
base_spend    = float(spend_f["spend"].sum())
base_cr = base_orders/base_sessions if base_sessions>0 else 0
base_aov = base_revenue/base_orders if base_orders>0 else 0

st.subheader("Hypothèses")
c1,c2,c3 = st.columns(3)
with c1:
    spend_delta = st.slider("Budget (Δ%)", -50, 100, 10, step=5)
with c2:
    price_delta = st.slider("AOV (Δ%)", -20, 20, 0, step=1)
with c3:
    conv_delta = st.slider("CR (Δ%)", -50, 50, 5, step=1)

new_spend = base_spend * (1 + spend_delta/100)
new_sessions = int(base_sessions * (1 + 0.6*spend_delta/100))
new_cr = base_cr * (1 + conv_delta/100)
new_orders = int(new_sessions * new_cr)
new_aov = base_aov * (1 + price_delta/100)
new_revenue = new_orders * new_aov

base = pd.DataFrame({"metric":["Sessions","Commandes","CA","Dépenses","ROAS"],
                     "value":[base_sessions, base_orders, base_revenue, base_spend, (base_revenue/base_spend if base_spend>0 else None)]})
scen = pd.DataFrame({"metric":["Sessions","Commandes","CA","Dépenses","ROAS"],
                     "value":[new_sessions, new_orders, new_revenue, new_spend, (new_revenue/new_spend if new_spend>0 else None)]})
comp = base.merge(scen, on="metric", suffixes=("_base","_scen"))
comp["delta_%"] = np.where(comp["value_base"]!=0, (comp["value_scen"]-comp["value_base"])/comp["value_base"]*100, np.nan)

st.subheader("Impact du scénario")
st.dataframe(comp, use_container_width=True)
st.plotly_chart(px.bar(comp, x="metric", y="delta_%", text_auto=".1f", title="Δ% vs baseline"), use_container_width=True)
