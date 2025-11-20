import streamlit as st
import datetime as dt

st.set_page_config(page_title="Marketing Analytics v2", page_icon="📈", layout="wide")

# --- Filtre global partagé ---
if "start_date" not in st.session_state:
    st.session_state.start_date = dt.date(2022, 1, 1)
if "end_date" not in st.session_state:
    st.session_state.end_date = dt.date(2024, 12, 31)

with st.sidebar:
    st.header("Filtre Date Global")
    start, end = st.date_input(
        "Période (global)",
        value=(st.session_state.start_date, st.session_state.end_date),
        min_value=dt.date(2022,1,1),
        max_value=dt.date(2024,12,31),
        key="global_date_filter"
    )
    st.session_state.start_date = start
    st.session_state.end_date = end

# petit rappel visuel utile
st.caption(f"Période active : **{st.session_state.start_date} → {st.session_state.end_date}**")
