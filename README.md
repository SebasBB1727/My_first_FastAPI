# Smart Notes API - Powered by Gemini AI

Una API REST moderna, asíncrona y robusta para la gestión de notas inteligentes. Este sistema permite a los usuarios registrarse, autenticarse de forma segura y guardar notas que son procesadas automáticamente por la Inteligencia Artificial de Google Gemini para generar resúmenes instantáneos.

## Características Principales

* **Arquitectura Asíncrona:** Construida con `FastAPI` y `aiosqlite` para soportar alta concurrencia sin bloqueo de I/O.
* **Integración de IA:** Utiliza el SDK asíncrono de `google-genai` (modelo Gemini 2.5 Flash) para análisis y resumen de textos en milisegundos.
* **Seguridad (Auth):** Autenticación mediante tokens JWT (JSON Web Tokens) y contraseñas hasheadas con `passlib` (bcrypt).
* **Base de Datos:** ORM implementado con `SQLModel` y base de datos SQLite.
* **Control de Accesos:** Rutas protegidas basadas en roles (Usuarios Estándar y Administradores).
* **Scripts de Mantenimiento:** Herramientas CLI nativas para la creación segura de administradores de sistema.
* **Frontend Incluido:** Cliente ligero en Vanilla JS y HTML (PicoCSS) para consumir la API de forma visual.

## Tecnologías Utilizadas

* **Backend:** Python 3.11+, FastAPI, SQLModel, SQLAlchemy Async, Pydantic.
* **Inteligencia Artificial:** Google Gemini API (`google-genai`).
* **Seguridad:** JWT, Passlib, Bcrypt.
* **Frontend:** HTML5, Vanilla JavaScript, Fetch API, PicoCSS.

## Instalación y Uso Local

### 1. Clonar el repositorio

```bash
git clone [https://github.com/SebasBB1727/My_first_FastAPI.git](https://github.com/SebasBB1727/My_first_FastAPI.git)
cd My_first_FastAPI
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
# Activar en Windows:
.venv\Scripts\activate
# Activar en Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto y agrega tus credenciales:

```env
SECRET_KEY="tu_super_secreto_generado_con_openssl"
ALGORITHM="HS256"
GEMINI_API_KEY="tu_api_key_de_google_ai_studio"
```

### 4. Inicializar la Base de Datos (Admin)

Antes de iniciar el servidor, crea a tu usuario Administrador ejecutando el script de consola:

```bash
python create_admin.py
```

### 5. Correr el servidor

Inicia la API con recarga automática para desarrollo:

```bash
uvicorn main:app --reload
```

* La documentación interactiva (Swagger) estará disponible en: `http://localhost:8000/docs`
* Para ver la interfaz gráfica, simplemente abre el archivo `index.html` en tu navegador de preferencia.

## Endpoints Principales

* `POST /registro/` - Creación de nuevos usuarios.
* `POST /login/` - Generación de token JWT.
* `POST /notes/` - Creación de notas con resumen IA generado automáticamente (Requiere Auth).
* `GET /notes/` - Obtener notas del usuario actual (Requiere Auth).
* `GET /notes/all` - Obtener notas de todos los usuarios (Exclusivo Administradores).
* `DELETE /notes/all` - Borrado masivo (Exclusivo Administradores).