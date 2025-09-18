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

            # Ejecutar creación de tablas
            for sql in sql_productos.split(";"):
                if sql.strip():
                    conn.execute(text(sql))
            for sql in sql_ventas.split(";"):
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
    query = "SELECT * FROM productos"
    engine = get_connection()
    df = pd.read_sql(query, engine)
    return df

# Data Frame de ventas
def data_ventas():
    query = """SELECT
        p.nombre AS Producto,
        cantidad AS Cantidad,
        precio_total AS Total,
        edad_cliente AS Edad,
        genero_cliente AS Genero,
        ubicacion AS Ubicacion,
        dia AS Dia,
        mes AS Mes,
        anio AS Anio,
        fecha AS Fecha
    FROM ventas v
    JOIN productos p ON v.producto_id = p.id"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    return df

# Data Frame de predicciones (con regressors adicionales)
def cargar_datos():
    query = """SELECT
        fecha,
        SUM(precio_total) AS Total,
        AVG(edad_cliente) AS Edad_Promedio,
        COUNT(CASE WHEN genero_cliente = 'femenino' THEN 1 END) / COUNT(*) AS Proporcion_Femenino,
        COUNT(CASE WHEN ubicacion = 'local 1' THEN 1 END) / COUNT(*) AS Proporcion_Local1
    FROM ventas
    GROUP BY fecha
    ORDER BY fecha"""
    engine = get_connection()
    df = pd.read_sql(query, engine)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df
