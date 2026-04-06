import getpass
import asyncio
from sqlmodel import select 
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import engine, create_db_and_tables
from app.models import User
from app.auth import get_password_hash

async def guardar_admin_en_db(nuevo_admin, usuario):
    
    await create_db_and_tables()
    
    async with AsyncSession(engine) as session:
        statement = select(User).where(User.nombre_usuario == usuario)
        resultados = await session.exec(statement)
        usuario_existente = resultados.first()

        if usuario_existente:
            print(f"\n Error: El usuario '{usuario}' ya existe. No se puede duplicar.")
            return False 
        
        session.add(nuevo_admin)
        await session.commit()
        return True


def crear_usuario_admin():
    print("\n====== Inizializacion de Administrador de Sistema ======")
    counter=3
    while counter > 0:
        print("\n")
        usuario = input("Ingrese el nombre del usuario admin: ").strip() #strip.() quita los espacios vacios, para evitar errores de dedo por espacios
        correo = input("Ingrese el correo electronico admin: ").strip()

        if not usuario or not correo:
            print("\nLos campos usuario o correo no pueden estar vacios")
            continue
        
        print("\nConfirmamos los datos:")
        print(usuario)
        print(correo)
        print("Los datos son correctos? (Escribe (Y) para confirmar o (N) para reintentar)")
        confirm = input("(Y/N): ")
        counter -= 1

        if confirm.lower() == "y":
            break

        elif counter == 0:
            return

        else:
            continue

    trys = 3
    while trys > 0:
        print("\n")
        password = getpass.getpass("Ingresa la password: (8 caracteres min): ")
        password_confirm = getpass.getpass("Confirma la password: ")

        if password != password_confirm:
            trys -= 1
            print(f"\n\nLas passwords no coinciden, intentos restantes {trys}")
            continue

        if len(password) < 8:
            trys -= 1
            print(f"\n\nLas password debe tener minimo 8 caracteres, intentos restantes {trys}")
            continue

        break

    if trys == 0:
        print("\nHas superado el limite de intentos. Operación cancelada.")
        return
    
    #Utilizamos el metodo ya definido en auth para hashear la password exactamente igual que los otros usuarios
    #para que tengan la misma seguridad
    hash_generado = get_password_hash(password)

    nuevo_admin = User(
        nombre_usuario= usuario,
        correo = correo,
        hashed_password=hash_generado,
        es_admin=True
    )
    exito = asyncio.run(guardar_admin_en_db(nuevo_admin, usuario))

    if exito:
        print(f"\nEl usuario {usuario} ha sido creado exitosamente como admin")


if __name__ == "__main__":
    crear_usuario_admin()