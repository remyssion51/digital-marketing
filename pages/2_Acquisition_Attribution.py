import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend

st.title("📣 Acquisition & Attribution — funnel & ROAS")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

with st.sidebar:
    st.header("Filtres")
    dmin, dmax = sessions["date"].min(), sessions["date"].max()
    d1, d2 = st.date_input("Période", [pd.to_datetime(dmin), pd.to_datetime(dmax)])
    channels = st.multiselect("Channel", sorted(sessions["channel"].unique().tolist()),
                              default=sorted(sessions["channel"].unique().tolist()))

sess_f = sessions[(sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (sessions["channel"].isin(channels))]
ord_f  = orders[(orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (orders["channel"].isin(channels))]
spend_f= spend[(spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))) & (spend["channel"].isin(channels))]

st.subheader("Funnel simple (sessions → commandes) par channel")
funnel = sess_f.groupby("channel", as_index=False)["sessions"].sum().merge(
    ord_f.groupby("channel", as_index=False)["revenue"].count().rename(columns={"revenue":"orders"}),
    on="channel", how="left"
).fillna(0)
funnel["conv_rate"] = np.where(funnel["sessions"]>0, funnel["orders"]/funnel["sessions"], 0)
st.plotly_chart(px.bar(funnel.sort_values("conv_rate", ascending=False), x="channel", y="conv_rate", text_auto=".1%"),
                use_container_width=True)

st.subheader("ROAS par channel")
sp = spend_f.groupby("channel", as_index=False)["spend"].sum()
rv = ord_f.groupby("channel", as_index=False)["revenue"].sum()
mix = pd.merge(sp, rv, on="channel", how="outer").fillna(0)
mix["ROAS"] = np.where(mix["spend"]>0, mix["revenue"]/mix["spend"], None)
st.dataframe(mix.sort_values("revenue", ascending=False), use_container_width=True)

st.caption("Attribution avancée (multi-touch) possible si vous exportez des parcours événementiels complets.")
