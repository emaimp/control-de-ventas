import asyncio
import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# ------------------------------------------------------------------------------
# Conexión a la base de datos
db_config_registros = st.secrets["conex_mysql"]
# ------------------------------------------------------------------------------
# Configuración
DATABASE_URL = (
    f"mysql+aiomysql://"
    f"{db_config_registros['user']}:{db_config_registros['password']}@"
    f"{db_config_registros['host']}/"
    f"{db_config_registros['database2']}"
)
# ------------------------------------------------------------------------------
# Crear el motor asíncrono para SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)
# ------------------------------------------------------------------------------
# Crear la sesión asíncrona
SessionAsync = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ------------------------------------------------------------------------------
# Función para cargar los datos
async def cargar_datos_sqlalchemy():
    try:
        # Sesión asíncrona
        async with SessionAsync() as session:
            # Consulta asíncrona usando text()
            result = await session.execute(
                text("SELECT Fecha, Total FROM ventas;")
            )
            rows = result.fetchall()  # Obtener los resultados
            # Convertir los resultados en DataFrame
            df = pd.DataFrame(rows, columns=["Fecha", "Total"])
            # Columna 'Fecha' en formato datetime
            df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y-%m-%d")
            return df
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


# ------------------------------------------------------------------------------
# Carga de datos
@st.cache_data()
def cargar_datos():
    return asyncio.run(cargar_datos_sqlalchemy())


# ------------------------------------------------------------------------------
