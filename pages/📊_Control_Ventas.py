import time
import streamlit as st
import plotly.express as px
from streamlit_extras.grid import grid
from connection.control import data_ventas
from streamlit_extras.metric_cards import style_metric_cards

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
    dfDatos = data_ventas()
# ----------------------------------------------------------------------------------------
# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 33, 31])
with colt2:
    # Titulo
    st.header("Control de Ventas")
    st.write("")
# ========================================================================================
my_grid = grid([3])
with my_grid.expander("Filtros", expanded=False):
    colop1, colop2, colop3 = st.columns([33, 34, 33])
    # Métrica producto vendidos (sumar cantidad)
    with colop1:
        with st.container(border=True):
            # Filtro de mes
            meses_unicos = sorted(dfDatos["Mes"].unique())
            parMes = st.select_slider(
                "Meses",
                options=meses_unicos,
                value=meses_unicos[0],  # Valor por defecto (mes 1)
                format_func=lambda x: f"Mes {x}",  # Formato visual
            )
    with colop2:
        with st.container(border=True):
            # Filtro de año
            anios_unicos = sorted(dfDatos["Anio"].unique())
            parAno = st.select_slider(
                "Años",
                options=anios_unicos,
                value=anios_unicos[0],  # Valor por defecto (primer año)
                format_func=lambda x: f"Año {x}",  # Formato visual
            )
    with colop3:
        with st.container(border=True):
            # Filtro de ropa
            parRopa = st.multiselect(
                "Ropa", options=sorted(dfDatos["Ropa"].unique()), placeholder=""
            )
            st.write("")
# ========================================================================================
# Si hay parámetros aplicamos los filtros
if parAno:
    dfDatos = dfDatos[dfDatos["Anio"] == parAno]
if parMes:
    dfDatos = dfDatos[dfDatos["Mes"] <= parMes]
if len(parRopa) > 0:
    dfDatos = dfDatos[dfDatos["Ropa"].isin(parRopa)]
# ----------------------------------------------------------------------------------------
# Obtenemos los datos del mes
dfMesActual = dfDatos[dfDatos["Mes"] == parMes]
# ----------------------------------------------------------------------------------------
# Obtenemos los datos del año
if parMes:
    if parMes > 1:
        dfMesAnterior = dfDatos[dfDatos["Mes"] == parMes - 1]
    else:
        dfMesAnterior = dfDatos[dfDatos["Mes"] == parMes]
# ----------------------------------------------------------------------------------------
# Valores Productos vendidos
productosAct = dfMesActual["Cantidad"].sum()
productosAnt = dfMesAnterior["Cantidad"].sum()
variacion = productosAnt - productosAct
# Valores Ventas realizadas
ordenesAct = dfMesActual["Cantidad"].count()
ordenesAnt = dfMesAnterior["Cantidad"].count()
variacion = ordenesAct - ordenesAnt
# Valores Ganancias totales
ventasAct = dfMesActual["Total"].sum()
ventasAnt = dfMesAnterior["Total"].sum()
variacion = ventasAct - ventasAnt


# ========================================================================================
# Métricas
def metric():
    col1, col2, col3 = st.columns(3)
    # Métrica producto vendidos (sumar cantidad)
    col1.metric(label="Productos vendidos", value=productosAct, delta=int(variacion))
    # Métrica ventas realizadas (contar cantidad)
    col2.metric(label="Ventas realizadas", value=ordenesAct, delta=int(variacion))
    # Métrica ventas totales (suma todo el total ventas)
    col3.metric(label="Gancias totales", value=ventasAct, delta=int(variacion))
    # Aplicar el estilo personalizado
    style_metric_cards(
        background_color="#040720", border_color="#ff8000", border_left_color="#ff8000"
    )


metric()
# ========================================================================================
# Columnas con una proporción de %
col_g_meses, col_g_mes = st.columns([50, 50])
with col_g_meses:
    with st.container(border=True):
        dfVentasMes = dfDatos.groupby("Mes").agg({"Total": "sum"}).reset_index()
        fig = px.line(dfVentasMes, x="Mes", y="Total", title="Ganancias por meses")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
with col_g_mes:
    with st.container(border=True):
        dfVentasRopa = (
            dfMesActual.groupby("Ropa")
            .agg({"Total": "sum"})
            .reset_index()
            .sort_values(by="Total", ascending=False)
        )
        fig = px.bar(
            dfVentasRopa,
            x="Ropa",
            y="Total",
            title=f"Ganancia del mes: {parMes}",
            color="Ropa",
            text_auto=",.0f",
        )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
# ========================================================================================
# Tablas de productos top
with st.container(border=True):
    col_topmax, col_topmin = st.columns(2)
    dfProductosVentas = (
        dfMesActual.groupby(["Marca", "Ropa"])
        .agg({"Total": "sum", "Cantidad": "count"})
        .reset_index()
    )
    with col_topmax:
        st.subheader("Productos más vendidos")
        st.table(
            dfProductosVentas.sort_values(by="Cantidad", ascending=False).head(10)[
                ["Marca", "Ropa", "Total", "Cantidad"]
            ]
        )
    with col_topmin:
        st.subheader("Productos menos vendidos")
        st.table(
            dfProductosVentas.sort_values(by="Cantidad").head(10)[
                ["Marca", "Ropa", "Total", "Cantidad"]
            ]
        )
# ========================================================================================
