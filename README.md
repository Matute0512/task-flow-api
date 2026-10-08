# TaskFlow API

API profesional para gestión de tareas con categorías y autenticación JWT, contruida con FastAPI.

## Características

- Autenticación y autorización con JWT.
- CRUD completo de usuarios, categorías y tareas.
- Documentación interactiva con OpenAPI/Swagger.
- Validación de datos con Pydantic V2.
- Base de datos con SQLAlchemy 2.0 y migraciones con Alembic.
- Estructura modular y escalable.

## Stack Tecnológico

- **Python:** 3.10+
- **Framework:** FastAPI
- **Base de Datos:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.0
- **Migraciones:** Alembic
- **Autenticación:** JWT con python-jose
- **Validación:** Pydantic V2

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Matute0512/task-flow-api.git
cd taskflow-api
```

### 2. Crear entorno virtual

```bash
py 3.10 -m venv venv
source venv/bin/activate # Linux/macOS
.\venv\Scripts\Activate.ps1 # Windows PowerShell
```

### 3. Instalar dependencias

```bash
pip install -r requirements-dev.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores
```

### 5. Ejecutar migraciones (próximamente)

```bash
alembic upgrade head
```

### 6. Iniciar el servidor

```bash
python run.py
```

## Documentación

Una vez iniciado el servidor, accede a:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Estructura del proyecto

```text
taskflow-api/
├── app/                    # Código de la aplicación
│   ├── core/              # Configuración y seguridad
│   ├── database/          # Conexión a BD
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Schemas Pydantic
│   ├── routers/           # Endpoints
│   └── main.py            # Punto de entrada
├── alembic/               # Migraciones
├── tests/                 # Tests
└── requirements.txt       # Dependencias
```

## Endpoints Principales

- ``POST /auth/register`` - Registrar usuario
- ``POST /auth/login`` - Login y obtener token JWT
- ``GET /tasks/`` - Listar tareas (requiere auth)
- ``POST /tasks/`` - Crear tarea (requiere auth)
- ``GET /categories/`` - Listar categorías

## Licencia

MIT

## Autor

Matías Torres - matiastorres@gmail.com