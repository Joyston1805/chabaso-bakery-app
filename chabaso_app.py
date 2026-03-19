import streamlit as st
import pandas as pd
import os

# ------------------ CONFIG ------------------
st.set_page_config(
    layout="wide",
    page_title="CHABASO Bakery Pro",
    page_icon="🍞"
)

IMAGE_FOLDER = "Product Photos"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ------------------ STYLING ------------------
st.markdown("""
<style>
.main-header {color: #8B4513; font-size: 3rem; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ------------------ IMAGE MATCH ------------------
def get_image_path(product_desc):
    if not product_desc:
        return None
    for ext in ["jpg", "jpeg", "png"]:
        path = os.path.join(IMAGE_FOLDER, f"{product_desc}.{ext}")
        if os.path.exists(path):
            return path
    return None

# ------------------ SAFE SAVE DATA ------------------
def save_data(df):
    try:
        with pd.ExcelWriter("DOUGH-PROD.xlsx", engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name="ML", index=False)
        st.success("✅ Data saved!")
    except:
        st.error("❌ Save failed (works locally only)")

# ------------------ SAFE LOAD DATA ------------------
@st.cache_data
def load_data():
    """Load with full safety - NO CRASHES"""
    try:
        if not os.path.exists("DOUGH-PROD.xlsx"):
            st.warning("⚠️ DOUGH-PROD.xlsx not found - Using test data")
            return create_test_data()
        
        df = pd.read_excel("DOUGH-PROD.xlsx", sheet_name="ML")
        
        # **FIX: Remove duplicate columns**
        df.columns = pd.Index([str(col).strip() for col in df.columns])
        # Keep only unique column names
        df = df.loc[:, ~df.columns.duplicated()]
        
        df.columns = df.columns.str.strip()
        
        if df.empty:
            st.warning("⚠️ Empty Excel - Using test data")
            return create_test_data()
            
        st.success(f"✅ Loaded {len(df)} products")
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Load failed - Using test data")
        return create_test_data()

def create_test_data():
    """Emergency test data - always works"""
    df = pd.DataFrame({
        'product_code': ['CB001', 'BG002', 'BR003', 'SF004'],
        'dough_code': ['DCB1', 'DBG1', 'DBR1', 'DSF1'],
        'product_desc': ['Ciabatta Loaf', 'Classic Baguette', 'Brioche Roll', 'Sourdough'],
        'cutwt_per_pc_g': [250, 180, 75, 200],
        'Prod_Status': ['Active', 'Active', 'Active', 'Active']
    })
    st.info("🧪 Using test data (4 bakery products)")
    return df

# ------------------ LOAD DATA FIRST ------------------
df = load_data()

# ------------------ HEADER ------------------
st.markdown('<h1 class="main-header">🍞 CHABASO Bakery Pro</h1>', unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
page = st.sidebar.selectbox("Navigate", [
    "📊 Dashboard",
    "🔍 Product Lookup", 
    "➕ Add Product"
])

# ------------------ DASHBOARD ------------------
if page == "📊 Dashboard":
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(df))
    
    active_count = len(df[df["Prod_Status"] == "Active"]) if "Prod_Status" in df.columns else 0
    col2.metric("Active Products", active_count)
    
    avg_weight = round(df["cutwt_per_pc_g"].mean(), 2) if "cutwt_per_pc_g" in df.columns else 0
    col3.metric("Avg Weight (g)", avg_weight)
    
    # **FIX: Safe dataframe display**
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No data to display")

# ------------------ LOOKUP ------------------
elif page == "🔍 Product Lookup":
    st.header("🔍 Product Lookup")
    
    search = st.text_input("🔍 Search by Product Code or Dough Code")
    
    if search and not df.empty:
        mask1 = df["product_code"].astype(str).str.contains(search, case=False, na=False)
        mask2 = df["dough_code"].astype(str).str.contains(search, case=False, na=False)
        results = df[mask1 | mask2]
        
        if not results.empty:
            for _, row in results.iterrows():
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(row.get("product_desc", "N/A"))
                    # **FIX: Ultra-safe display**
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val):
                            display_val = str(val) if pd.api.types.is_numeric_dtype(row[col]) else val
                            st.write(f"**{col}:** {display_val}")
                
                with col2:
                    img = get_image_path(row.get("product_desc"))
                    if img and os.path.exists(img):
                        st.image(img, use_container_width=True)
                    else:
                        st.info("🖼️ No image")
        else:
            st.warning("❌ No products match your search")
    elif df.empty:
        st.warning("⚠️ No data loaded")
    else:
        st.info("👆 Enter code to search")

# ------------------ ADD PRODUCT ------------------
elif page == "➕ Add Product":
    st.header("➕ Add Product")
    
    with st.form("product_form"):
        inputs = {}
        
        known_cols = ['product_code', 'dough_code', 'product_desc', 'cutwt_per_pc_g', 'Prod_Status']
        for col in known_cols:
            inputs[col] = st.text_input(col, placeholder=f"Enter {col}")
        
        photo = st.file_uploader("🖼️ Product Image", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("➕ Add Product")
        
        if submitted:
            new_row = pd.DataFrame([inputs])
            
            if photo and inputs.get("product_desc"):
                ext = photo.name.split('.')[-1].lower()
                if ext == "jpeg": 
                    ext = "jpg"
                filepath = os.path.join(IMAGE_FOLDER, f"{inputs['product_desc']}.{ext}")
                with open(filepath, "wb") as f:
                    f.write(photo.getbuffer())
                st.success(f"🖼️ Image saved!")
            
            if not df.empty:
                updated_df = pd.concat([df, new_row], ignore_index=True)
            else:
                updated_df = new_row
            
            save_data(updated_df)
            st.success("✅ Product added!")
            st.rerun()
