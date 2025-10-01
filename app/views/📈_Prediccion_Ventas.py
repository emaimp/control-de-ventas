import time
import streamlit as st
import plotly.express as px
from connection.db import cargar_datos_ganancias, cargar_datos_cantidad
from models.prophet import generar_forecast_ganancias, generar_forecast_cantidad

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
    df_ganancias = cargar_datos_ganancias()
    df_cantidad = cargar_datos_cantidad()

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([32, 38, 30])
with colt2:
    st.header("Predicción de Ventas 📈")
    st.write("")  # Espacio
    st.write("")  # Espacio

#
# Visualización de la predicción "ganancias"
#
def prediccion_ganancias(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo):

    # Generar el forecast usando Prophet
    try:
        dfResultado_display, fig1, mape, rmse, cobertura = generar_forecast_ganancias(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo)
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
                    st.success("Precisión del modelo: BUENA.")
                else:
                    st.warning("Precisión del modelo: MALA.")
        else:
            # Mostrar mensaje de error cuando no se pueden calcular métricas
            st.error("No se pudo calcular precisión (insuficientes datos o error).")

#
# Visualización de la predicción "cantidad"
#
def prediccion_cantidad(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo):

    # Generar el forecast usando Prophet
    try:
        dfResultado_display, fig1, mape, rmse, cobertura = generar_forecast_cantidad(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo)
    except ValueError as e:
        st.error(str(e))
        return
    except Exception as e:
        st.error(f"Error en evaluación: {e}")
        return

    # Crear pestañas para organizar los diferentes aspectos del resultado
    tab_q1, tab_q2, tab_q3 = st.tabs(["Resultado", "Gráfico", "Precisión"])

    # Pestaña de resultados: mostrar tabla de datos y gráfico lineal en columnas
    with tab_q1:
        cq1, cq2 = st.columns([30, 70])

        with cq1:
            st.dataframe(dfResultado_display)

        with cq2:
            fig = px.line(dfResultado_display, x="Fecha", y="Cantidad")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Pestaña del gráfico: mostrar el gráfico completo de Prophet centrado
    with tab_q2:
        col_qplot1, col_qplot2, col_qplot3 = st.columns([17, 60, 23])
        with col_qplot2:
            st.write(fig1)

    # Pestaña de precisión: mostrar métricas de evaluación del modelo
    with tab_q3:
        # Verificar si las métricas de precisión están disponibles
        if mape is not None:
            col_qm1, col_qm2, col_qm3 = st.columns([5, 90 , 5])

            # Columna central con la información
            with col_qm2:
                st.metric(label=f"Precisión (MAPE): {mape:.2f}%", value="")
                st.caption("Mientras menor sea el porcentaje de error absoluto mas certera es la predicción.")
                st.metric(label=f"Raíz del Error Cuadrático Medio (RMSE): {rmse:.2f}", value="")
                st.caption("Mientras menor sea el error absoluto en unidades originales mas certera es la predicción.")
                st.metric(label=f"Cobertura de Intervalos: {cobertura:.2f}%", value="")
                st.caption("Porcentaje de predicciones que caen dentro de intervalos de confianza (ideal >80%).")
                st.write("Nota: Valores basados en cross-validation. En datos caóticos se espera un MAPE alto (>30%).")

                # Evaluar la calidad de las predicciones basada en MAPE
                if mape < 50:
                    st.success("Precisión del modelo: BUENA.")
                else:
                    st.warning("Precisión del modelo: MALA.")
        else:
            # Mostrar mensaje de error cuando no se pueden calcular métricas
            st.error("No se pudo calcular precisión (insuficientes datos o error).")

#
# Verificación y limpieza de los datos "ganancias"
#
if df_ganancias is not None and not df_ganancias.empty:
    # Fase de limpieza de datos: eliminar filas con valores faltantes críticos
    df_ganancias = df_ganancias.dropna(subset=["fecha", "Ganancias"])
    if df_ganancias.empty:
        st.error("No quedan datos después de limpieza.")
        st.stop()

    # Eliminar valores atípicos extremos en las ventas totales para mejorar estabilidad del modelo
    upper_limit = df_ganancias["Ganancias"].quantile(0.99)
    df_ganancias = df_ganancias[df_ganancias["Ganancias"] <= upper_limit]
    if df_ganancias.empty:
        st.error("No quedan datos después de remover outliers.")
        st.stop()

    # Renombramos columnas para Prophet
    df_ganancias = df_ganancias.rename(columns={"fecha": "Fecha"})

    # Dividir los datos en conjuntos de entrenamiento y prueba para validación del modelo
    if len(df_ganancias) > 30:
        # Solo dividir si hay suficientes datos para una evaluación significativa
        train_size = int(len(df_ganancias) * 0.8)
        df_train = df_ganancias.iloc[:train_size]
        df_test = df_ganancias.iloc[train_size:]
    else:
        # Usar todos los datos tanto para train como test si son insuficientes
        df_train = df_ganancias
        df_test = df_ganancias.copy()
        st.warning("Pocos datos para evaluación precisa (usa al menos 30 días)")

else:
    # Manejar caso donde no hay datos disponibles para procesar
    st.error("No se cargaron datos.")

#
# Verificación y limpieza de los datos "cantidad"
#
if df_cantidad is not None and not df_cantidad.empty:
    # Fase de limpieza de datos: eliminar filas con valores faltantes críticos
    df_cantidad = df_cantidad.dropna(subset=["fecha", "Cantidad"])
    if df_cantidad.empty:
        st.error("No quedan datos de cantidad después de limpieza.")
        st.stop()
    else:
        # Eliminar valores atípicos extremos
        upper_limit_c = df_cantidad["Cantidad"].quantile(0.99)
        df_cantidad = df_cantidad[df_cantidad["Cantidad"] <= upper_limit_c]
        if df_cantidad.empty:
            st.error("No quedan datos de cantidad después de remover outliers.")
            st.stop()
        else:
            # Renombrar columnas para Prophet
            df_cantidad = df_cantidad.rename(columns={"fecha": "Fecha"})

            # Dividir en train/test para cantidad
            if len(df_cantidad) > 30:
                train_size_c = int(len(df_cantidad) * 0.8)
                df_train_c = df_cantidad.iloc[:train_size_c]
                df_test_c = df_cantidad.iloc[train_size_c:]
            else:
                df_train_c = df_cantidad
                df_test_c = df_cantidad.copy()
                st.warning("Pocos datos de cantidad para evaluación precisa (usa al menos 30 días)")

else:
    # Manejar caso donde no hay datos disponibles para procesar
    st.error("No se cargaron datos de cantidad.")
    st.stop()

# Definir las frecuencias de control
frequencias = ["Mes", "Año"]
frequenciasCodigo = ["M", "Y"]

#
# Crear columnas para la interfaz de controles del usuario
#
col_main1, col_main2, col_main3 = st.columns([43, 14, 43])

with col_main1:
    # Mostrar vista previa de los datos procesados en una tabla
    st.dataframe(df_ganancias, use_container_width=True)

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
    # Predicción de ganancias
    st.header("Predicción de Ganancias")
    prediccion_ganancias(df_ganancias, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo)

    # Predicción de cantidad
    st.header("Predicción de Cantidad")
    prediccion_cantidad(df_cantidad, parFrecuencia, parPeriodosFuturos, df_train_c, frequencias, frequenciasCodigo)
