import streamlit as st

# ----------------------------------------------------------------------------------------
# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)
# ----------------------------------------------------------------------------------------
# Cargar styles.css
with open("config/styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
# ----------------------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------------------
# Columna banner
colb1, colb2, colb3 = st.columns(3)
with colb2:
    st.image("assets/banner.png", width=650)
st.write("") # Espacio
# ----------------------------------------------------------------------------------------
# Columna del texto y gif
col_inf1, col_inf2, col_inf3 = st.columns([33, 37, 30])
with col_inf2:
    with st.expander("Información sobre la aplicación"):
        st.write(
            """
            Permite :red[identificar] :orange[patrones] de ventas,
            :blue[medir] el desempeño de los productos,
            y hacer :green[proyecciones] de ganancia futuras.
            """
        )
        st.image("assets/programmer.gif")
# ----------------------------------------------------------------------------------------
