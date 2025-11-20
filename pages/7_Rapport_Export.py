import streamlit as st, pandas as pd, numpy as np
from io import BytesIO
from helpers import load_sessions, load_orders, load_spend

st.title("📄 Rapport & Export")

sessions = load_sessions()
orders = load_orders()
spend = load_spend()

dmin, dmax = sessions["date"].min(), sessions["date"].max()
d1, d2 = st.date_input("Période", [pd.to_datetime(dmin), pd.to_datetime(dmax)])

sess_f = sessions[sessions["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
ord_f  = orders[orders["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]
spend_f= spend[spend["date"].between(pd.to_datetime(d1), pd.to_datetime(d2))]

total_sessions = int(sess_f["sessions"].sum())
orders_count = int(len(ord_f))
revenue = float(ord_f["revenue"].sum())
spend_total = float(spend_f["spend"].sum())
conv_rate = (orders_count/total_sessions) if total_sessions>0 else 0.0
roas = (revenue/spend_total) if spend_total>0 else None
aov = (revenue/orders_count) if orders_count>0 else 0.0

st.subheader("Résumé automatique")
bullets = [
    f"• Sessions totales : {total_sessions:,}".replace(","," "),
    f"• Commandes : {orders_count:,}".replace(","," "),
    f"• Chiffre d'affaires : {revenue:,.0f} €".replace(","," "),
    f"• Taux de conversion : {conv_rate*100:.2f} %",
    f"• AOV : {aov:,.0f} €".replace(","," "),
    f"• Dépenses marketing (proxy) : {spend_total:,.0f} €".replace(","," "),
    f"• ROAS : {roas:.2f}" if roas is not None else "• ROAS : n/a"
]
st.write("\n".join(bullets))

st.subheader("Export Excel (commandes filtrées)")
output = BytesIO()
try:
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        ord_f.to_excel(writer, index=False, sheet_name="orders")
except Exception:
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        ord_f.to_excel(writer, index=False, sheet_name="orders")

st.download_button("Télécharger Excel", data=output.getvalue(),
                   file_name="orders_export.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("Pour PDF: ajoutez `pdfkit` ou `reportlab` selon votre environnement.")
