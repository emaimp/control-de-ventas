import time
import streamlit as st
import matplotlib.pyplot as plt
from connection.db import data_stock, data_costos

# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 34, 30])
with colt2:
    st.header("Consulta de Stock 🏷️")
    st.write("") # Espacio
    st.write("") # Espacio

tabs = st.tabs(["Productos", "Costos"])

with tabs[0]:
    # Toast para cargar los datos
    with st.spinner("Cargando productos..."):
        time.sleep(1)
        dfDatos = data_stock()

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
            c_unica = sorted(dfDatos["Categoria"].unique())
            categoria = st.selectbox("Categoria", options=c_unica, index=None, placeholder="")
            st.write("")
            nombre = st.text_input("Nombre", placeholder="", max_chars=100, key="nombre_productos")
            st.write("")
            precio_min = st.number_input("Precio Mínimo", min_value=0, value=None, step=1, placeholder="")
            st.write("")
            precio_max = st.number_input("Precio Máximo", min_value=0, value=None, step=1, placeholder="")

        # Filtrado de datos
        if categoria is not None:
            dfDatos = dfDatos[dfDatos["Categoria"] == categoria]
        if nombre != "":
            dfDatos = dfDatos[dfDatos["Nombre"].str.contains(nombre, case=False, na=False)]
        if precio_min is not None:
            dfDatos = dfDatos[dfDatos["Precio_Venta"] >= precio_min]
        if precio_max is not None:
            dfDatos = dfDatos[dfDatos["Precio_Venta"] <= precio_max]

    # Mostrar la tabla dataframe
    with coldataframe:
        # Crear un colormap de Matplotlib
        cmap = plt.get_cmap("YlGnBu")  # RdYlGn
        # Aplicar color de fondo a las columnas 'precio_venta' y 'stock'
        styled_df = dfDatos.style.background_gradient(
            subset=["Precio_Venta", "Stock"], cmap=cmap
            ).format({"Precio_Venta": "{:.2f}"})

        # Tabla de los productos
        st.dataframe(styled_df, use_container_width=True)

with tabs[1]:
    # Cargar datos de costos
    with st.spinner("Cargando costos..."):
        dfCostos = data_costos()

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
            # Opciones de filtrado basadas en tabla costos
            cat_unica = sorted(dfCostos["Categoria"].unique())
            categoria_c = st.selectbox("Categoria", options=cat_unica, index=None, placeholder="", key="categoria_costos")
            st.write("")
            nombre = st.text_input("Nombre", placeholder="", max_chars=100, key="nombre_costos")
            st.write("")
            precio_min_c = st.number_input("Precio Compra Mínimo", min_value=0.0, value=None, step=0.01, placeholder="", key="precio_min_costos")
            st.write("")
            precio_max_c = st.number_input("Precio Compra Máximo", min_value=0.0, value=None, step=0.01, placeholder="", key="precio_max_costos")

        # Filtrado de datos
        if categoria_c is not None:
            dfCostos = dfCostos[dfCostos["Categoria"] == categoria_c]
        if nombre != "":
            dfCostos = dfCostos[dfCostos["Nombre"].str.contains(nombre, case=False, na=False)]
        if precio_min_c is not None:
            dfCostos = dfCostos[dfCostos["Precio_Compra"] >= precio_min_c]
        if precio_max_c is not None:
            dfCostos = dfCostos[dfCostos["Precio_Compra"] <= precio_max_c]

    # Mostrar la tabla dataframe
    with coldataframe:
        # Crear un colormap de Matplotlib
        cmap = plt.get_cmap("YlGnBu")
        # Aplicar color de fondo a las columnas numéricas
        styled_df_c = dfCostos.style.background_gradient(
            subset=["Precio_Compra", "Impuesto"], cmap=cmap
            ).format({"Precio_Compra": "{:.2f}", "Impuesto": "{:.0f}%"})

        # Tabla de los costos
        st.dataframe(styled_df_c, use_container_width=True)
