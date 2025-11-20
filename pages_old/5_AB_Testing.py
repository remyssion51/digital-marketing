import streamlit as st, pandas as pd, numpy as np
from statsmodels.stats.proportion import proportions_ztest
import plotly.express as px
from helpers import load_ab

st.title("🧪 A/B Testing — Conversion")

ab = load_ab()

with st.sidebar:
    st.header("Paramètres")
    alpha = st.slider("Niveau de signification (α)", 0.01, 0.10, 0.05, step=0.01)

agg = ab.groupby("variant").agg(visitors=("visitors","sum"), conversions=("conversions","sum")).reset_index()
st.write("Résumé A/B", agg)

# z-test for two proportions
count = agg["conversions"].values
nobs = agg["visitors"].values
stat, pval = proportions_ztest(count, nobs)
st.metric("Stat Z", f"{stat:.2f}")
st.metric("p-value", f"{pval:.4f}")
better = "B" if agg.loc[agg["variant"]=="B","conversions"].values[0]/agg.loc[agg["variant"]=="B","visitors"].values[0] > \
               agg.loc[agg["variant"]=="A","conversions"].values[0]/agg.loc[agg["variant"]=="A","visitors"].values[0] else "A"
st.success(f"Variante **{better}** a le meilleur taux de conversion global. " + ("Différence statistiquement significative ✅" if pval < alpha else "Pas significatif ❌"))

# Daily plot
daily = ab.assign(cr=lambda x: x["conversions"]/x["visitors"])
fig = plot = px.line(daily, x="date", y="cr", color="variant", markers=True)
st.plotly_chart(fig, use_container_width=True)