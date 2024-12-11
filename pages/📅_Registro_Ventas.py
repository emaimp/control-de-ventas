import time
import pandas as pd
import streamlit as st
from connection.consulta import data_stock
from connection.registro import save_data

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
colt1, colt2, colt3 = st.columns(3)
with colt2:
    st.header("Registro de Ventas")
# ----------------------------------------------------------------------------------------
# Obtener valores únicos para los selectbox
unique_ropa = sorted(dfDatos["Ropa"].unique())
unique_marca = sorted(dfDatos["Marca"].unique())
unique_talla = sorted(dfDatos["Talla"].unique())
unique_color = sorted(dfDatos["Color"].unique())
# ----------------------------------------------------------------------------------------
# Opciones
cols1, cols2 = st.columns([91, 9])
with cols1:
    st.write("")
with cols2:
    st.markdown("⚙️ Opciones")
# ========================================================================================
# Columnas principales
col_opciones, col_botones = st.columns([91, 9])
# ========================================================================================
# Columna opciones
with col_opciones:
    with st.container(border=True):
        # Columnas de filtros
        col_ropa, col_marca, col_talla, col_color = st.columns(4)
        with col_ropa:
            value_ropa = st.selectbox("Selecciona una ropa:", unique_ropa)
        with col_marca:
            value_marca = st.selectbox("Selecciona una marca:", unique_marca)
        with col_talla:
            value_talla = st.selectbox("Selecciona una talla:", unique_talla)
        with col_color:
            value_color = st.selectbox("Selecciona un color:", unique_color)
        # Columnas de number_input y el date_input
        col_input, col_date = st.columns(2)
        with col_input:
            numero_input = st.number_input(
                "Ingresa un número:", min_value=0, step=1, format="%d"
            )
        with col_date:
            fecha_input = st.date_input("Selecciona una fecha:")
# ========================================================================================
# Filtrar el DataFrame según las selecciones
filtered_data = dfDatos[
    (dfDatos["Ropa"] == value_ropa)
    & (dfDatos["Marca"] == value_marca)
    & (dfDatos["Talla"] == value_talla)
    & (dfDatos["Color"] == value_color)
]
# ----------------------------------------------------------------------------------------
# Variables del DataFrame
precio = None
total = None
# ----------------------------------------------------------------------------------------
# Obtener el precio
if not filtered_data.empty:
    precio = filtered_data["Precio"].values[0]
    if numero_input > 0:
        total = precio * numero_input
        st.success(f"Total: {total:.2f}")  # Mostrar el total
else:
    st.write("Sin coincidencias")
# ----------------------------------------------------------------------------------------
# Separar el dia, mes y año de la fecha
if fecha_input:
    dia = fecha_input.day
    mes = fecha_input.month
    año = fecha_input.year
else:
    dia = mes = año = None
# ----------------------------------------------------------------------------------------
# Usar sesión de estado para acumular resultados
if "resultados" not in st.session_state:
    st.session_state.resultados = pd.DataFrame(
        columns=[
            "Ropa",
            "Marca",
            "Talla",
            "Color",
            "Precio",
            "Cantidad",
            "Total",
            "Dia",
            "Mes",
            "Anio",
            "Fecha",
        ]
    )
# ========================================================================================
# Columna botones
with col_botones:
    with st.container(border=True):
        # Botón Añadir
        if st.button("Añadir", key="blue"):
            # Crear un DataFrame para mostrar los resultados
            nuevo_resultado = pd.DataFrame(
                {
                    "Ropa": [value_ropa],
                    "Marca": [value_marca],
                    "Talla": [value_talla],
                    "Color": [value_color],
                    "Precio": [precio],
                    "Cantidad": [int(numero_input)],
                    "Total": ([total] if total is not None else [0.0]),
                    "Dia": [dia],
                    "Mes": [mes],
                    "Anio": [año],
                    "Fecha": [fecha_input],
                }
            )
            # Acumular resultados
            st.session_state.resultados = pd.concat(
                [st.session_state.resultados, nuevo_resultado], ignore_index=True
            )
        # Botón Borrar
        if st.button("Borrar", key="red"):
            st.session_state.resultados = pd.DataFrame(
                columns=[
                    "Ropa",
                    "Marca",
                    "Talla",
                    "Color",
                    "Precio",
                    "Cantidad",
                    "Total",
                    "Dia",
                    "Mes",
                    "Anio",
                    "Fecha",
                ]
            )
        # Botón guardar
        if st.button("Cargar", key="green"):
            if not st.session_state.resultados.empty:
                save_data(st.session_state.resultados)
                st.toast("Registro de venta cargado ✅")
            else:
                st.toast("No hay datos para cargar ❌")
# ========================================================================================
# Tabla de resultados acumulados
if not st.session_state.resultados.empty:
    st.table(st.session_state.resultados)
# ----------------------------------------------------------------------------------------
