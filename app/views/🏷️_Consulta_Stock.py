import time
import streamlit as st
import matplotlib.pyplot as plt
from connection.db import data_stock

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

# Toast para cargar los datos
with st.spinner("Cargando..."):
    time.sleep(1)
    dfDatos = data_stock()

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 34, 30])
with colt2:
    st.header("Consulta de Stock 🏷️")
    st.write("") # Espacio
    st.write("") # Espacio

#
# Filtros
#
cols1, cols2 = st.columns([20, 80])
with cols1:
    st.markdown("⚙️ Filtros")
with cols2:
    st.write("")

#
# Columnas principales
#
colfiltros, coldataframe = st.columns([20, 80])
#
# Menu de filtros
#
with colfiltros:
    with st.container(border=True):
        # Opciones de filtrado basadas en tabla productos
        c_unica = sorted(dfDatos["categoria"].unique())
        categoria = st.selectbox("Categoria", options=c_unica, index=None, placeholder="")
        st.write("")
        nombre = st.text_input("Nombre", placeholder="", max_chars=100)
        st.write("")
        precio_min = st.number_input("Precio Mínimo", min_value=0, value=None, step=1, placeholder="")
        st.write("")
        precio_max = st.number_input("Precio Máximo", min_value=0, value=None, step=1, placeholder="")

# Filtrado de datos
if categoria is not None:
    dfDatos = dfDatos[dfDatos["categoria"] == categoria]
if nombre != "":
    dfDatos = dfDatos[dfDatos["nombre"].str.contains(nombre, case=False, na=False)]
if precio_min is not None:
    dfDatos = dfDatos[dfDatos["precio"] >= precio_min]
if precio_max is not None:
    dfDatos = dfDatos[dfDatos["precio"] <= precio_max]

# Crear un colormap de Matplotlib
cmap = plt.get_cmap("YlGnBu")  # RdYlGn
# Aplicar color de fondo a las columnas 'precio' y 'stock'
styled_df = dfDatos.style.background_gradient(
    subset=["precio", "stock"], cmap=cmap
)

# Mostrar la tabla dataframe
with coldataframe:
    st.dataframe(styled_df, use_container_width=True)
