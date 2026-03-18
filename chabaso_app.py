import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="CHABASO Pro", page_icon="🍞")
st.title("🍞 CHABASO Bakery Management System")

# Sidebar menu
page = st.sidebar.selectbox("Select Function", [
    "🔍 Product Lookup", 
    "➕ Add Product", 
    "📊 Dashboard", 
    "📈 Reports"
])

# Demo data - replace with your Excel upload later
@st.cache_data
def get_data():
    return pd.DataFrame({
        'product_code': ['DOUGH001
