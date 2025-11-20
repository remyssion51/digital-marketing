import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
import plotly.express as px
from helpers import load_ab_safari_chrome

st.title("🧪 A/B Testing — Safari vs Chrome")

# chargement unique
ab = load_ab_safari_chrome()

# sécurité colonnes
missing = [c for c in ["date","variant","visitors","conversions"] if c not in ab.columns]
if missing:
    st.error(f"Colonnes manquantes dans AB_testing_Safari_Chrome.csv: {missing}")
    st.stop()

with st.sidebar:
    st.header("Paramètres")
    alpha = st.slider("Niveau de signification (α)", 0.01, 0.10, 0.05, step=0.01)

ab["date"] = pd.to_datetime(ab["date"])
agg = ab.groupby("variant").agg(visitors=("visitors","sum"),
                                conversions=("conversions","sum")).reset_index()

# il faut 2 variantes
if len(agg) < 2:
    st.error("Le fichier ne contient pas 2 variantes (A & B).")
    st.stop()

# ordonner (A puis B)
agg = agg.sort_values("variant")
count = agg["conversions"].values
nobs  = agg["visitors"].values

# test
z, pval = proportions_ztest(count, nobs)
st.metric("Stat Z", f"{z:.2f}")
st.metric("p-value", f"{pval:.4f}")

# meilleure variante
agg["cr"] = agg["conversions"] / agg["visitors"]
best = agg.sort_values("cr", ascending=False).iloc[0]["variant"]

st.success(f"Variante **{best}** a le meilleur taux de conversion. " +
           ("Différence significative ✅" if pval < alpha else "Pas significatif ❌"))

# courbe CR journalière
daily = ab.assign(cr=lambda x: x["conversions"] / x["visitors"])
st.plotly_chart(px.line(daily, x="date", y="cr", color="variant", markers=True),
                use_container_width=True)

