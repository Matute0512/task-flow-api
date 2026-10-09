# TaskFlow API

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-e92063.svg)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TaskFlow API** es una solución backend RESTful empresarial y de alto rendimiento diseñada para la gestión organizada de tareas y categorías con autenticación segura basada en tokens JWT. Desarrollada bajo los estándares modernos de **FastAPI**, **SQLAlchemy 2.0**, **Pydantic V2** y orquestación con **Docker**.

---

## Características Principales

- **Autenticación y Autorización Robusta:** Implementación de flujo OAuth2 con tokens Bearer JWT (`python-jose`) y almacenamiento de credenciales con hashing seguro mediante `bcrypt`.
- **Mitigación BOLA (Broken Object Level Authorization):** Aislamiento estricto de recursos por usuario; cada usuario interactúa única y exclusivamente con sus propias entidades.
- **Consultas Modernas con SQLAlchemy 2.0:** Mapeo relacional declarativo tipado con `Mapped` y `mapped_column`, y consultas optimizadas mediante `select()` y `scalars()`.
- **Validación Estricta con Pydantic V2:** Serialización eficiente de esquemas con `ConfigDict(from_attributes=True)` y configuración desacoplada con `SettingsConfigDict`.
- **Integridad Referencial y Preservación de Datos:** Reglas de cascada seguras que garantizan que la eliminación de una categoría preserve las tareas asociadas mediante `ON DELETE SET NULL`.
- **Paginación y Filtrado Estandarizados:** Soporte para paginación uniforme (`skip`, `limit`, `total`) y filtrado avanzado por estado (`is_completed`), prioridad y categoría.
- **Migraciones de Esquema Automatizadas:** Versionado y sincronización continua de base de datos administrado por **Alembic**.
- **Infraestructura Contenerizada Lista para Producción:** Imagen Docker multi-stage optimizada ejecutada bajo usuario sin privilegios de root y orquestación integral con **Docker Compose** y **PostgreSQL**.
- **Documentación Interactiva Integrada:** Especificación OpenAPI 3.1 accesible de forma nativa vía Swagger UI y ReDoc.

---

## Stack Tecnológico

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.10+ | Lenguaje base fuertemente tipado |
| **Framework Web** | FastAPI | Enrutamiento asíncrono y documentación automática |
| **ORM** | SQLAlchemy 2.0 | Persistencia de datos y abstracción relacional |
| **Validación & DTOs** | Pydantic V2 | Validación de datos, serialización y configuración |
| **Migraciones** | Alembic | Control de versiones del esquema de base de datos |
| **Seguridad** | Passlib / Bcrypt & Python-Jose | Hashing criptográfico y gestión de tokens JWT |
| **Bases de Datos** | PostgreSQL 15 / SQLite | Almacenamiento relacional (Prod / Dev) |
| **Contenedores** | Docker & Docker Compose | Empaquetado multi-stage y orquestación local |
| **Testing & Linting** | Pytest & Ruff | Suite de pruebas de integración y análisis de código |

---

## Arquitectura del Proyecto

El proyecto sigue una arquitectura en capas modular y mantenible:

```text
taskflow-api/
├── alembic/                 # Configuración y versiones de migración de base de datos
│   ├── versions/            # Scripts de migración versionados
│   └── env.py               # Configuración del entorno de migraciones
├── app/                     # Código fuente de la aplicación
│   ├── core/                # Configuración global (Settings) y motor de seguridad (JWT/bcrypt)
│   ├── database/            # Inicializador del motor SQLAlchemy y generador de sesiones
│   ├── models/              # Modelos de dominio y tablas (User, Category, Task)
│   ├── schemas/             # Esquemas de validación y DTOs Pydantic V2
│   ├── routers/             # Controladores y endpoints organizados por dominio
│   ├── dependencies.py      # Inyección de dependencias (get_db, get_current_user)
│   └── main.py              # Punto de entrada de la aplicación FastAPI
├── docs/                    # Documentación formal de arquitectura y diagramas
├── tests/                   # Suite de pruebas automatizadas con pytest
├── .env.example             # Plantilla de variables de entorno
├── .dockerignore            # Exclusiones para la construcción de imágenes Docker
├── docker-compose.yml       # Orquestación de servicios (API + PostgreSQL)
├── Dockerfile               # Construcción multi-stage de la imagen de producción
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Dependencias de desarrollo y testing
└── run.py                   # Script de ejecución directa con Uvicorn
```

Para una explicación exhaustiva de los patrones de diseño y diagramas de flujo, consulta [Documento de Arquitectura](docs/architecture.md).

---

## Guía de Instalación y Despliegue

### Opción A: Despliegue Rápido con Docker Compose (Recomendado)

Esta opción aprovisiona automáticamente la base de datos **PostgreSQL 15**, ejecuta las migraciones pendientes de **Alembic** y levanta el servidor **FastAPI**:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Matute0512/task-flow-api.git
   cd task-flow-api
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   ```

3. **Construir y levantar los contenedores:**
   ```bash
   docker compose up --build -d
   ```

4. **Verificar estado de los servicios:**
   ```bash
   docker compose ps
   ```
   La API estará disponible en `http://localhost:8000`.

---

### Opción B: Instalación Local en Entorno Virtual

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Matute0512/task-flow-api.git
   cd task-flow-api
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   # En Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate

   # En Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias de desarrollo y producción:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

4. **Configurar el archivo `.env`:**
   ```bash
   cp .env.example .env
   ```
   *(Por defecto, puedes utilizar SQLite en local configurando `DATABASE_URL=sqlite:///./taskflow.db`)*.

5. **Aplicar las migraciones a la base de datos:**
   ```bash
   alembic upgrade head
   ```

6. **Iniciar el servidor en modo desarrollo:**
   ```bash
   python run.py
   # O directamente con Uvicorn:
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

---

## Documentación Interactiva

Una vez en ejecución, los contratos OpenAPI se encuentran disponibles en:

- **Swagger UI (Interactiva):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc (Documentación Estática):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Principales Endpoints de la API

Todos los endpoints protegidos requieren el encabezado: `Authorization: Bearer <access_token>`.

### Autenticación (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Registra una nueva cuenta de usuario.
- `POST /api/v1/auth/login` — Autentica credenciales y emite el token Bearer JWT.
- `GET /api/v1/auth/me` — Retorna los datos del usuario actualmente autenticado.

### Categorías (`/api/v1/categories`)
- `POST /api/v1/categories` — Crea una categoría vinculada al usuario autenticado.
- `GET /api/v1/categories` — Lista las categorías del usuario con paginación (`skip`, `limit`).
- `GET /api/v1/categories/{id}` — Obtiene el detalle de una categoría propia.
- `PUT /api/v1/categories/{id}` — Actualiza los datos de una categoría.
- `DELETE /api/v1/categories/{id}` — Elimina una categoría (las tareas quedan con `category_id=null`).

### Tareas (`/api/v1/tasks`)
- `POST /api/v1/tasks` — Crea una tarea para el usuario autenticado.
- `GET /api/v1/tasks` — Lista tareas con paginación y filtros opcionales (`is_completed`, `priority`, `category_id`).
- `GET /api/v1/tasks/{id}` — Obtiene el detalle completo de una tarea.
- `PUT /api/v1/tasks/{id}` — Actualiza los campos de una tarea existente.
- `DELETE /api/v1/tasks/{id}` — Elimina permanentemente una tarea propia.

### Sistema
- `GET /` — Mensaje de bienvenida y versión de la API.
- `GET /health` — Endpoint de verificación de salud para Docker / Kubernetes.

---

## Ejecución de Pruebas y Calidad de Código

### Ejecutar Pruebas Automatizadas (Pytest)
El proyecto incluye pruebas de integración end-to-end con cliente HTTP simulado:
```bash
pytest -v
```

### Análisis Estático de Código (Ruff)
```bash
ruff check app/
```

---

## Licencia

Distribuido bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para mayor información.

---

## Autor

**Matías Torres**  
- Correo: [matiastorres678@gmail.com](mailto:matiastorres678@gmail.com)  
- Repositorio: [https://github.com/Matute0512/task-flow-api](https://github.com/Matute0512/task-flow-api)