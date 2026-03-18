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

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    if not os.path.exists("DOUGH-PROD.xlsx"):
        return pd.DataFrame()

    df = pd.read_excel("DOUGH-PROD.xlsx", sheet_name="ML")

    # Clean column names (strip spaces)
    df.columns = df.columns.str.strip()

    return df

def save_data(df):
    with pd.ExcelWriter("DOUGH-PROD.xlsx", engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, sheet_name="ML", index=False)

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
