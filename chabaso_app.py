import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="CHABASO Pro", page_icon="🍞")
st.title("🍞 CHABASO Bakery Pro")

# Sidebar
page = st.sidebar.selectbox("Choose Action", ["🔍 Product Lookup", "➕ Add Product", "📊 Dashboard"])

# Demo data (replace with your Excel later)
@st.cache_data
def load_data():
    return pd.DataFrame({
        'product_code

