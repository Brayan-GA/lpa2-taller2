# Imagen base oficial de Python
FROM python:3.12-slim

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements primero (mejor cache de Docker)
COPY ./app/requirements.txt .

# Instalar dependencias (la caché de pip se conserva entre builds,
# así un build fallido no obliga a volver a descargar todo)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=120 --retries 10 -r requirements.txt

# Copiar el resto de la aplicación
COPY ./app .

# Exponer puerto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

