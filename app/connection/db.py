import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# Conexión a la base de datos madre
DATABASE_NAME = "comercio"
db_config = st.secrets["conex_mysql"]

# Crear engine principal usando pymysql
def get_engine(database=None):
    engine_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}"
    if database:
        engine_url += f"/{database}"
    return create_engine(engine_url)

# Función para crear la base de datos y tablas
def initialize_database():
    # Engine temporal sin especificar la base de datos
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Crear base de datos si no existe
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
            conn.commit()

        # Ahora crear engine para la base de datos específica
        engine_db = get_engine(DATABASE_NAME)
        with engine_db.connect() as conn:
            # Leer y ejecutar las sentencias SQL de las tablas
            with open("app/database/productos.sql", "r") as f:
                sql_productos = f.read()
            with open("app/database/ventas.sql", "r") as f:
                sql_ventas = f.read()
            with open("app/database/costos.sql", "r") as f:
                sql_costos = f.read()

            # Ejecutar creación de tablas
            for sql in sql_productos.split(";"):
                if sql.strip():
                    conn.execute(text(sql))
            for sql in sql_ventas.split(";"):
                if sql.strip():
                    conn.execute(text(sql))
            for sql in sql_costos.split(";"):
                if sql.strip():
                    conn.execute(text(sql))

            conn.commit()
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
        st.stop()

# Variable global para la inicialización
database_initialized = False

# Función para obtener engine
def get_connection():
    global database_initialized
    if not database_initialized:
        try:
            initialize_database()
            database_initialized = True
        except Exception as e:
            st.error(f"Error al inicializar la base de datos: {e}")
            st.stop()
    return get_engine(DATABASE_NAME)

# Data Frame de productos
def data_stock():
    query = """SELECT
        id AS ID,
        nombre AS Nombre,
        categoria AS Categoria,
        precio_venta AS Precio_Venta,
        stock AS Stock
    FROM productos"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    return df

# Data Frame de costos
def data_costos():
    query = """SELECT
        c.id AS ID,
        p.nombre AS Nombre,
        p.categoria AS Categoria,
        c.precio_compra AS Precio_Compra,
        c.impuesto AS Impuesto
    FROM costos c
    JOIN productos p ON c.producto_id = p.id"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    return df

# Data Frame de ventas
def data_ventas():
    query = """SELECT
        p.nombre AS Producto,
        v.cantidad AS Cantidad,
        (p.precio_venta - c.precio_compra - p.precio_venta * (c.impuesto / 100)) * v.cantidad AS Ganancias,
        v.edad_cliente AS Edad,
        v.genero_cliente AS Genero,
        v.ubicacion AS Ubicacion,
        v.dia AS Dia,
        v.mes AS Mes,
        v.anio AS Anio,
        v.fecha AS Fecha
    FROM ventas v
    JOIN productos p ON v.producto_id = p.id
    JOIN costos c ON c.producto_id = p.id"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    return df

# Data Frame de predicciones
def cargar_datos():
    query = """SELECT
        v.fecha,
        SUM( (p.precio_venta - c.precio_compra - p.precio_venta * (c.impuesto / 100)) * v.cantidad ) AS Ganancias
    FROM ventas v
    JOIN productos p ON v.producto_id = p.id
    JOIN costos c ON c.producto_id = p.id
    GROUP BY v.fecha
    ORDER BY v.fecha"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df
