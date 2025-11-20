import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend

st.title("📣 Acquisition & Attribution")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

# Filters
with st.sidebar:
    st.header("Filtres")
    min_d, max_d = sessions["date"].min(), sessions["date"].max()
    d1, d2 = st.date_input("Période", [min_d, max_d])
    channels = st.multiselect("Canaux", sorted(sessions["channel"].unique()), default=list(sessions["channel"].unique()))

sess_f = sessions[(sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (sessions["channel"].isin(channels))]
ord_f = orders[(orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (orders["channel"].isin(channels))]
spend_f = spend[(spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (spend["channel"].isin(channels))]

st.subheader("Funnel simple (sessions → commandes) par canal")
funnel = sess_f.groupby("channel", as_index=False)["sessions"].sum().merge(
    ord_f.groupby("channel", as_index=False)["revenue"].count().rename(columns={"revenue":"orders"}),
    on="channel", how="left").fillna(0)
funnel["conv_rate"] = np.where(funnel["sessions"]>0, funnel["orders"]/funnel["sessions"], 0)
fig = px.bar(funnel.sort_values("conv_rate", ascending=False), x="channel", y="conv_rate", text_auto=".1%")
st.plotly_chart(fig, use_container_width=True)

st.subheader("ROI par canal")
spend_ch = spend_f.groupby("channel", as_index=False)["spend"].sum()
rev_ch = ord_f.groupby("channel", as_index=False)["revenue"].sum()
mix = pd.merge(spend_ch, rev_ch, on="channel", how="outer").fillna(0)
mix["ROAS"] = np.where(mix["spend"]>0, mix["revenue"]/mix["spend"], None)
st.dataframe(mix)

st.info("Modèles d’attribution avancés (last-click, first-click, linéaire, time-decay) : pour la démo, on utilise l’attribution par **dernier canal connu** (proxy). Pour un vrai parcours multi-touch, chargez une table d'événements et appliquez les règles.")