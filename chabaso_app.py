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

# ------------------ LOAD DATA -----------------

def load_data():  # NO CACHE - we need to see debug!
    st.write("🔍 **DEBUG: Checking files...**")
    
    # Show current directory
    current_dir = os.getcwd()
    st.write(f"📁 **Current directory:** `{current_dir}`")
    
    # List ALL files in repo root
    all_files = os.listdir('.')
    st.write("📋 **ALL FILES FOUND:**")
    for f in sorted(all_files):  # Sorted for consistency
        file_size = os.path.getsize(f) / 1024  # KB
        st.write(f"  - **{f}** ({file_size:.1f} KB)")
    
    # Check Excel specifically
    excel_path = "DOUGH-PROD.xlsx"
    file_exists = os.path.exists(excel_path)
    st.write(f"✅ **DOUGH-PROD.xlsx exists:** {file_exists}")
    
    if file_exists:
        file_size = os.path.getsize(excel_path) / 1024
        st.write(f"📊 **File size:** {file_size:.1f} KB")
    
    if not file_exists:
        st.error("❌ DOUGH-PROD.xlsx MISSING!")
        st.info("💡 Push it to GitHub repo root (same level as app.py)")
        return pd.DataFrame()
    
    try:
        st.info("📖 Reading Excel...")
        df = pd.read_excel("DOUGH-PROD.xlsx", sheet_name="ML")
        df.columns = df.columns.str.strip()
        st.success(f"✅ **LOADED {len(df)} ROWS** from {len(df.columns)} columns!")
        st.write("**First 3 rows:**")
        st.dataframe(df.head(3))
        return df
    except Exception as e:
        st.error(f"❌ **Excel Error:** {str(e)}")
        st.write("**Column names found:**", list(df.columns) if 'df' in locals() else "None")
        return pd.DataFrame()


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
    
    if "Prod_Status" in df.columns:
        col2.metric("Active Products", len(df[df["Prod_Status"] == "Active"]))
    else:
        col2.metric("Active Products", "N/A")

    if "cutwt_per_pc_g" in df.columns:
        col3.metric("Avg Weight (g)", round(df["cutwt_per_pc_g"].mean(), 2))
    else:
        col3.metric("Avg Weight", "N/A")

    st.dataframe(df, use_container_width=True)

# ------------------ LOOKUP ------------------
elif page == "🔍 Product Lookup":
    st.header("🔍 Product Lookup")

    search = st.text_input("Search by Product Code or Dough Code")

    if search and not df.empty:
        results = df[
            df["product_code"].astype(str).str.contains(search, case=False, na=False) |
            df["dough_code"].astype(str).str.contains(search, case=False, na=False)
        ]

        if not results.empty:
            for _, row in results.iterrows():
                col1, col2 = st.columns([2,1])

                with col1:
                    st.subheader(row.get("product_desc", "N/A"))

                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and str(val).strip() != "":
                            st.write(f"**{col}:** {val}")

                with col2:
                    img = get_image_path(row.get("product_desc"))
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.info("No image found")

        else:
            st.warning("❌ No match found")

# ------------------ ADD PRODUCT ------------------
elif page == "➕ Add Product":
    st.header("➕ Add Product")

    with st.form("form"):
        inputs = {}

        for col in df.columns:
            inputs[col] = st.text_input(col)

        photo = st.file_uploader("Upload Product Image", type=["jpg","jpeg","png"])

        submit = st.form_submit_button("Add Product")

        if submit:
            new_row = pd.DataFrame([inputs])

            # Save image
            if photo and inputs.get("product_desc"):
                ext = photo.name.split('.')[-1].lower()
                if ext == "jpeg":
                    ext = "jpg"

                filepath = os.path.join(IMAGE_FOLDER, f"{inputs['product_desc']}.{ext}")

                with open(filepath, "wb") as f:
                    f.write(photo.getbuffer())

            updated_df = pd.concat([df, new_row], ignore_index=True)
            save_data(updated_df)

            st.success("✅ Product added successfully!")
