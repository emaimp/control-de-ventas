import time
import streamlit as st
import matplotlib.pyplot as plt
from connection.consulta import data_stock

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
# Toast para cargar los datos
with st.spinner("Cargando..."):
    time.sleep(1)
    dfDatos = data_stock()
# ----------------------------------------------------------------------------------------
# Titulo de la pagina
colt1, colt2, colt3 = st.columns([37, 33, 30])
with colt2:
    st.header("Consulta de Stock")
# ----------------------------------------------------------------------------------------
# Filtros
cols1, cols2 = st.columns([20, 80])
with cols1:
    st.markdown("⚙️ Filtros")
with cols2:
    st.write("")
# ----------------------------------------------------------------------------------------
# Columnas principales
colfiltros, coldataframe = st.columns([20, 80])
# Menu de filtros
with colfiltros:
    with st.container(border=True):
        # Opciones de filtrado
        r_unica = sorted(dfDatos["Ropa"].unique())
        ropa = st.selectbox("Ropa", options=r_unica, index=None, placeholder="")
        st.write("")
        m_unica = sorted(dfDatos["Marca"].unique())
        marca = st.selectbox("Marca", options=m_unica, index=None, placeholder="")
        st.write("")
        talla = st.text_input("Talla", max_chars=3, placeholder="")
        st.write("")
        color = st.text_input("Color", max_chars=10, placeholder="")
# ----------------------------------------------------------------------------------------
# Filtrado de datos
if ropa is not None:
    dfDatos = dfDatos[dfDatos["Ropa"] == ropa]
if marca is not None:
    dfDatos = dfDatos[dfDatos["Marca"] == marca]
if talla != "":
    dfDatos = dfDatos[dfDatos["Talla"].str.upper() == talla.upper()]
if color != "":
    dfDatos = dfDatos[dfDatos["Color"].str.contains(color.capitalize(), na=False)]
# ----------------------------------------------------------------------------------------
# Crear un colormap de Matplotlib
cmap = plt.get_cmap("YlGnBu")  # RdYlGn
# Aplicar color de fondo a las columnas 'Favoritos','Cantidad' y 'Precio'
styled_df = dfDatos.style.background_gradient(
    subset=["Favoritos", "Cantidad", "Precio"], cmap=cmap
)
# ----------------------------------------------------------------------------------------
# Mostrar la tabla dataframe
with coldataframe:
    st.dataframe(styled_df, use_container_width=True)
# ----------------------------------------------------------------------------------------
