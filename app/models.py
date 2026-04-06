from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

#Generaremos los modelos base que deberan de seguir para recibir datos y mandar error si no se reciben de esa manera
class NoteBase(SQLModel):
    titulo: str
    contenido: Optional[str] = None

class UserBase(SQLModel):
    nombre_usuario: str = Field(index = True, unique = True)
    correo: str
    es_admin: bool = Field(default=False)

#En estos metodos creamos las tablas por el argumento table=True, toma los valores base anteriores y agrega los valores
#adicionales programados
class User(UserBase, table = True):
    id: Optional[int] = Field(default= None, primary_key= True)
    hashed_password: str
    notas: List["Note"] = Relationship(back_populates="owner")


class Note(NoteBase, table = True):
    id: Optional[int] = Field(default= None, primary_key= True)
    nota: str
    owner_id: int = Field(foreign_key= "user.id")
    owner: User = Relationship(back_populates="notas") 

#Aqui le stamos diciendo que esta funcion tome esa base, asegurando que los datos cumplan con esa base
class CrearNota(NoteBase):
    #Lo que el usuario envía al crear una nota
    pass

#Aqui al crear usuario verificamos que vengan con los datos de la base y encima verificar que la password_plana tenga
#ese limite y minimo de caracteres
class CrearUsuario(UserBase):
    password_plana: str = Field(max_length=72, min_length=8)
    