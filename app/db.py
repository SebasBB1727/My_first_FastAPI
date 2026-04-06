from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

#Aqui vamos a crear un SQLite ara evitar postgres y fricciones con un servidor externo.
#El dia en el que migre a Postgres, solo tengo que cambiar las tres siguientes lineas a la DB
#que yo quiera usar, y todo el codigo sigue funcionando exactamente igual.
#Las URLs de conexión a bases de datos siguen el estándar universal: 
#(tecnologia://usuario:clave@servidor:puerto/nombre_base_datos)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

engine = create_async_engine(sqlite_url, echo=True) 
#echo me arroja en consola todo lo que hace SQLAlchemy, excelente herramienta para debugging, pero en produccion se quita 
#o se pone False, para ahorrar memoria

async def create_db_and_tables():
    #La funcion de crear tablas tambien es async
    async with engine.begin() as conn:
        #Usamos conn.run_sync() para ejecutar la función síncrona vieja
        #de forma segura dentro de nuestro entorno asíncrono nuevo.
        await conn.run_sync(SQLModel.metadata.create_all)

#Este apartado de Session es para generar una session y cerrarla de forma automatica con el yield,
#esto se hace para evitar tener sesiones abiertas y no cargar la DB

async def get_session():
    async with AsyncSession(engine) as session:
        yield session