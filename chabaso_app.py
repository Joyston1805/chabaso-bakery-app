import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    layout="wide", 
    page_title="CHABASO Bakery Pro",
    page_icon="🍞",
    initial_sidebar_state="expanded"
)

# Custom CSS for bakery theme
st.markdown("""
    <style>
    .main-header {color: #8B4513; font-size: 3rem; font-weight: bold;}
    .metric-card {background: linear-gradient(135deg, #F4A261 0%, #E76F51 100%); padding: 1rem; border-radius: 10px;}
    .product-card {background: #FFF9C4; padding: 1.5rem; border-radius: 15px; border-left: 5px solid #DDA0DD;}
    .stButton > button {background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border: none; color: white; padding: 0.5rem 2rem; border-radius: 25px;}
    </style>
""", unsafe_allow_html=True)

# Load data from multiple sheets
@st.cache_data
def load_chabaso_data():
    try:
        xl_file = pd.ExcelFile("DOUGH-PROD.xlsx")
        data = {}
        for sheet in xl_file.sheet_names:
            data[sheet] = pd.read_excel(xl_file, sheet_name=sheet)
        return data
    except:
        # Demo data if file not found
        return {
            "Products": pd.DataFrame({
                "product_code": ["DOUGH001", "DOUGH002"],
                "product_desc": ["Ciabatta", "Baguette"],
                "dough_code": ["CIA001", "BAG001"],
                "weight_g": [85, 120],
                "status": ["Active", "Active"]
            })
        }

# Main app
st.markdown('<h1 class="main-header">🍞 CHABASO Bakery Pro</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🍞 Bakery Control Panel")
page = st.sidebar.selectbox("Select Function", [
    "📊 Dashboard", 
    "🔍 Product Lookup", 
    "➕ Add Product", 
    "📝 Recipes & Specs", 
    "📈 Analytics"
])

data = load_chabaso_data()
main_df = data.get("Products", pd.DataFrame())

# Page 1: Dashboard
if page == "📊 Dashboard":
    st.header("📊 Bakery Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Products", len(main_df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        active = len(main_df[main_df['status'] == 'Active'])
        st.metric("Active Products", active)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        total_weight = main_df['weight_g'].sum()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Weight (g)", f"{total_weight:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sheets Loaded", len(data))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent products
    st.subheader("Latest Products")
    st.dataframe(main_df.tail(10), use_container_width=True)

# Page 2: Product Lookup
elif page == "🔍 Product Lookup":
    st.header("🔍 Instant Product Lookup")
    
    col1, col2 = st.columns(2)
    with col1:
        product_code = st.text_input("Enter Product Code", placeholder="DOUGH001")
    
    if product_code:
        # Search across all sheets
        found = False
        for sheet_name, df in data.items():
            if 'product_code' in df.columns:
                match = df[df['product_code'].astype(str).str.contains(product_code, case=False, na=False)]
                if not match.empty:
                    found = True
                    st.markdown(f"### 📄 Found in **{sheet_name}**")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        for idx, row in match.iterrows():
                            with st.expander(f"**{row.get('product_code', 'N/A')}** - {row.get('product_desc', 'N/A')}"):
                                for col, val in row.items():
                                    if pd.notna(val) and str(val).strip():
                                        st.write(f"**{col}:** {val}")
                    
                    with col2:
                        st.info("🖼️ Product photo goes here")
        
        if not found:
            st.warning("❌ Product code not found")

# Page 3: Add Product
elif page == "➕ Add Product":
    st.header("➕ Add New Bakery Product")
    
    with st.form("new_product"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_code = st.text_input("Product Code *", placeholder="DOUGH001")
            product_desc = st.text_input("Product Description *", placeholder="Ciabatta Rustica")
            dough_code = st.text_input("Dough Code", placeholder="CIA001")
        
        with col2:
            weight_g = st.number_input("Weight per piece (g)", min_value=1.0, value=85.0)
            status = st.selectbox("Status", ["Active", "Inactive", "Test"])
            category = st.selectbox("Category", ["Ciabatta", "Baguette", "Rolls", "Specialty"])
        
        # Recipe specs
        st.subheader("Recipe & Specifications")
        ingredients = st.text_area("Ingredients", placeholder="Flour 60%, Water 40%, Salt 2%, Yeast 1%")
        bake_time = st.text_input("Bake Time", placeholder="25-30 min @ 425°F")
        shelf_life = st.text_input("Shelf Life", placeholder="3 days")
        
        # Photo upload
        uploaded_photo = st.file_uploader("📸 Product Photo", type=['jpg', 'png'])
        
        submitted = st.form_submit_button("✅ Add Product", use_container_width=True)
        
        if submitted and product_code and product_desc:
            # Add to main dataframe
            new_row = pd.DataFrame({
                'product_code': [product_code],
                'product_desc
