import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_sessions, load_orders, load_spend

st.title("🏠 Overview — KPI & Tendances")

sessions = load_sessions()
orders   = load_orders()
spend    = load_spend()

# --- GLOBAL FILTER (depuis app.py)
start = st.session_state.start_date
end   = st.session_state.end_date
start_dt = pd.to_datetime(start)
end_dt   = pd.to_datetime(end)

with st.sidebar:
    st.header("Filtres (dimensions)")
    countries = st.multiselect("Country",
                               sorted(sessions["country"].dropna().unique()),
                               default=sorted(sessions["country"].dropna().unique()),
                               key="ov_countries")
    channels  = st.multiselect("Channel",
                               sorted(sessions["channel"].dropna().unique()),
                               default=sorted(sessions["channel"].dropna().unique()),
                               key="ov_channels")
    browsers  = st.multiselect("Browser",
                               sorted(sessions["browser"].dropna().unique()),
                               default=sorted(sessions["browser"].dropna().unique()),
                               key="ov_browsers")

# --- FILTRAGE
sess_f = sessions[(sessions["date"].between(start_dt, end_dt)) &
                  (sessions["country"].isin(countries)) &
                  (sessions["channel"].isin(channels)) &
                  (sessions["browser"].isin(browsers))]

ord_f  = orders[(orders["date"].between(start_dt, end_dt)) &
                (orders["country"].isin(countries)) &
                (orders["channel"].isin(channels)) &
                (orders["browser"].isin(browsers))]

spend_f= spend[(spend["date"].between(start_dt, end_dt)) &
               (spend["channel"].isin(channels))]


# --- FORMAT k/M
def km(v: float):
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"{v/1_000:.0f}k"
    return f"{v:.0f}"

# --- KPIs
total_sessions = sess_f["sessions"].sum()
orders_count   = len(ord_f)
revenue        = ord_f["revenue"].sum()
conv_rate      = (orders_count/total_sessions) if total_sessions>0 else 0
spend_total    = spend_f["spend"].sum()
roas           = revenue/spend_total if spend_total>0 else None
aov            = revenue/orders_count if orders_count>0 else 0

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("Sessions", km(total_sessions))
with c2: st.metric("Commandes", km(orders_count))
with c3: st.metric("CA", km(revenue)+"€")
with c4: st.metric("Conversion", f"{conv_rate*100:.2f}%")
with c5: st.metric("AOV", km(aov)+"€")


# ==============================
#  GRAPH 1 : TREND30D SEULE
# ==============================
st.subheader("Revenu quotidien — Trendline 30j")

ts = ord_f.groupby("date",as_index=False)["revenue"].sum()
if len(ts):
    ts = ts.sort_values("date")
    ts["trend30d"] = ts["revenue"].rolling(30).mean()
    fig = px.line(ts,x="date",y="trend30d")
    fig.update_layout(yaxis_title="Revenu moy. 30j")
    st.plotly_chart(fig,use_container_width=True)
else:
    st.warning("Pas de données pour la période sélectionnée.")


# ==============================
#  GRAPH 2 : SESSIONS / CHANNEL
# ==============================
st.subheader("Sessions par channel")
s_by_ch = sess_f.groupby("channel",as_index=False)["sessions"].sum().sort_values("sessions",ascending=False)
fig2 = px.bar(s_by_ch,x="channel",y="sessions",text=s_by_ch["sessions"].apply(km))
fig2.update_traces(textposition="outside")
fig2.update_layout(uniformtext_minsize=10, uniformtext_mode='show')
st.plotly_chart(fig2,use_container_width=True)


# ==============================
#  GRAPH 3 : REVENUE vs SPEND
# ==============================
st.subheader("Revenu & Spend par channel")
sp_ch = spend_f.groupby("channel",as_index=False)["spend"].sum()
rv_ch = ord_f.groupby("channel",as_index=False)["revenue"].sum()
mix = pd.merge(sp_ch,rv_ch,on="channel",how="outer").fillna(0).sort_values("revenue",ascending=False)

mix_long = mix.melt(id_vars="channel",value_vars=["revenue","spend"],var_name="type",value_name="amount")
fig3 = px.bar(mix_long,x="channel",y="amount",color="type",barmode="group",text=mix_long["amount"].apply(km))
fig3.update_traces(textposition="outside")
fig3.update_layout(uniformtext_minsize=10,uniformtext_mode='show')
st.plotly_chart(fig3,use_container_width=True)