import time
import streamlit as st
import plotly.express as px
from streamlit_extras.grid import grid
from connection.db import data_ventas, data_costos, data_stock

# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

# Toast para cargar los datos
with st.spinner("Cargando..."):
    time.sleep(1)
    dfDatos = data_ventas()

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 34, 30])
with colt2:
    # Titulo
    st.header("Control de Ventas 📊")
    st.write("") # Espacio
    st.write("") # Espacio

#
# Verificación y limpieza de los datos
#
if not dfDatos.empty:
    # Elimina filas con valores faltantes críticos
    dfDatos = dfDatos.dropna(subset=["Mes", "Anio", "Edad", "Producto", "Ubicacion", "Genero", "Cantidad", "Ganancias"])
    if dfDatos.empty:
        st.error("No quedan datos después de limpieza.")
        st.stop()

# Verificar si hay datos disponibles
if dfDatos.empty:
    st.error("No hay datos de ventas con ganancias asociadas.")
    st.stop()

# Diccionario para los nombres de los meses
meses_dict = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
    }

#
# Columas para los filtros
#
my_grid = grid([6])
with my_grid.expander("Filtros", expanded=True):

    col_izq, col_der = st.columns(2)

    with col_izq:
        # Filtro de mes
        with st.container(border=True):
            meses_unicos = sorted(dfDatos["Mes"].unique())
            toggle_meses = st.toggle("Seleccionar todos los meses")
            if toggle_meses:
                parMes = max(meses_unicos)
            else:
                parMes = st.select_slider(
                    "Meses",
                    options=meses_unicos,
                    value=meses_unicos[0],  # Valor por defecto (mes 1)
                    format_func=lambda x: meses_dict.get(x, f"Mes {x}"),  # Formato visual
                )
        # Filtro de año
        with st.container(border=True):
            anios_unicos = sorted(dfDatos["Anio"].unique())
            parAno = st.select_slider(
                "Años",
                options=anios_unicos,
                value=anios_unicos[0],  # Valor por defecto (primer año)
                format_func=lambda x: f"Año {x}",  # Formato visual
            )
        # Filtro de edad
        with st.container(border=True):
            edades_min = int(dfDatos["Edad"].min())
            edades_max = int(dfDatos["Edad"].max())
            parEdad = st.slider(
                "Edad",
                min_value=edades_min,
                max_value=edades_max,
                value=(edades_min, edades_max)
            )

    with col_der:
        # Filtro de producto
        with st.container(border=True):
            productos_unicos = sorted(dfDatos["Producto"].unique())
            toggle = st.toggle("Seleccionar todos los productos")
            if toggle:
                parProducto = productos_unicos
            else:
                parProducto = st.multiselect(
                    "Producto", options=productos_unicos, placeholder=""
                )
        # Filtro de ubicación
        with st.container(border=True):
            ubicaciones_unicas = sorted(dfDatos["Ubicacion"].unique())
            parUbicacion = st.multiselect(
                "Ubicacion", options=ubicaciones_unicas, placeholder=""
            )
        # Filtro de género
        with st.container(border=True):
            generos_unicos = sorted(dfDatos["Genero"].unique())
            parGenero = st.multiselect(
                "Genero", options=generos_unicos, placeholder=""
            )

# Si hay parámetros aplicamos los filtros
if parAno:
    dfDatos = dfDatos[dfDatos["Anio"] == parAno]
if parMes:
    dfDatos = dfDatos[dfDatos["Mes"] <= parMes]
if parEdad:
    dfDatos = dfDatos[(dfDatos["Edad"] >= parEdad[0]) & (dfDatos["Edad"] <= parEdad[1])]

if len(parProducto) > 0:
    dfDatos = dfDatos[dfDatos["Producto"].isin(parProducto)]
if len(parUbicacion) > 0:
    dfDatos = dfDatos[dfDatos["Ubicacion"].isin(parUbicacion)]
if len(parGenero) > 0:
    dfDatos = dfDatos[dfDatos["Genero"].isin(parGenero)]

#
# Obtenemos los datos del año
#
if parMes:
    if parMes > 1:
        dfMesAnterior = dfDatos[dfDatos["Mes"] == parMes - 1]
    else:
        dfMesAnterior = dfDatos[dfDatos["Mes"] == parMes]

#
# Obtenemos los datos del mes
#
dfMesActual = dfDatos[dfDatos["Mes"] == parMes]

#
# Valores Productos vendidos
#
productosAct = dfMesActual["Cantidad"].sum()
productosAnt = dfMesAnterior["Cantidad"].sum()
variacion_prod = productosAct - productosAnt
# Valores Ventas realizadas
ordenesAct = dfMesActual["Cantidad"].count()
ordenesAnt = dfMesAnterior["Cantidad"].count()
variacion_ord = ordenesAct - ordenesAnt
# Valores Ganancias totales
ventasAct = dfMesActual["Ganancias"].sum()
ventasAnt = dfMesAnterior["Ganancias"].sum()
variacion_venta = ventasAct - ventasAnt

# Verificar si los filtros están activos
filtros_otros_activos = (
    parMes != meses_unicos[0] or
    parAno != anios_unicos[0] or
    parEdad != (edades_min, edades_max) or
    len(parUbicacion) > 0 or
    len(parGenero) > 0
)

if len(parProducto) > 0:
    st.write("") # Espacio

    #
    # Métricas
    #
    def metric():
        col1, col2, col3 = st.columns(3)
        
        # Definir colores reactivos
        color_prod = "#00aa00" if variacion_prod >= 0 else "#aa0000"
        color_ord = "#00aa00" if variacion_ord >= 0 else "#aa0000"
        color_venta = "#00aa00" if variacion_venta >= 0 else "#aa0000"
        
        # HTML para métricas con colores reactivos
        html_prod = f"""
        <div style="background-color: #040720; border: 2px solid {color_prod}; border-left: 4px solid {color_prod}; padding: 10px; margin: 5px; border-radius: 5px;">
            <div style="color: #ffffff; font-size: 14px;">Productos vendidos</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{productosAct:,}</div>
            <div style="color: {color_prod}; font-size: 16px; font-weight: bold;">{variacion_prod:+.0f}</div>
        </div>
        """
        
        html_ord = f"""
        <div style="background-color: #040720; border: 2px solid {color_ord}; border-left: 4px solid {color_ord}; padding: 10px; margin: 5px; border-radius: 5px;">
            <div style="color: #ffffff; font-size: 14px;">Ventas realizadas</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{ordenesAct:,}</div>
            <div style="color: {color_ord}; font-size: 16px; font-weight: bold;">{variacion_ord:+.0f}</div>
        </div>
        """
        
        html_venta = f"""
        <div style="background-color: #040720; border: 2px solid {color_venta}; border-left: 4px solid {color_venta}; padding: 10px; margin: 5px; border-radius: 5px;">
            <div style="color: #ffffff; font-size: 14px;">Ganancias totales</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: bold;">${ventasAct:,.0f}</div>
            <div style="color: {color_venta}; font-size: 16px; font-weight: bold;">${variacion_venta:+,.0f}</div>
        </div>
        """
        
        # Mostrar las métricas
        col1.markdown(html_prod, unsafe_allow_html=True)
        col2.markdown(html_ord, unsafe_allow_html=True)
        col3.markdown(html_venta, unsafe_allow_html=True)

    metric()

    st.write("") # Espacio
    st.write("") # Espacio

    # Primera dos columnas de gráficos
    col_v_meses, col_v_ubicacion = st.columns(2)

    #
    # Columna ventas por meses
    #
    with col_v_meses:
        with st.container(border=True):
            dfVentasMes = (
                dfDatos.groupby("Mes")
                .agg({"Ganancias": "sum"})
                .reset_index()
                )
            dfVentasMes['Mes_Nombre'] = dfVentasMes['Mes'].map(meses_dict)
            fig = px.line(
                dfVentasMes,
                x="Mes_Nombre",
                y="Ganancias",
                title="Ganancias totales por cada Mes",
                hover_data={"Mes_Nombre": False, "Mes": False}
                )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="MESES",
                yaxis_title="GANANCIAS",
                )
            st.plotly_chart(fig, use_container_width=True)

    #
    # Columna ventas por ubicación
    #
    with col_v_ubicacion:
        with st.container(border=True):
            dfVentasUbicacionMes = (
                dfDatos.groupby(["Mes", "Ubicacion"])
                .agg({"Ganancias": "sum"})
                .reset_index()
                .sort_values(by=["Mes", "Ganancias"], ascending=[True, False])
                )
            dfVentasUbicacionMes["Ubicacion"] = dfVentasUbicacionMes["Ubicacion"].str.capitalize()
            dfVentasUbicacionMes['Mes_Nombre'] = dfVentasUbicacionMes['Mes'].map(meses_dict)
            fig = px.bar(
                dfVentasUbicacionMes,
                x="Mes_Nombre",
                y="Ganancias",
                color="Ubicacion",
                title="Ganancias totales por Ubicación",
                barmode="group",
                labels={"Ubicacion": "Ubicación"},
                hover_data={"Mes_Nombre": False, "Mes": False, "Ubicacion": False}
            )
            fig.update_layout(
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="MESES",
                yaxis_title="GANANCIAS",
            )
            st.plotly_chart(fig, use_container_width=True)

    #
    # Gráfico de género
    #
    with st.container(border=True):
        dfVentasGenero = (
            dfMesActual.groupby(["Producto", "Genero"])
            .agg({"Ganancias": "sum", "Cantidad": "sum"})
            .reset_index()
        )
        dfVentasGenero["Genero"] = dfVentasGenero["Genero"].str.capitalize()
        fig = px.bar(
            dfVentasGenero,
            x="Producto",
            y="Ganancias",
            color="Genero",
            title=f"Ganancias totales por género en el mes de {meses_dict.get(parMes, 'Desconocido')}",
            barmode="group",
            labels={"Genero": "Género"},
            hover_data={"Producto": False, "Genero": False, "Cantidad": False, "Ganancias": True}
        )
        fig.update_layout(
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="PRODUCTOS",
            yaxis_title="GANANCIAS",
        )
        st.plotly_chart(fig, use_container_width=True)

    #
    # Gráfico de edad promedio
    #
    with st.container(border=True):
        dfEdadProducto = (
            dfMesActual.groupby("Producto")
            .agg({"Edad": "mean", "Ganancias": "sum"})
            .reset_index()
        )
        dfEdadProducto["Edad"] = dfEdadProducto["Edad"].round(1)
        fig = px.bar(
            dfEdadProducto,
            x="Producto",
            y="Ganancias",
            color="Producto",
            title=f"Ganancias totales por edad promedio en el mes de {meses_dict.get(parMes, 'Desconocido')}",
            text="Edad",
            hover_data={"Producto": False, "Edad": False, "Ganancias": True}
        )
        fig.update_layout(
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showticklabels=False, title="Edad Promedio"),
            yaxis_title="GANANCIAS",
        )
        st.plotly_chart(fig, use_container_width=True)

    #
    # Gráfico ventas por producto
    #
    with st.container(border=True):
        dfVentasProducto = (
            dfDatos.groupby(["Mes", "Producto"])
            .agg({"Ganancias": "sum", "Cantidad": "sum"})
            .reset_index()
            .sort_values(by=["Mes", "Producto"])
        )
        dfVentasProducto = dfVentasProducto[dfVentasProducto["Mes"] == parMes]
        fig = px.bar(
            dfVentasProducto,
            x="Producto",
            y="Ganancias",
            color="Producto",
            title=f"Ganancias y cantidad de productos vendidos en el mes de {meses_dict.get(parMes, 'Desconocido')}",
            text="Cantidad",
            hover_data={"Producto": False, "Cantidad": False}
        )
        fig.update_layout(
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showticklabels=False, title="Cantidad Vendida"),
            yaxis_title="GANANCIAS",
        )
        st.plotly_chart(fig, use_container_width=True)

elif filtros_otros_activos:
    st.info("Aún no has filtrado por producto. Seleccioná al menos un producto para ver los gráficos.")

if len(parProducto) == 0 and not filtros_otros_activos:
    st.info("Para ver las gráficas, seleccioná al menos un producto en los filtros.")

#
# Tabla de precios y ganancias por producto
#
with st.container(border=True):
    st.subheader("Precios y Ganancias por Producto")
    dfCostos = data_costos()
    dfStock = data_stock()[["Nombre", "Precio_Venta"]]
    dfCostos = dfCostos.merge(dfStock, on="Nombre", how="left")
    dfCostos["Ganancia"] = (
        dfCostos["Precio_Venta"]
        - dfCostos["Precio_Compra"]
        - (dfCostos["Precio_Venta"] * dfCostos["Impuesto"] / 100)
    )
    dfCostos_renamed = dfCostos.rename(
        columns={
            "Precio_Compra": "Precio Compra",
            "Precio_Venta": "Precio Venta"
        }
    )
    st.dataframe(
        dfCostos_renamed[["Nombre", "Categoria", "Precio Compra", "Precio Venta", "Ganancia"]],
        height=400,
        use_container_width=True
    )
