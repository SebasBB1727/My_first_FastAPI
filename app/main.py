from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db import create_db_and_tables, get_session
from app.models import Note, CrearNota, CrearUsuario, User
from sqlmodel import select, delete
from app.auth import get_password_hash, verify_password, create_access_token, obtener_usuario_actual, obtener_usuario_admin
from app.ai_service import generar_resumen_nota
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

#Le estamos asignando un formato de arranque "seguro" a la app, para que cree los recursos antes de
#ejecutarse y cerrarse al apagarse
#todo lo que esta antes del yield se ejecuta antes de encender el servidor y lo que esta despues
#se ejecuta al apagar el servidor, por eso se lo pasamos como argumento a FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


# Le damos permiso a cualquier página web de hablar con nuestra API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite peticiones desde cualquier lugar
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, DELETE, etc.
    allow_headers=["*"], # Permite enviar Tokens en los headers
)
#En el apartado: "session: Session = Depends(get_session)" basicamente le estamos diciendo
#que ejecute la sesion que ya definimos en "db.py" en si esto no cambia, siempre se pone asi

#EL usuario_actual: User = Depends(obtener_usuario_actual) se ejecuta antes de correr el codigo, corriendo las autenticaciones
#previamente definidas, para convertir a usuario_actual en un objeto con los valores encontrados en la tabla y
#poder acceder a el id y ejecutarlo de forma correcta en la DB
@app.post("/notes/")
async def crear_nota(nota_entrada: CrearNota, 
               session: AsyncSession = Depends(get_session), 
               usuario_actual: User = Depends(obtener_usuario_actual)
               ):
    
    #Aqui inyectaremos la funcion de generacion de nota de la IA
    resumen_ia = await generar_resumen_nota(nota_entrada.contenido)

    #Aqui el CrearNota verifica que los datos del json vengan en el formato que se le pido, si no
    #solito regresa un erros FastAPI, despues los asigna a nota_entrada, se los asignamos a nueva_nota a 
    #con tipo Note y le brindamos los datos listos para hacer un commit exitoso a la base de datos
    nueva_nota = Note(
        titulo= nota_entrada.titulo,
        nota= resumen_ia,
        contenido= nota_entrada.contenido,
        owner_id= usuario_actual.id
    )
    
    #Aqui lo que hacemos es formar los datos, subirlos a la base de datos y refrescar la informacion para que
    #regrese la nueva nota con el id que se le asigno cuando se hizo el commit
    # session.add() NO lleva await porque solo es una preparación en la memoria de Python, no toca el disco duro.
    session.add(nueva_nota)
    #Las operaciones que tocan el disco duro AHORA llevan 'await'
    await session.commit()
    await session.refresh(nueva_nota)

    return nueva_nota

#Registra a un usuario
@app.post("/registro/")
async def registrar_usuario(usuario_entrada: CrearUsuario, session: AsyncSession = Depends(get_session)):
    
    hash_generado = get_password_hash(usuario_entrada.password_plana)

    nuevo_usuario = User(
        nombre_usuario = usuario_entrada.nombre_usuario,
        correo= usuario_entrada.correo,
        hashed_password = hash_generado
    )

    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario)

    #IMPORTANTE- NUNCA regresar el hash por seguridad
    return {"mensaje": f"Usuario {nuevo_usuario.nombre_usuario} creado exitosamente"}

@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):

    #Aqui el statement verifica en la tabla si existe el mismo usuario que recibo en la autenticacion
    #el usuario_db, obtiene todos los valores asociados al statement y lo convierte en un objeto para 
    #acceder a el con un "." 
    statement = select(User).where(User.nombre_usuario == form_data.username)
    resultado = await session.exec(statement)
    usuario_db = resultado.first()

    #Aqui verifica que exista usuario y que coincida la contraseña con la del usuario
    if not usuario_db or not verify_password(form_data.password, usuario_db.hashed_password):
        
        #Aqui estamos lanzando una excepcion de http, se recomienda usar "status." para que nos arrojen los codigos
        #de estado y minimizemos el error de tipado y realicemos un "clean code"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    #Aqui le generamos el token, pero se lo realizamos al id del usuario obtenido por que es el unico que no se puede
    #repetir en toda la tabla, si lo hicieramos con el usuario o contraseña, existiria la posibilidad de tener duplicados
    #y eso es un error de seguridad
    #Ademas, nos servira para asignarle id a la tabla "Note" extrayendo ese "sub"
    token_jwt = create_access_token(data={"sub": str(usuario_db.id)})

    #Se usan esas llaves de diccionario por que es como lo dicta la industria ({"WWW-Authenticate": "Bearer"},
    #{"sub": str(usuario_db.id)}, {"access_token" : token_jwt, "token_type": "bearer"})
    return {"access_token" : token_jwt, "token_type": "bearer"}

@app.get("/notes/")
async def ver_notas_usuario(session: AsyncSession = Depends(get_session), usuario_actual: User = Depends(obtener_usuario_actual)):
    
    #statement es la peticion que se le realizara a la base de datos, son los filtros escritos en python y traducidos a SQL
    statement = select(Note).where(Note.owner_id == usuario_actual.id)
    #session.exec()es cuantos resultados y como los vamos a poner, desde solo mostrar el primero, todos, el tulrimo, etc
    resultados = await session.exec(statement)
    note_db = resultados.all()
    return note_db

@app.get("/notes/all", dependencies=[Depends(obtener_usuario_admin)])
async def ver_notas(session: AsyncSession = Depends(get_session)):
    
    statement = select(Note)
    
    resultado = await session.exec(statement)
    note_db = resultado.all()
    return note_db

@app.get("/usuarios/", dependencies=[Depends(obtener_usuario_admin)])
async def obtener_usuarios(session: AsyncSession = Depends(get_session)):
    statement = select(User)

    resultado = await session.exec(statement)
    user_db = resultado.all()
    return user_db

@app.delete("/notes/all")
async def borrar_db_notes(session: AsyncSession = Depends(get_session), admin_actual: User = Depends(obtener_usuario_admin)):

    statement = delete(Note)

    usuario = admin_actual.nombre_usuario

    await session.exec(statement)
    await session.commit()

    return {"mensaje": f"Base de datos 'Notes' borrada por el admin {usuario} exitosamente"}