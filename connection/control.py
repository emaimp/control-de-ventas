import asyncio
import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# -----------------------------------------------------------------------------------
# Conexión a la base de datos
db_config_registros = st.secrets["conex_mysql"]
# -----------------------------------------------------------------------------------
# Configuración
DATABASE_URL = (
    f"mysql+aiomysql://"
    f"{db_config_registros['user']}:{db_config_registros['password']}@"
    f"{db_config_registros['host']}/"
    f"{db_config_registros['database2']}"
)
# -----------------------------------------------------------------------------------
# Motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
# -----------------------------------------------------------------------------------
# Sesión asíncrona
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# -----------------------------------------------------------------------------------
# Conexión ventas
async def get_ventas_mysql():
    # Sesión asíncrona
    async with AsyncSessionLocal() as session:
        try:
            # Ejecutar la consulta asíncrona
            result = await session.execute(text("SELECT * FROM ventas"))
            # Obtener todos los resultados
            rows = result.fetchall()
            # Convertir a DataFrame
            df = pd.DataFrame(
                rows,
                columns=[
                    "Ropa",
                    "Marca",
                    "Talla",
                    "Color",
                    "Precio",
                    "Cantidad",
                    "Total",
                    "Dia",
                    "Mes",
                    "Anio",
                    "Fecha",
                ],
            )
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None


# -----------------------------------------------------------------------------------
# Data Frame
@st.cache_data()
def data_ventas():
    df = asyncio.run(get_ventas_mysql())
    return df


# -----------------------------------------------------------------------------------