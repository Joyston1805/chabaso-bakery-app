import streamlit as st
import pandas as pd
import os

# ------------------ CONFIG ------------------
st.set_page_config(
    layout="wide",
    page_title="CHABASO Bakery Pro",
    page_icon="🍞"
)

IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ------------------ STYLING ------------------
st.markdown("""
<style>
.main-header {color: #8B4513; font-size: 3rem; font-weight: bold;}
.metric-card {background: linear-gradient(135deg, #F4A261 0%, #E76F51 100%); padding: 1rem; border-radius: 10px;}
.stButton > button {background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border: none; color: white; border-radius: 25px;}
</style>
""", unsafe_allow_html=True)

# ------------------ IMAGE MATCHING ------------------
def get_image_path(product_desc):
    if not product_desc:
        return None

    # Prioritize JPG since your files are JPG
    for ext in ["jpg", "jpeg", "png"]:
        path = os.path.join(IMAGE_FOLDER, f"{product_desc}.{ext}")
        if os.path.exists(path):
            return path

    return None

# ------------------ DATA ------------------
@st.cache_data
def load_data():
    if os.path.exists("DOUGH-PROD.xlsx"):
        return pd.read_excel("DOUGH-PROD.xlsx")
    else:
        return pd.DataFrame(columns=[
            "product_code","product_desc","dough_code",
            "weight_g","status","category",
            "ingredients","bake_time","shelf_life"
        ])

def save_data(df):
    df.to_excel("DOUGH-PROD.xlsx", index=False)

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
    st.header("📊 Bakery Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Products", len(df))
    col2.metric("Active Products", len(df[df['status'] == 'Active']))
    col3.metric("Total Weight (g)", int(df['weight_g'].sum()) if not df.empty else 0)

    st.subheader("All Products")
    st.dataframe(df, use_container_width=True)

# ------------------ LOOKUP ------------------
elif page == "🔍 Product Lookup":
    st.header("🔍 Product Lookup")

    search = st.text_input("Search by Product Code or Dough Code")

    if search:
        results = df[
            df['product_code'].astype(str).str.contains(search, case=False, na=False) |
            df['dough_code'].astype(str).str.contains(search, case=False, na=False)
        ]

        if not results.empty:
            for _, row in results.iterrows():
                col1, col2 = st.columns([2,1])

                with col1:
                    st.subheader(row['product_desc'])
                    st.write(f"**Product Code:** {row['product_code']}")
                    st.write(f"**Dough Code:** {row['dough_code']}")
                    st.write(f"**Weight:** {row['weight_g']} g")
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Ingredients:** {row.get('ingredients','')}")
                    st.write(f"**Bake Time:** {row.get('bake_time','')}")
                    st.write(f"**Shelf Life:** {row.get('shelf_life','')}")

                with col2:
                    img = get_image_path(row['product_desc'])
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.info("No image found")

        else:
            st.warning("❌ No products found")

# ------------------ ADD PRODUCT ------------------
elif page == "➕ Add Product":
    st.header("➕ Add Product")

    with st.form("form"):
        col1, col2 = st.columns(2)

        with col1:
            product_code = st.text_input("Product Code *")
            product_desc = st.text_input("Product Name *")
            dough_code = st.text_input("Dough Code")

        with col2:
            weight_g = st.number_input("Weight (g)", value=85.0)
            status = st.selectbox("Status", ["Active","Inactive","Test"])
            category = st.selectbox("Category", ["Ciabatta","Baguette","Rolls","Other"])

        ingredients = st.text_area("Ingredients")
        bake_time = st.text_input("Bake Time")
        shelf_life = st.text_input("Shelf Life")

        photo = st.file_uploader("Upload Product Image", type=["jpg","jpeg","png"])

        submit = st.form_submit_button("Add Product")

        if submit:
            if not product_code or not product_desc:
                st.error("Product Code and Product Name are required!")
            else:
                # Save image using exact product name
                if photo:
                    file_ext = photo.name.split('.')[-1].lower()

                    # Normalize extension
                    if file_ext == "jpeg":
                        file_ext = "jpg"

                    filepath = os.path.join(IMAGE_FOLDER, f"{product_desc}.{file_ext}")

                    with open(filepath, "wb") as f:
                        f.write(photo.getbuffer())

                new_row = pd.DataFrame([{
                    "product_code": product_code,
                    "product_desc": product_desc,
                    "dough_code": dough_code,
                    "weight_g": weight_g,
                    "status": status,
                    "category": category,
                    "ingredients": ingredients,
                    "bake_time": bake_time,
                    "shelf_life": shelf_life
                }])

                df_updated = pd.concat([df, new_row], ignore_index=True)
                save_data(df_updated)

                st.success("✅ Product added successfully!")
