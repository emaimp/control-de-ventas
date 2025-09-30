import time
import streamlit as st
import plotly.express as px
from connection.db import cargar_datos
from models.prophet import generar_forecast

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
    df = cargar_datos()

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([32, 38, 30])
with colt2:
    st.header("Predicción de Ventas 📈")
    st.write("")  # Espacio
    st.write("")  # Espacio

#
# Función para realizar la predicción con Prophet
#
def realizar_prediccion(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo):

    # Generar el forecast usando Prophet
    try:
        dfResultado_display, fig1, mape, rmse, cobertura = generar_forecast(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo)
    except ValueError as e:
        st.error(str(e))
        return
    except Exception as e:
        st.error(f"Error en evaluación: {e}")
        return

    # Crear pestañas para organizar los diferentes aspectos del resultado
    tab_1, tab_2, tab_3 = st.tabs(["Resultado", "Gráfico", "Precisión"])

    # Pestaña de resultados: mostrar tabla de datos y gráfico lineal en columnas
    with tab_1:
        c1, c2 = st.columns([30, 70])

        with c1:
            st.dataframe(dfResultado_display)

        with c2:
            fig = px.line(dfResultado_display, x="Fecha", y="Ganancias")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Pestaña del gráfico: mostrar el gráfico completo de Prophet centrado
    with tab_2:
        col_plot1, col_plot2, col_plot3 = st.columns([17, 60, 23])
        with col_plot2:
            st.write(fig1)

    # Pestaña de precisión: mostrar métricas de evaluación del modelo
    with tab_3:
        # Verificar si las métricas de precisión están disponibles
        if mape is not None:
            col_m1, col_m2, col_m3 = st.columns([5, 90 , 5])

            # Columna central con la información
            with col_m2:
                st.metric(label=f"Precisión (MAPE): {mape:.2f}%", value="")
                st.caption("Mientras menor sea el porcentaje de error absoluto mas certera es la predicción.")
                st.metric(label=f"Raíz del Error Cuadrático Medio (RMSE): {rmse:.2f}", value="")
                st.caption("Mientras menor sea el error absoluto en unidades originales mas certera es la predicción.")
                st.metric(label=f"Cobertura de Intervalos: {cobertura:.2f}%", value="")
                st.caption("Porcentaje de predicciones que caen dentro de intervalos de confianza (ideal >80%).")
                st.write("Nota: Valores basados en cross-validation. En datos caóticos se espera un MAPE alto (>30%).")

                # Evaluar la calidad de las predicciones basada en MAPE
                if mape < 50:
                    st.success("Precisión buena del modelo.")
                else:
                    st.warning("Precisión mala del modelo.")
        else:
            # Mostrar mensaje de error cuando no se pueden calcular métricas
            st.error("No se pudo calcular precisión (insuficientes datos o error).")

#
# Verificar si los datos fueron cargados correctamente desde la base de datos
#
if df is not None and not df.empty:
    # Fase de limpieza de datos: eliminar filas con valores faltantes críticos
    df = df.dropna(subset=["fecha", "Ganancias"])
    if df.empty:
        st.error("No quedan datos después de limpieza.")
        st.stop()

    # Eliminar valores atípicos extremos en las ventas totales para mejorar estabilidad del modelo
    upper_limit = df["Ganancias"].quantile(0.99)
    df = df[df["Ganancias"] <= upper_limit]
    if df.empty:
        st.error("No quedan datos después de remover outliers.")
        st.stop()

    # Renombramos columnas para Prophet
    df = df.rename(columns={"fecha": "Fecha"})

    # Dividir los datos en conjuntos de entrenamiento y prueba para validación del modelo
    if len(df) > 30:
        # Solo dividir si hay suficientes datos para una evaluación significativa
        train_size = int(len(df) * 0.8)
        df_train = df.iloc[:train_size]
        df_test = df.iloc[train_size:]
    else:
        # Usar todos los datos tanto para train como test si son insuficientes
        df_train = df
        df_test = df.copy()
        st.warning("Pocos datos para evaluación precisa (usa al menos 30 días)")

    # Definir las frecuencias de control
    frequencias = ["Mes", "Año"]
    frequenciasCodigo = ["M", "Y"]

    #
    # Crear columnas para la interfaz de controles del usuario
    #
    col_main1, col_main2, col_main3 = st.columns([43, 14, 43])

    with col_main1:
        # Mostrar vista previa de los datos procesados en una tabla
        st.dataframe(df, use_container_width=True)

    with col_main2:
        st.write("") # Espacio

    with col_main3:
        with st.container(border=True):
            # Seleccionar la frecuencia temporal deseada para las predicciones
            parFrecuencia = st.selectbox("Frecuencia", options=frequencias)
            st.write("")
            st.write("") # Espacio
            st.write("") # Espacio
            st.write("") # Espacio
            st.write("") # Espacio
            st.write("")
            # Definir el número de períodos futuros a predecir
            parPeriodosFuturos = st.slider("Periodo de tiempo", 1, 12, 1)
            st.write("")
            st.write("") # Espacio
            st.write("")
            col_be1, col_be2, col_be3 = st.columns([38, 30, 32])
            with col_be2:
                # Botón que inicia el proceso de predicción al ser presionado
                btnEjecutarForecast = st.button("Ejecutar")

    # Verificar si el usuario ha presionado el botón para ejecutar la predicción
    if btnEjecutarForecast:
        realizar_prediccion(df, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo)
else:
    # Manejar caso donde no hay datos disponibles para procesar
    st.error("No se cargaron datos.")
