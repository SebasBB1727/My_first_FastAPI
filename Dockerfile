# 1. EL INGREDIENTE BASE (El Sistema Operativo)
# Usamos una versión oficial de Python optimizada y ligera ("slim")
FROM python:3.11-slim

# 2. LA MESA DE TRABAJO
# Le decimos a Docker que todo lo que hagamos a partir de aquí será dentro de la carpeta /app
WORKDIR /app

# 3. EL TRUCO DEL CACHÉ (Optimización nivel Senior)
# Primero copiamos SOLO el archivo de requerimientos.
COPY requirements.txt .

# 4. INSTALAR DEPENDENCIAS
# Instalamos las librerías. --no-cache-dir evita guardar basura de la instalación para que la caja pese menos.
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPIAR EL RESTO DEL CÓDIGO
# Copiamos todo lo que hay en nuestra carpeta (excepto lo del .dockerignore) hacia la carpeta /app del contenedor.
COPY . .

# 6. EL PUERTO DE SALIDA
# Le avisamos a quien use el contenedor que nuestra API vive en el puerto 8000
EXPOSE 8000

# 7. LA ORDEN DE ARRANQUE
# Esto es lo que ejecuta el contenedor cuando lo encienden. 
# IMPORTANTE: Usamos --host 0.0.0.0 para que el servidor acepte conexiones desde afuera de la caja.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]