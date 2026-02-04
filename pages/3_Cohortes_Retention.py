import streamlit as st, pandas as pd, numpy as np
import plotly.express as px
from helpers import load_orders

st.title("👥 Cohortes & Rétention")

orders = load_orders().copy()

orders["_cust"] = (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders["user_id"]%2000).astype(str)) if "user_id" in orders.columns else                   (orders["country"].astype(str) + "_" + orders["channel"].astype(str) + "_" + (orders.index%2000).astype(str))

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

st.markdown("""

Pour lire la heatmap, chaque ligne correspond à une **cohorte de clients** qui font leur première commande.
Chaque colonne représente le **nombre de mois écoulés** depuis cette première commande.

- **M0** = mois du premier achat (100% par définition)
- **M1** = % de ces clients revenus acheter le mois suivant
- **M2** = % revenus deux mois après
- etc.

Plus la case est foncée, plus la proportion de clients qui reviennent est élevée.

---

On observe que des clients continuent d’acheter pendant **de très nombreux mois** et même que la retention semble augmenter après le premier mois.
Or, dans la réalité du retail :
- la majorité des clients n’achètent **qu’une seule fois**
- la rétention chute très vite après 2–3 mois
- après 1 an, presque aucun client ne revient

Ces données proviennent d’un dataset pédagogique où le comportement des utilisateurs
a été simulé pour faciliter les analyses, et non pour reproduire fidèlement
le comportement réel d’acheteurs de vêtements.
La heatmap est donc **mathématiquement correcte**, mais **business irréaliste**.
""")

