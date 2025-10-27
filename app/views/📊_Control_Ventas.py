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

# Cargar styles.css
with open("app/config/styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Toast para cargar los datos
with st.spinner("Cargando..."):
    time.sleep(1)
    dfDatos = data_ventas()

if dfDatos.empty:
    st.error("No hay datos de ventas con costos asociados.")
    st.stop()

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 34, 30])
with colt2:
    # Titulo
    st.header("Control de Ventas 📊")
    st.write("") # Espacio
    st.write("") # Espacio

#
# Columas para los filtros
#
my_grid = grid([6])
with my_grid.expander("Filtros", expanded=False):

    # Primera fila: mes, año, edad
    col_mes, col_anio, col_edad = st.columns([1, 1, 1])
    
    # Columna para el filtro de mes
    with col_mes:
        with st.container(border=True):
            # Filtro de mes
            meses_unicos = sorted(dfDatos["Mes"].unique())
            parMes = st.select_slider(
                "Meses",
                options=meses_unicos,
                value=meses_unicos[0],  # Valor por defecto (mes 1)
                format_func=lambda x: f"Mes {x}",  # Formato visual
            )
    # Columna para el filtro del año
    with col_anio:
        with st.container(border=True):
            # Filtro de año
            anios_unicos = sorted(dfDatos["Anio"].unique())
            parAno = st.select_slider(
                "Años",
                options=anios_unicos,
                value=anios_unicos[0],  # Valor por defecto (primer año)
                format_func=lambda x: f"Año {x}",  # Formato visual
            )
    # Columna para el filtro de la edad
    with col_edad:
        with st.container(border=True):
            # Filtro de edad (rango)
            edades_min = int(dfDatos["Edad"].min())
            edades_max = int(dfDatos["Edad"].max())
            parEdad = st.slider(
                "Edad",
                min_value=edades_min,
                max_value=edades_max,
                value=(edades_min, edades_max)
            )

    # Segunda fila: producto, ubicación, género
    col_producto, col_ubicacion, col_genero = st.columns([1, 1, 1])
    
    # Columna para el filtro de los productos
    with col_producto:
        with st.container(border=True):
            # Filtro de producto
            productos_unicos = sorted(dfDatos["Producto"].unique())
            parProducto = st.multiselect(
                "Producto", options=productos_unicos, placeholder=""
            )
    # Columna para el filtro de la ubicación
    with col_ubicacion:
        with st.container(border=True):
            # Filtro de ubicacion
            ubicaciones_unicas = sorted(dfDatos["Ubicacion"].unique())
            parUbicacion = st.multiselect(
                "Ubicacion", options=ubicaciones_unicas, placeholder=""
            )
    # Columna para el filtro del género
    with col_genero:
        with st.container(border=True):
            # Filtro de genero
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

#
# Primera dos columnas de gráficos
#
col_v_meses, col_v_ubicacion = st.columns(2)

# Columna ventas por meses
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

# Columna ventas por mes y ubicación
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
            text="Ubicacion",
            barmode="group",
            labels={"Ubicacion": "Ubicación"},
            hover_data={"Mes_Nombre": False, "Mes": False, "Ubicacion": False}
            )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="MESES",
            yaxis_title="GANANCIAS",
            )
        st.plotly_chart(fig, use_container_width=True)

#
# Segunda dos columnas de gráficos
#
col_v_edad, col_v_genero = st.columns(2)

# Columna ventas por edad
with col_v_edad:
    with st.container(border=True):
        dfEdadProducto = (
            dfMesActual.groupby("Producto")
            .agg({"Edad": "mean", "Ganancias": "sum"})
            .reset_index()
        )
        dfEdadProducto["Edad"] = dfEdadProducto["Edad"].round(1)
        dfEdadProducto["Edad_Texto"] = "Edad: " + dfEdadProducto["Edad"].astype(str)
        fig = px.bar(
            dfEdadProducto,
            x="Producto",
            y="Ganancias",
            title=f"Ganancias totales por edad promedio en el mes de {meses_dict.get(parMes, 'Desconocido')}",
            text="Edad_Texto",
            hover_data={"Producto": False, "Edad": False, "Edad_Texto": False}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="PRODUCTOS",
            yaxis_title="GANANCIAS",
        )
        st.plotly_chart(fig, use_container_width=True)

# Columna ventas por género
with col_v_genero:
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
            title=f"Ganancia totales por género en el mes de {meses_dict.get(parMes, 'Desconocido')}",
            text="Genero",
            barmode="group",
            labels={"Genero": "Género"},
            hover_data={"Producto": False, "Genero": False}
        )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="PRODUCTOS",
            yaxis_title="GANANCIAS",
        )
        st.plotly_chart(fig, use_container_width=True)

#
# Container para el gráfico ventas por producto
#
with st.container(border=True):
    dfVentasProducto = (
        dfDatos.groupby(["Mes", "Producto"])
        .agg({"Ganancias": "sum", "Cantidad": "sum"})
        .reset_index()
        .sort_values(by=["Mes", "Producto"])
    )
    dfVentasProducto['Mes_Nombre'] = dfVentasProducto['Mes'].map(meses_dict)
    fig = px.bar(
        dfVentasProducto,
        x="Mes_Nombre",
        y="Ganancias",
        color="Producto",
        title="Ganancias y cantidad de productos vendidos totales",
        text="Cantidad",
        barmode="relative",
        hover_data={"Mes_Nombre": False, "Mes": False, "Producto": False, "Cantidad": False}
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="MESES",
        yaxis_title="GANANCIAS",
    )
    st.plotly_chart(fig, use_container_width=True)

#
# Tablas de productos top
#
with st.container(border=True):
    col_topmax, col_topmin = st.columns(2)
    dfProductosVentas = (
        dfMesActual.groupby(["Producto", "Ubicacion"])
        .agg({"Ganancias": "sum", "Cantidad": "sum"})
        .reset_index()
    )
    with col_topmax:
        st.subheader("Productos más vendidos")
        st.table(
            dfProductosVentas.sort_values(by="Cantidad", ascending=False).head(10)[
                ["Producto", "Ubicacion", "Ganancias", "Cantidad"]
            ]
        )
    with col_topmin:
        st.subheader("Productos menos vendidos")
        st.table(
            dfProductosVentas.sort_values(by="Cantidad", ascending=True).head(10)[
                ["Producto", "Ubicacion", "Ganancias", "Cantidad"]
            ]
        )

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
