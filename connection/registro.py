import asyncio
import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Table, Column, MetaData, Integer, String, Float, Date

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
# Crear sesión asíncrona
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# -----------------------------------------------------------------------------------
# Crear una tabla que refleje la estructura de la base de datos
metadata = MetaData()
registros_table = Table("ventas",metadata,
    Column("Ropa", String),
    Column("Marca", String),
    Column("Talla", String),
    Column("Color", String),
    Column("Precio", Float),
    Column("Cantidad", Integer),
    Column("Total", Float),
    Column("Dia", Integer),
    Column("Mes", Integer),
    Column("Anio", Integer),
    Column("Fecha", Date),
)


# -----------------------------------------------------------------------------------
# Conexión registro
async def save_dataframe(df: pd.DataFrame):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                for _, row in df.iterrows():
                    # Preparar los datos a insertar
                    insert_stmt = registros_table.insert().values(
                        Ropa=row["Ropa"],
                        Marca=row["Marca"],
                        Talla=row["Talla"],
                        Color=row["Color"],
                        Precio=row["Precio"],
                        Cantidad=row["Cantidad"],
                        Total=row["Total"],
                        Dia=row["Dia"],
                        Mes=row["Mes"],
                        Anio=row["Anio"],
                        Fecha=row["Fecha"],
                    )
                    # Ejecutar la inserción asíncrona
                    await session.execute(insert_stmt)
                # Confirmar la transacción
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Error: {e}")
                return False
        return True


# -----------------------------------------------------------------------------------
# Carga de datos
@st.cache_data()
def save_data(df: pd.DataFrame):
    asyncio.run(save_dataframe(df))


# -----------------------------------------------------------------------------------
