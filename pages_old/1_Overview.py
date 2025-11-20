import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend, month_period, kpi_card, money

st.title("🏠 Overview — KPI & Tendances")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

# Filters
with st.sidebar:
    st.header("Filtres")
    min_d, max_d = sessions["date"].min(), sessions["date"].max()
    d1, d2 = st.date_input("Période", [min_d, max_d])
    channels = st.multiselect("Canaux", sorted(sessions["channel"].unique()), default=list(sessions["channel"].unique()))
    countries = st.multiselect("Pays", sorted(sessions["country"].unique()), default=["FR","DE","UK"])
    devices = st.multiselect("Device", sorted(sessions["device"].unique()), default=["desktop","mobile"])

mask = (
    (sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) &
    (sessions["channel"].isin(channels)) &
    (sessions["country"].isin(countries)) &
    (sessions["device"].isin(devices))
)
sess_f = sessions.loc[mask]
ord_f = orders.loc[orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2)) &
                   orders["channel"].isin(channels) &
                   orders["country"].isin(countries) &
                   orders["device"].isin(devices)]
spend_f = spend.loc[(spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) &
                    (spend["channel"].isin(channels))]

# KPIs
total_sessions = int(sess_f["sessions"].sum())
orders_count = len(ord_f)
revenue = float(ord_f["revenue"].sum())
conv_rate = orders_count / total_sessions if total_sessions>0 else 0
spend_total = float(spend_f["spend"].sum())
roas = (revenue / spend_total) if spend_total>0 else None
aov = (revenue / orders_count) if orders_count>0 else 0

c1,c2,c3,c4,c5 = st.columns(5)
with c1: kpi_card("Sessions", total_sessions)
with c2: kpi_card("Commandes", orders_count)
with c3: kpi_card("CA", revenue, " €")
with c4: kpi_card("Conversion", conv_rate*100, " %")
with c5: kpi_card("AOV", aov, " €")

# Timeseries revenue
rev_ts = ord_f.groupby("date", as_index=False)["revenue"].sum()
st.subheader("Revenu quotidien")
fig = px.line(rev_ts, x="date", y="revenue", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Sessions by channel
st.subheader("Sessions par canal")
s_by_ch = sess_f.groupby("channel", as_index=False)["sessions"].sum().sort_values("sessions", ascending=False)
fig2 = px.bar(s_by_ch, x="channel", y="sessions", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Spend vs Revenue by channel
st.subheader("Revenu & Dépense par canal")
spend_ch = spend_f.groupby("channel", as_index=False)["spend"].sum()
rev_ch = ord_f.groupby("channel", as_index=False)["revenue"].sum()
mix = pd.merge(spend_ch, rev_ch, on="channel", how="outer").fillna(0)
mix = mix.sort_values("revenue", ascending=False)
fig3 = px.bar(mix.melt(id_vars="channel", value_vars=["revenue","spend"],
                       var_name="type", value_name="amount"),
              x="channel", y="amount", color="type", barmode="group", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

st.caption("Astuce : remplacez les CSV dans `data/` par vos propres exports analytics pour une démo réaliste.")