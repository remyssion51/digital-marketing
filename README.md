# App 1 — Marketing Analytics (Streamlit)

## Lancer l'app localement
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Datasets fournis (dans `data/`)
- `sessions.csv` — sessions par jour/pays/device/canal
- `orders.csv` — commandes avec revenu par commande
- `channels_spend.csv` — dépenses marketing quotidiennes par canal
- `ab_test.csv` — trafic et conversions variantes A/B (avril 2025)

## Pages clés
- Overview — KPI & tendances
- Acquisition & Attribution — performance par canal + attribution simple
- Cohortes & Rétention — heatmap de cohorte (1er achat)
- Segments & Scoring — RFM + KMeans (clients)
- A/B Testing — test statistique (p-value, IC)
- What-if — simulation budget/prix/taux de conversion
- Rapport & Export — résumé + export CSV/XLSX