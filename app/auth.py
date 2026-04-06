import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWSError
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.db import get_session
from app.models import User
from sqlmodel.ext.asyncio.session import AsyncSession

#Busca en mi archivo raiz una carpeta llamada .env para cargar las contrasenias, esto es fundamental para
#no sufrir riesgos de seguridad

load_dotenv()

#Aqui van las claves de acceso, las cuales estan en mi .env y las importa de ese archivo, la ventaja de este metodo
#es que puedo cambiar las contrasenias del .env siempre y el programa servira siempre y cuando exista ese archivo
SECRET_KEY = os.getenv("SECRET_KEY", "clave_de_respaldo_no_segura")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
CRYPT_SCHEMA = os.getenv("CRYPT_SCHEMA")

#Aqui le estamos diciendo que encriptador usara, el eschema o metodo, bcrypt es el bueno por excelencia, deprecated es
#por si se usan 2 metodos de encriptacion distintos, use ambos para la validacion de contrasenias
pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

#Realiza un hash a la contrasenia aplicando un "salt" para asegurar la diferencia entre 2 contrasenias iguales
def get_password_hash(password: str) -> str:
    password_truncada = password[:72]
    return pwd_context.hash(password_truncada)

#A la contrasenia colocada por el usuario, le agrega el mismo salt y hash para corroborar si es la misma que la de la DB
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#Aqui estamos brindando un token a cada peticion con un tiempo determinado, con ese token tienen acceso a nuestra API
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    
    #En Python, si modificas un diccionario directamente, modificas el original en todo el programa.
    #Hacemos .copy() para trabajar en un clon y no alterar los datos originales que nos enviaron.
    to_encode = data.copy()
    
    #Esto es para garantizar que funcione en cualquier uso horario
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Usamos la variable de entorno para los minutos
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    #"exp" es una palabra reservada para verificar el tiempo del token    
    to_encode.update({"exp": expire})

    #Aqui es donde codificamos el token para verificar que este bien y no haya sido modificado
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

#Le decimos a FastAPI y a Swagger UI dónde debe ir a buscar el token. 
#El "tokenUrl" debe coincidir exactamente con el nombre de tu ruta de login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Esta es la función "Guardia". Se ejecutará automáticamente cada vez que alguien 
#intente entrar a una ruta protegida.
async def obtener_usuario_actual (
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
        ):
    
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        #Intentamos abrir (decodificar) el token con nuestra llave secreta, esto es para evitar errores y asegurarnos
        #que esl token sea valido, de lo contrario levantar un HTTPError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        #Extraemos el "sub" (que sabemos que es el ID del usuario)
        id_usuario : str = payload.get("sub")

        #Si el token no tiene "sub", es un token inválido para nuestro sistema
        if id_usuario is None:
            raise excepcion_credenciales
    
    #Si el token expiró o la firma matemática no coincide, jose lanza JWTError
    except JWSError:
        raise excepcion_credenciales
    
    # Usamos session.get() que es más rápido que select().where() cuando buscamos por Primary Key
    usuario_db = await session.get(User, int(id_usuario))

    #Si el usuario fue borrado de la base de datos mientras su token seguía vivo
    if usuario_db is None:
        raise excepcion_credenciales

    return usuario_db

#Generamos una dependencia anidada, usara la verififacion de usuario y contraseña y verificara si tiene valor
#True en la casilla de "es_admin" en la base de datos
def obtener_usuario_admin(usuario_actual: User = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, #este codigo significa que sabe quien eres, pero no podees permisos
            detail="El usuario no tiene permisos de administrador"
        )
    return usuario_actual