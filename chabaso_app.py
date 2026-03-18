import streamlit as st
import pandas as pd

st.title("🍞 CHABASO Bakery App")
st.write("Upload your DOUGH-PROD.xlsx to search products!")

uploaded_file = st.file_uploader("📁 Upload Excel", type=['xlsx'])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"✅ Loaded {len(df)} products!")
    st.dataframe(df.head())
else:
    st.info("👆 Please upload DOUGH-PROD.xlsx")
