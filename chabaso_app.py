import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide", page_title="CHABASO Pro", page_icon="🍞")
st.markdown("""
<style>
.main-header {color: #8B4513; text-align: center; font-size: 3.5rem;}
.product-card {background: linear-gradient(135deg, #FFF9C4 0%, #F8E8A8 100%); padding: 2rem; border-radius: 20px; margin: 1rem 0;}
.stButton >
