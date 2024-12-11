import time
import pandas as pd
import streamlit as st
from prophet import Prophet
import plotly.express as px
from connection.prediccion import cargar_datos

# ---------------------------------------------------------------------------------------------
# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)
# ---------------------------------------------------------------------------------------------
# Cargar styles.css
with open("config/styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
# ---------------------------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------------------------
# Toast para cargar los datos
with st.spinner("Cargando..."):
    time.sleep(1)
    df = cargar_datos()
# ---------------------------------------------------------------------------------------------
# Titulo de la pagina
colt1, colt2, colt3 = st.columns([34, 34, 32])
with colt2:
    st.header("Predicción de Ventas")
    st.write("")  # Espacio
    st.write("")  # Espacio
# ---------------------------------------------------------------------------------------------
# Verificar si los datos fueron cargados
if df is not None and not df.empty:
    # with st.container(border=True):
    df.columns = ["ds", "y"]  # Renombramos las columnas a 'ds' y 'y' para Prophet
    # Definir las frecuencias de control
    frequencias = ["Mes", "Año"]
    frequenciasCodigo = ["M", "Y"]
    # -----------------------------------------------------------------------------------------
    # Definir los controles para los parámetros
    col_opt1, col_opt2, col_opt3 = st.columns([33, 34, 33])
    with col_opt1:
        # Mostrar el dataframe
        st.dataframe(df, use_container_width=True)
    with col_opt2:
        st.write("")  # Espacio
    with col_opt3:
        with st.container(border=True):
            # Control para la frecuencia de los datos
            parFrecuencia = st.selectbox("Frecuencia", options=frequencias)
            # with st.container(border=True):
            st.write("")  #
            st.write("")  #
            st.write("")  # Espacio
            st.write("")  #
            st.write("")  #
            # Control para el horizonte de predicción
            parPeriodosFuturos = st.slider("Periodo de tiempo", 1, 24, 1)
            st.write("")  #
            st.write("")  # Espacio
            st.write("")  #
            st.write("")  #
            col_be1, col_be2, col_be3 = st.columns([38, 30, 32])
            with col_be2:
                # Botón para ejecutar la predicción
                btnEjecutarForecast = st.button("Ejecutar")
    # -----------------------------------------------------------------------------------------
    # Ejecutamos la predicción
    if btnEjecutarForecast:
        m = Prophet(daily_seasonality=True)  # Establecer los datos a diarios
        m.fit(df)
        # Detectar la frecuencia de los datos
        frequencia = frequenciasCodigo[frequencias.index(parFrecuencia)]
        future = m.make_future_dataframe(periods=parPeriodosFuturos, freq=frequencia)
        # Hacer la predicción
        forecast = m.predict(future)
        dfPrediccion = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(
            parPeriodosFuturos
        )
        # Generar el gráfico de Prophet
        fig1 = m.plot(forecast)
        # Ajustar la opacidad del gráfico
        fig1.patch.set_facecolor((1, 1, 1, 0))  # Fondo de la figura
        fig1.gca().set_facecolor((1, 1, 1, 1))  # Fondo del area de trazado
        # Eliminar los bordes superiores derecho
        fig1.gca().spines["top"].set_color("none")
        fig1.gca().spines["right"].set_color("none")
        # -------------------------------------------------------------------------------------
        # Generar las pestañas para mostrar el resultado y el gráfico
        tab1, tab2 = st.tabs(["Resultado", "Gráfico"])
        df["Tipo"] = "Real"
        dfPrediccion["Tipo"] = "New"
        dfPrediccion = dfPrediccion.rename(columns={"yhat": "y"})
        dfResultado = pd.concat([dfPrediccion[["ds", "y"]]])  # df.sort_values(by='ds'), 'Tipo'
        with tab1:
            c1, c2 = st.columns([30, 70])
            with c1:
                st.dataframe(dfResultado)
            with c2:
                fig = px.line(dfResultado, x="ds", y="y")  # color='Tipo'
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
        with tab2:
            col_plot1, col_plot2, col_plot3 = st.columns([17, 60, 23])
            with col_plot2:
                st.write(fig1)
else:
    st.error("No se cargaron datos")
# ---------------------------------------------------------------------------------------------
