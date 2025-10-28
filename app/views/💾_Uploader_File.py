import pandas as pd
import streamlit as st
from sqlalchemy import text
from connection.db import get_connection

# Configuración de inicio
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    )

# Titulo de la pagina
colt1, colt2, colt3 = st.columns([36, 33, 31])
with colt2:
    # Titulo
    st.header("Carga de Datos 💾")
    st.write("")
    st.write("") # Espacio
    st.write("")

#
# Funciones para validar y sanitizar datos
#
def validar_productos(df):
    required_cols = ['nombre', 'categoria', 'precio_venta', 'stock']
    if not all(col in df.columns for col in required_cols):
        return False, f"Faltan columnas requeridas: {required_cols}"
    # Sanitizar tipos
    df['precio_venta'] = df['precio_venta'].astype(int)
    df['stock'] = df['stock'].astype(int)
    return True, df

def validar_costos(df):
    required_cols = ['producto_id', 'precio_compra', 'impuesto']
    if not all(col in df.columns for col in required_cols):
        return False, f"Faltan columnas requeridas: {required_cols}"
    # Sanitizar tipos
    df['producto_id'] = df['producto_id'].astype(int)
    df['precio_compra'] = df['precio_compra'].astype(float)
    df['impuesto'] = df['impuesto'].astype(float)
    return True, df

def validar_ventas(df):
    required_cols = ['producto_id', 'cantidad', 'precio_total', 'edad_cliente', 'genero_cliente', 'ubicacion', 'dia', 'mes', 'anio', 'fecha']
    if not all(col in df.columns for col in required_cols):
        return False, f"Faltan columnas requeridas: {required_cols}"
    return True, df

#
# Función para insertar productos
#
def insertar_productos(engine, df):
    inserted = 0
    errors = []
    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(
                    text("INSERT INTO productos (nombre, categoria, precio_venta, stock) VALUES (:nombre, :categoria, :precio_venta, :stock)"),
                    {
                        'nombre': row['nombre'],
                        'categoria': row['categoria'],
                        'precio_venta': row['precio_venta'],
                        'stock': row['stock']
                    }
                )
                inserted += 1
            except Exception as e:
                errors.append(f"Error en fila {_}: {str(e)}")
    return inserted, errors

#
# Función para insertar costos
#
def insertar_costos(engine, df):
    inserted = 0
    errors = []
    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(
                    text("INSERT INTO costos (producto_id, precio_compra, impuesto) VALUES (:producto_id, :precio_compra, :impuesto)"),
                    {
                        'producto_id': row['producto_id'],
                        'precio_compra': row['precio_compra'],
                        'impuesto': row['impuesto']
                    }
                )
                inserted += 1
            except Exception as e:
                errors.append(f"Error en fila {_}: {str(e)}")
    return inserted, errors

#
# Función para insertar ventas
#
def insertar_ventas(engine, df):
    inserted = 0
    errors = []
    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(
                    text("""
                        INSERT INTO ventas (producto_id, cantidad, precio_total, edad_cliente, genero_cliente, ubicacion, dia, mes, anio, fecha)
                        VALUES (:producto_id, :cantidad, :precio_total, :edad_cliente, :genero_cliente, :ubicacion, :dia, :mes, :anio, :fecha)
                    """),
                    {
                        'producto_id': row['producto_id'],
                        'cantidad': row['cantidad'],
                        'precio_total': row['precio_total'],
                        'edad_cliente': row['edad_cliente'],
                        'genero_cliente': row['genero_cliente'],
                        'ubicacion': row['ubicacion'],
                        'dia': row['dia'],
                        'mes': row['mes'],
                        'anio': row['anio'],
                        'fecha': pd.to_datetime(row['fecha']).date()
                    }
                )
                inserted += 1
            except Exception as e:
                errors.append(f"Error en fila {_}: {str(e)}")
    return inserted, errors

#
# Selector de tabla destino
#
destino = st.radio(
    "Selecciona los datos a cargar:",
    options=["productos", "costos", "ventas"],
    captions=[
        "Columnas requeridas: nombre, categoria, precio_venta, stock",
        "Columnas requeridas: producto_id, precio_compra, impuesto",
        "Columnas requeridas: producto_id, cantidad, precio_total, edad_cliente, genero_cliente, ubicacion, dia, mes, anio, fecha"
        ]
    )

#
# Zona de carga
#
uploaded_files = st.file_uploader(
    "Archivos compatibles (.xlsx .xls) o csv",
    accept_multiple_files=True,
    type=["xlsx", "xls", "csv"]
    )

# Verificar si se han subido archivos
if uploaded_files:
    # Procesar cada archivo subido
    for i, uploaded_file in enumerate(uploaded_files):
        # Leer archivo según el tipo
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write(f"**Vista de {uploaded_file.name}:**")
        st.dataframe(df)

        # Botón para confirmar carga por archivo
        button_1, button_2, button_3 = st.columns(3)
        with button_2:
            if st.button(f"Cargar '{uploaded_file.name}'", type="primary", width="stretch"):
                # Verificar y validar
                if destino == "productos":
                    valido, resultado = validar_productos(df)
                elif destino == "costos":
                    valido, resultado = validar_costos(df)
                elif destino == "ventas":
                    valido, resultado = validar_ventas(df)
                else:
                    st.error("Selección de tabla no válida.")
                    valido = False

                if not valido:
                    st.error(resultado)
                else:
                    df = resultado
                    # Intentar conexión e inserción
                    engine = get_connection()
                    if destino == "productos":
                        inserted, errors = insertar_productos(engine, df)
                    elif destino == "costos":
                        inserted, errors = insertar_costos(engine, df)
                    elif destino == "ventas":
                        inserted, errors = insertar_ventas(engine, df)

                    if inserted > 0:
                        st.success(f"Todos los datos se cargaron correctamente.")
                    if errors:
                        st.warning("Errores en algunas inserciones:")
                        for error in errors:
                            st.write(error)
