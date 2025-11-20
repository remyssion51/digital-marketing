import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend, kpi, money

st.title("🏠 Overview — KPI & Tendances (country + channel + browser)")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

# Required columns check
for df, name, cols in [
    (sessions,"sessions",["date","country","channel","browser","sessions"]),
    (orders,"orders",["date","country","channel","browser","revenue"]),
    (spend,"channel_spend",["date","channel","spend"])
]:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        st.error(f"Fichier `{name}`: colonnes manquantes {missing}")
        st.stop()

# Filters
with st.sidebar:
    st.header("Filtres")
    dmin, dmax = sessions["date"].min(), sessions["date"].max()
    d1, d2 = st.date_input("Période", [pd.to_datetime(dmin), pd.to_datetime(dmax)])
    countries = st.multiselect("Country", sorted(sessions["country"].dropna().unique().tolist()),
                               default=sorted(sessions["country"].dropna().unique().tolist()))
    channels = st.multiselect("Channel", sorted(sessions["channel"].dropna().unique().tolist()),
                              default=sorted(sessions["channel"].dropna().unique().tolist()))
    browsers = st.multiselect("Browser", sorted(sessions["browser"].dropna().unique().tolist()),
                              default=sorted(sessions["browser"].dropna().unique().tolist()))

mask_s = (
    sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2)) &
    sessions["country"].isin(countries) &
    sessions["channel"].isin(channels) &
    sessions["browser"].isin(browsers)
)
sess_f = sessions.loc[mask_s].copy()

mask_o = (
    orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2)) &
    orders["country"].isin(countries) &
    orders["channel"].isin(channels) &
    orders["browser"].isin(browsers)
)
ord_f = orders.loc[mask_o].copy()

spend_f = spend.loc[spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2)) & spend["channel"].isin(channels)].copy()

# KPIs
total_sessions = int(sess_f["sessions"].sum()) if len(sess_f) else 0
orders_count = int(len(ord_f))
revenue = float(ord_f["revenue"].sum()) if len(ord_f) else 0.0
conv_rate = (orders_count/total_sessions) if total_sessions>0 else 0.0
spend_total = float(spend_f["spend"].sum()) if len(spend_f) else 0.0
roas = (revenue/spend_total) if spend_total>0 else None
aov = (revenue/orders_count) if orders_count>0 else 0.0

c1,c2,c3,c4,c5 = st.columns(5)
with c1: kpi("Sessions", total_sessions)
with c2: kpi("Commandes", orders_count)
with c3: kpi("CA", revenue, " €")
with c4: kpi("Conversion", conv_rate*100, " %")
with c5: kpi("AOV", aov, " €")

st.subheader("Revenu quotidien")
rev_ts = ord_f.groupby("date", as_index=False)["revenue"].sum()
if len(rev_ts):
    st.plotly_chart(px.line(rev_ts, x="date", y="revenue", markers=True), use_container_width=True)
else:
    st.warning("Pas de données pour la période sélectionnée.")

st.subheader("Sessions par channel")
s_by_ch = sess_f.groupby("channel", as_index=False)["sessions"].sum().sort_values("sessions", ascending=False)
st.plotly_chart(px.bar(s_by_ch, x="channel", y="sessions", text_auto=True), use_container_width=True)

st.subheader("Revenue & Spend par channel")
sp_ch = spend_f.groupby("channel", as_index=False)["spend"].sum()
rv_ch = ord_f.groupby("channel", as_index=False)["revenue"].sum()
mix = pd.merge(sp_ch, rv_ch, on="channel", how="outer").fillna(0)
mix = mix.sort_values("revenue", ascending=False)
st.plotly_chart(
    px.bar(mix.melt(id_vars="channel", value_vars=["revenue","spend"], var_name="type", value_name="amount"),
           x="channel", y="amount", color="type", barmode="group", text_auto=True),
    use_container_width=True
)
