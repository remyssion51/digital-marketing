import streamlit as st
import pandas as pd
import numpy as np

DATA_DIR = "new_data"

@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    path = f"{DATA_DIR}/{name}.csv"
    df = pd.read_csv(path)
    # auto parse dates if column names = date / created_at
    for col in df.columns:
        if col.lower() in ("date","created_at","order_date"):
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
    return df

def load_sessions():
    return load_csv("sessions")

def load_orders():
    return load_csv("orders")

def load_spend():
    return load_csv("channel_spend")

def load_ab_paid_organic():
    return load_csv("AB_testing_Paid_Organic")

def load_ab_safari_chrome():
    return load_csv("AB_testing_Safari_Chrome")

def money(x):
    try:
        return f"{x:,.0f} €".replace(",", " ")
    except:
        return f"{x} €"

def kpi(label, value, suffix=""):
    try:
        st.metric(label, f"{value:,.0f}{suffix}".replace(",", " "))
    except:
        st.metric(label, f"{value}{suffix}")
