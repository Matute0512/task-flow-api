# ========================================================
# ETAPA 1: Builder (Compilación e instalación de dependencias)
# ========================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Variables de entorno para optimización de compilación
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar manifiesto de dependencias de producción
COPY requirements.txt ./

# Actualizar pip e instalar dependencias en el sistema de la etapa builder
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================================================
# ETAPA 2: Producción (Imagen final mínima y segura)
# ========================================================
FROM python:3.10-slim AS production

WORKDIR /app

# Variables de entorno de ejecución para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Crear usuario y grupo de sistema sin privilegios de root (Principio de menor privilegio)
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser

# Copiar dependencias empaquetadas desde la etapa builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar el código fuente del proyecto y asignar propiedad al usuario no-root
COPY --chown=appuser:appgroup . .

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto del servicio
EXPOSE 8000

# Verificación de salud integrada a nivel de contenedor Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Comando por defecto para iniciar el servidor de producción con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]