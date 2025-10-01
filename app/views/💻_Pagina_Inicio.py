import streamlit as st

# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar styles.css
with open("app/config/styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Badges
st.sidebar.markdown(
    """
    [![Facebook](
        https://img.shields.io/badge/-Facebook-blue?style=for-the-badge&logo=facebook
        )](https://www.facebook.com/)
    [![WhatsApp](
        https://img.shields.io/badge/-WhatsApp-darkgreen?style=for-the-badge&logo=whatsapp
        )](https://web.whatsapp.com/)
    """
)

# Banner
col_banner1, col_banner2, col_banner3 = st.columns([33, 37, 30])
with col_banner2:
    st.write("") # Espacio
    st.image("app/assets/banner.png", width=480)

# Título de la empresa
col_title1, col_title2, col_title3 = st.columns([34, 36, 30])
with col_title2:
    st.header("Electrodomésticos S.A")
    st.write("") # Espacio
    st.write("") # Espacio
    st.write("") # Espacio

# Columna del texto
col_inf1, col_inf2, col_inf3 = st.columns([20, 60, 20])
with col_inf2:
    st.markdown(
        """
        <div class="text-box">
        Esta aplicación permite identificar patrones de ventas,
        medir las ganancias y desempeño de los productos,
        asi como hacer proyecciones de rendimiento futuro 📉📈.
        </div>
        """,
        unsafe_allow_html=True
    )
