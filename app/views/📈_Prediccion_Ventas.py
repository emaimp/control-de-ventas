import time
import pandas as pd
import streamlit as st
import plotly.express as px
from connection.db import cargar_datos
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

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

    # Verificar si hay datos válidos para realizar la predicción
    if df_limpio is None or df_limpio.empty:
        st.error("No hay datos disponibles para predicción.")
        return

    # Crear copias temporales con nombres compatibles con Prophet para entrenamiento
    df_train_prophet = df_train.rename(columns={"Fecha": "ds", "Ganancias": "y"})

    # Crear y configurar el modelo Prophet con estacionalidad diaria
    m = Prophet(daily_seasonality=True)
    # Agregar regresores adicionales al modelo para mejorar las predicciones
    m.add_regressor("Edad_Reg")
    m.add_regressor("Gen_Reg")
    m.add_regressor("Ubic_Reg")
    # Entrenar el modelo con los datos de entrenamiento
    m.fit(df_train_prophet)

    # Realizar validación cruzada para evaluar la precisión del modelo
    try:
        # Configurar parámetros de cross-validation: inicial 30 días, período 10 días, horizonte 7 días
        df_cv = cross_validation(m, initial='30 days', period='10 days', horizon='7 days', parallel="threads")
        df_p = performance_metrics(df_cv)
        # Calcular métricas de desempeño del modelo
        mape = df_p['mape'].mean() * 100  # Error absoluto porcentual promedio
        rmse = df_p['rmse'].mean()  # Raíz del error cuadrático medio
        cobertura = df_p['coverage'].mean() * 100  # Cobertura de intervalos de confianza
    except Exception as e:
        st.error(f"Error en evaluación: {e}")
        mape, rmse, cobertura = None, None, None

    # Crear copia temporal para el modelo completo con nombres compatibles con Prophet
    df_limpio_prophet = df_limpio.rename(columns={"Fecha": "ds", "Ganancias": "y"})

    # Crear un nuevo modelo idéntico para predicciones futuras (no se permite ajustar dos veces sobre el mismo objeto)
    m2 = Prophet(daily_seasonality=True)
    m2.add_regressor("Edad_Reg")
    m2.add_regressor("Gen_Reg")
    m2.add_regressor("Ubic_Reg")
    # Ajustar el modelo con todos los datos limpios disponibles
    m2.fit(df_limpio_prophet)

    # Determinar la frecuencia temporal seleccionada por el usuario
    frequencia = frequenciasCodigo[frequencias.index(parFrecuencia)]
    # Crear dataframe futuro con el período de predicción especificado
    future = m2.make_future_dataframe(periods=parPeriodosFuturos, freq=frequencia)

    # Asignar valores promedio históricos a los regresores para las fechas futuras
    future["Edad_Reg"] = df_limpio["Edad_Reg"].mean()
    future["Gen_Reg"] = df_limpio["Gen_Reg"].mean()
    future["Ubic_Reg"] = df_limpio["Ubic_Reg"].mean()

    # Generar las predicciones del modelo para el período futuro
    forecast = m2.predict(future)
    # Extraer solo las predicciones para los períodos futuros solicitados
    dfPrediccion = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(
        parPeriodosFuturos
    )

    # Generar gráfico completo de Prophet con datos históricos y predicciones
    fig1 = m2.plot(forecast)

    # Personalizar el estilo del gráfico para mayor legibilidad
    fig1.patch.set_facecolor((1, 1, 1, 0))  # Establecer fondo transparente
    fig1.gca().set_facecolor((1, 1, 1, 1))  # Mantener fondo blanco en el área de trazado
    # Ocultar bordes innecesarios para un diseño más limpio
    fig1.gca().spines["top"].set_color("none")
    fig1.gca().spines["right"].set_color("none")
    # Cambiar nombres de ejes para mejor interpretabilidad
    fig1.gca().set_xlabel("Fecha")
    fig1.gca().set_ylabel("Ganancias")

    # Crear pestañas para organizar los diferentes aspectos del resultado
    tab_1, tab_2, tab_3 = st.tabs(["Resultado", "Gráfico", "Precisión"])

    # Preparar datos para visualización diferenciando reales vs predicciones
    df_limpio["Tipo"] = "Real"
    dfPrediccion["Tipo"] = "New"
    dfPrediccion = dfPrediccion.rename(columns={"yhat": "y"})
    # Combinar datos reales y predicciones en un solo dataframe para comparación
    dfResultado = pd.concat([dfPrediccion[["ds", "y"]]])
    # Renombrar para mejorar interpretabilidad en la visualización
    dfResultado_display = dfResultado.rename(columns={"ds": "Fecha", "y": "Ganancias"})

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
                st.write("Estos valores se basan en cross-validation históricos con regressors adicionals. En datos caóticos se espera un MAPE alto (>30%).")
                
                # Evaluar la calidad de las predicciones basada en MAPE
                if mape < 50:
                    st.success("Precisión mejorada con regressors.")
                else:
                    st.warning("Precisión todavía alta; considera modelos alternativos.")
        else:
            # Mostrar mensaje de error cuando no se pueden calcular métricas
            st.error("No se pudo calcular precisión (insuficientes datos o error).")

#
# Verificar si los datos fueron cargados correctamente desde la base de datos
#
if df is not None and not df.empty:
    # Fase de limpieza de datos: eliminar filas con valores faltantes críticos
    df = df.dropna(subset=["fecha", "Total"])
    if df.empty:
        st.error("No quedan datos después de limpieza.")
        st.stop()

    # Imputar valores faltantes en las columnas de regresores con medias apropiadas
    df["Edad_Promedio"] = df["Edad_Promedio"].fillna(df["Edad_Promedio"].mean())
    df["Proporcion_Femenino"] = df["Proporcion_Femenino"].fillna(0.5)
    df["Proporcion_Local1"] = df["Proporcion_Local1"].fillna(0.5)

    # Eliminar valores atípicos extremos en las ventas totales para mejorar estabilidad del modelo
    upper_limit = df["Total"].quantile(0.99)
    df = df[df["Total"] <= upper_limit]
    if df.empty:
        st.error("No quedan datos después de remover outliers.")
        st.stop()

    # Renombramos columnas para Prophet
    df = df.rename(columns={"fecha": "Fecha", "Total": "Ganancias", "Edad_Promedio": "Edad_Reg", "Proporcion_Femenino": "Gen_Reg", "Proporcion_Local1": "Ubic_Reg"})

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
    col_main1, col_main2, col_main3 = st.columns([43, 24, 33])

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
            st.write("")
            st.write("") # Espacio visual entre elementos
            st.write("")
            st.write("")
            # Definir el número de períodos futuros a predecir
            parPeriodosFuturos = st.slider("Periodo de tiempo", 1, 12, 1)
            st.write("")
            st.write("") # Espacio visual
            st.write("")
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
    st.error("No se cargaron datos")
