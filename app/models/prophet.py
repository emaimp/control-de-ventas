import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

#
# Predicción de ganancias
#
def generar_forecast_ganancias(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo):
    # Verificar si hay datos válidos para realizar la predicción
    if df_limpio is None or df_limpio.empty:
        raise ValueError("No hay datos disponibles para predicción.")

    # Feriados de Argentina
    feriados_argentina = [
        (1, 1, "Año Nuevo"),
        (4, 2, "Día del Veterano de Malvinas"),
        (5, 1, "Día del Trabajo"),
        (5, 25, "Aniversario de la Revolución de Mayo"),
        (6, 20, "Día de la Bandera"),
        (7, 9, "Día de la Independencia"),
        (8, 17, "Pasaje a la Inmortalidad del Gral. José de San Martín"),
        (10, 12, "Día del Respeto a la Diversidad Cultural"),
        (11, 20, "Día de la Soberanía Nacional"),
        (12, 8, "Inmaculada Concepción de María"),
        (12, 25, "Navidad"),
    ]

    # Crear dataframe de holidays para Prophet
    holidays_list = []
    for year in [2020, 2021, 2022, 2023, 2024]:
        for month, day, name in feriados_argentina:
            holidays_list.append({
                'holiday': name,
                'ds': pd.to_datetime(f'{year}-{month}-{day}'),
                'lower_window': 0,
                'upper_window': 0,
            })
    holidays_df = pd.DataFrame(holidays_list)

    # Crear copias temporales con nombres compatibles con Prophet para entrenamiento
    df_train_prophet = df_train.rename(columns={"Fecha": "ds", "Ganancias": "y"})

    # Crear y configurar el modelo Prophet con estacionalidad ajustada y holidays
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive',
        holidays=holidays_df,
        holidays_prior_scale=5,
        interval_width=0.9,
        n_changepoints=50,
        changepoint_prior_scale=0.5,
        )
    # Entrenar el modelo con los datos de entrenamiento
    m.fit(df_train_prophet)

    # Realizar validación cruzada para evaluar la precisión del modelo
    try:
        # Configurar parámetros de cross-validation: inicial, período, horizonte
        df_cv = cross_validation(m, initial='1500 days', period='400 days', horizon='1 days', parallel="threads")
        # Calcular métricas de desempeño del modelo basadas en la validación cruzada
        df_p = performance_metrics(df_cv)
        
        mape = df_p['mape'].mean() * 100 # Error absoluto porcentual promedio
        rmse = df_p['rmse'].mean() # Raíz del error cuadrático medio
        cobertura = df_p['coverage'].mean() * 100 # Cobertura de intervalos de confianza
    except Exception as e:
        mape, rmse, cobertura = None, None, None

    # Crear copia temporal para el modelo completo con nombres compatibles con Prophet
    df_limpio_prophet = df_limpio.rename(columns={"Fecha": "ds", "Ganancias": "y"})

    # Crear un nuevo modelo idéntico para predicciones futuras (no se permite ajustar dos veces sobre el mismo objeto)
    m2 = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive',
        holidays=holidays_df,
        holidays_prior_scale=5,
        interval_width=0.9,
        n_changepoints=50,
        changepoint_prior_scale=0.5,
        )
    # Ajustar el modelo con todos los datos limpios disponibles
    m2.fit(df_limpio_prophet)

    # Calcular periods para predicciones diarias y agrupar después
    periods = parPeriodosFuturos * (365 if parFrecuencia == "Año" else 30 if parFrecuencia == "Mes" else 1)
    frequencia = 'D'
    # Crear dataframe futuro con el período de predicción especificado
    future = m2.make_future_dataframe(periods=periods, freq=frequencia)
    # Generar las predicciones del modelo para el período futuro
    forecast = m2.predict(future)
    # Extraer todas las predicciones diarias
    dfPrediccion = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    # Agrupar por mes o año según frecuencia seleccionada
    if parFrecuencia == "Mes":
        dfPrediccion = dfPrediccion.resample('M', on='ds').agg({'yhat': 'sum', 'yhat_lower': 'sum', 'yhat_upper': 'sum'}).reset_index()
    elif parFrecuencia == "Año":
        dfPrediccion = dfPrediccion.resample('Y', on='ds').agg({'yhat': 'sum', 'yhat_lower': 'sum', 'yhat_upper': 'sum'}).reset_index()
    # Para "Dia" se queda como está, no se usa

    # Obtener las últimas parPeriodosFuturos períodos
    dfPrediccion = dfPrediccion.tail(parPeriodosFuturos)

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

    # Preparar datos para visualización diferenciando reales vs predicciones
    dfResultado = dfPrediccion[["ds", "yhat"]].rename(columns={"yhat": "y"})
    # Renombrar para mejorar interpretabilidad en la visualización
    dfResultado_display = dfResultado.rename(columns={"ds": "Fecha", "y": "Ganancias"})

    # Retornar solo los elementos necesarios para la UI
    return dfResultado_display, fig1, mape, rmse, cobertura

#
# Predicción de ventas
#
def generar_forecast_ventas(df_limpio, parFrecuencia, parPeriodosFuturos, df_train, frequencias, frequenciasCodigo):
    # Verificar si hay datos válidos para realizar la predicción
    if df_limpio is None or df_limpio.empty:
        raise ValueError("No hay datos disponibles para predicción.")

    # Feriados de Argentina
    feriados_argentina = [
        (1, 1, "Año Nuevo"),
        (4, 2, "Día del Veterano de Malvinas"),
        (5, 1, "Día del Trabajo"),
        (5, 25, "Aniversario de la Revolución de Mayo"),
        (6, 20, "Día de la Bandera"),
        (7, 9, "Día de la Independencia"),
        (8, 17, "Pasaje a la Inmortalidad del Gral. José de San Martín"),
        (10, 12, "Día del Respeto a la Diversidad Cultural"),
        (11, 20, "Día de la Soberanía Nacional"),
        (12, 8, "Inmaculada Concepción de María"),
        (12, 25, "Navidad"),
    ]

    # Crear dataframe de holidays para Prophet
    holidays_list = []
    for year in [2020, 2021, 2022, 2023, 2024]:
        for month, day, name in feriados_argentina:
            holidays_list.append({
                'holiday': name,
                'ds': pd.to_datetime(f'{year}-{month}-{day}'),
                'lower_window': 0,
                'upper_window': 0,
            })
    holidays_df = pd.DataFrame(holidays_list)

    # Crear copias temporales con nombres compatibles con Prophet para entrenamiento
    df_train_prophet = df_train.rename(columns={"Fecha": "ds", "Ventas": "y"})

    # Crear y configurar el modelo Prophet con estacionalidad ajustada y holidays
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive',
        holidays=holidays_df,
        holidays_prior_scale=5,
        interval_width=0.9,
        n_changepoints=50,
        changepoint_prior_scale=0.5,
        )
    # Entrenar el modelo con los datos de entrenamiento
    m.fit(df_train_prophet)

    # Realizar validación cruzada para evaluar la precisión del modelo
    try:
        # Configurar parámetros de cross-validation: inicial, período, horizonte
        df_cv = cross_validation(m, initial='1500 days', period='400 days', horizon='1 days', parallel="threads")
        # Calcular métricas de desempeño del modelo basadas en la validación cruzada
        df_p = performance_metrics(df_cv)

        mape = df_p['mape'].mean() * 100 # Error absoluto porcentual promedio
        rmse = df_p['rmse'].mean() # Raíz del error cuadrático medio
        cobertura = df_p['coverage'].mean() * 100 # Cobertura de intervalos de confianza
    except Exception as e:
        mape, rmse, cobertura = None, None, None

    # Crear copia temporal para el modelo completo con nombres compatibles con Prophet
    df_limpio_prophet = df_limpio.rename(columns={"Fecha": "ds", "Ventas": "y"})

    # Crear un nuevo modelo idéntico para predicciones futuras (no se permite ajustar dos veces sobre el mismo objeto)
    m2 = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive',
        holidays=holidays_df,
        holidays_prior_scale=5,
        interval_width=0.9,
        n_changepoints=50,
        changepoint_prior_scale=0.5,
        )
    # Ajustar el modelo con todos los datos limpios disponibles
    m2.fit(df_limpio_prophet)

    # Calcular periods para predicciones diarias y agrupar después
    periods = parPeriodosFuturos * (365 if parFrecuencia == "Año" else 30 if parFrecuencia == "Mes" else 1)
    frequencia = 'D'
    # Crear dataframe futuro con el período de predicción especificado
    future = m2.make_future_dataframe(periods=periods, freq=frequencia)
    # Generar las predicciones del modelo para el período futuro
    forecast = m2.predict(future)
    # Extraer todas las predicciones diarias
    dfPrediccion = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    # Agrupar por mes o año según frecuencia seleccionada
    if parFrecuencia == "Mes":
        dfPrediccion = dfPrediccion.resample('M', on='ds').agg({'yhat': 'sum', 'yhat_lower': 'sum', 'yhat_upper': 'sum'}).reset_index()
    elif parFrecuencia == "Año":
        dfPrediccion = dfPrediccion.resample('Y', on='ds').agg({'yhat': 'sum', 'yhat_lower': 'sum', 'yhat_upper': 'sum'}).reset_index()
    # Para "Dia" se queda como está, no se usa

    # Obtener las últimas parPeriodosFuturos períodos
    dfPrediccion = dfPrediccion.tail(parPeriodosFuturos)

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
    fig1.gca().set_ylabel("Ventas")

    # Preparar datos para visualización diferenciando reales vs predicciones
    dfResultado = dfPrediccion[["ds", "yhat"]].rename(columns={"yhat": "y"})
    # Renombrar para mejorar interpretabilidad en la visualización
    dfResultado_display = dfResultado.rename(columns={"ds": "Fecha", "y": "Ventas"})

    # Retornar solo los elementos necesarios para la UI
    return dfResultado_display, fig1, mape, rmse, cobertura
