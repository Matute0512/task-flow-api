# Documento de Arquitectura de Software — TaskFlow API

**Versión:** 1.0.0  
**Estado:** Activo  
**Stack Principal:** Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic V2, PostgreSQL / SQLite, Docker  

---

## 1. Visión General y Principios de Diseño

**TaskFlow API** es un servicio backend RESTful de alto rendimiento diseñado para la gestión integral de tareas, categorías y usuarios bajo un modelo de aislamiento estricto por propietario (*multi-tenancy lógico a nivel de usuario*).

### Principios Rectores:
1. **Arquitectura en Capas (Layered Architecture):** Separación rigurosa entre transporte HTTP, validación de esquemas, lógica de negocio y persistencia de datos.
2. **Tipado Estricto y Validación en los Límites (Type Safety & Boundary Validation):** Empleo de **Pydantic V2** para contratos de entrada/salida y **SQLAlchemy 2.0** (`Mapped`, `mapped_column`) para garantizar consistencia estática y en tiempo de ejecución.
3. **Seguridad Integral (Defense in Depth & BOLA Mitigation):** Protección de recursos mediante tokens **JWT (JSON Web Tokens)** y hashing criptográfico **bcrypt**, asegurando que ningún usuario pueda acceder, modificar o eliminar recursos de terceros (*Broken Object Level Authorization*).
4. **Resiliencia y Portabilidad Contenerizada:** Diseño desacoplado operable tanto en desarrollo local (SQLite) como en entornos productivos contenerizados (PostgreSQL con Docker y Compose).

---

## 2. Arquitectura del Sistema

El sistema implementa una arquitectura por capas desacoplada. El flujo de información atraviesa barreras de responsabilidad claramente definidas:

```mermaid
flowchart TD
    subgraph Cliente
        C[Cliente Web / Móvil / Swagger UI]
    end

    subgraph Capa_Transporte ["Capa de Transporte y Enrutamiento (FastAPI)"]
        R_AUTH["Router: Auth (/api/v1/auth)"]
        R_CAT["Router: Categories (/api/v1/categories)"]
        R_TASK["Router: Tasks (/api/v1/tasks)"]
    end

    subgraph Capa_Seguridad ["Capa de Dependencias y Seguridad"]
        DEP_AUTH["get_current_user (OAuth2 Bearer JWT)"]
        DEP_DB["get_db (Session Generator con Auto-Rollback)"]
    end

    subgraph Capa_Validacion ["Capa de Esquemas y DTOs (Pydantic V2)"]
        S_USER[UserCreate / UserResponse]
        S_CAT[CategoryCreate / CategoryResponse]
        S_TASK[TaskCreate / TaskResponse]
        S_PAG[PaginatedResponse / PaginationParams]
    end

    subgraph Capa_Persistencia ["Capa de Dominio y Persistencia (SQLAlchemy 2.0)"]
        M_USER[(Modelo: User)]
        M_CAT[(Modelo: Category)]
        M_TASK[(Modelo: Task)]
        ALEMBIC["Motor de Migraciones (Alembic)"]
    end

    subgraph Almacenamiento ["Base de Datos"]
        DB[(PostgreSQL / SQLite)]
    end

    C -->|HTTP / JSON + Bearer Token| Capa_Transporte
    Capa_Transporte --> Capa_Seguridad
    Capa_Transporte --> Capa_Validacion
    Capa_Seguridad --> Capa_Persistencia
    Capa_Persistencia --> ALEMBIC
    Capa_Persistencia --> Almacenamiento
```

---

## 3. Modelo de Dominio y Entidad-Relación (ER)

El modelo de datos garantiza integridad referencial y aislamiento de la información.

```mermaid
erDiagram
    USER ||--o{ CATEGORY : "posee (1:N)"
    USER ||--o{ TASK : "posee (1:N)"
    CATEGORY ||--o{ TASK : "clasifica (0..1:N)"

    USER {
        int id PK "Identificador único autoincremental"
        string email UK "Correo electrónico corporativo / único"
        string username UK "Nombre de usuario único (indexado)"
        string hashed_password "Hash bcrypt seguro de la contraseña"
        boolean is_active "Estado de activación de la cuenta"
        boolean is_superuser "Privilegios administrativos"
        datetime created_at "Marca de tiempo de registro"
        datetime updated_at "Marca de tiempo de última actualización"
    }

    CATEGORY {
        int id PK "Identificador único de categoría"
        string name "Nombre de la categoría (máx 100)"
        string description "Detalle descriptivo opcional"
        string color "Código hexadecimal (#RRGGBB)"
        int owner_id FK "users.id (ON DELETE CASCADE)"
        datetime created_at "Marca de tiempo de creación"
    }

    TASK {
        int id PK "Identificador único de la tarea"
        string title "Título descriptivo de la tarea"
        string description "Cuerpo detallado de la tarea"
        boolean is_completed "Estado de ejecución"
        string priority "Prioridad: low | medium | high"
        datetime due_date "Fecha límite de finalización"
        int owner_id FK "users.id (ON DELETE CASCADE)"
        int category_id FK "categories.id (ON DELETE SET NULL)"
        datetime created_at "Marca de tiempo de creación"
        datetime updated_at "Marca de tiempo de última modificación"
    }
```

### Reglas de Integridad y Cascada:
- **`CATEGORY -> TASK (ON DELETE SET NULL)`:** La eliminación de una categoría no provoca la pérdida de tareas asociadas. La clave foránea `category_id` se actualiza automáticamente a `NULL`, preservando el histórico y contenido del usuario.
- **`USER -> CATEGORY / TASK (ON DELETE CASCADE)`:** La supresión de una cuenta de usuario elimina automáticamente en cascada todos sus recursos dependientes (categorías y tareas), evitando registros huérfanos en el almacenamiento.

---

## 4. Ciclo de Vida y Flujo de Autenticación (Diagrama de Secuencia)

El acceso a los recursos de la API requiere el flujo estándar de autenticación OAuth2 con tokens JWT portadores (*Bearer Tokens*).

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente (SPA / Mobile / Postman)
    participant Gateway as FastAPI Router
    participant Dep as Inyector de Dependencias
    participant Sec as Security Engine (bcrypt / JWT)
    participant DB as Motor de Base de Datos

    %% Registro
    rect rgb(240, 248, 255)
    note over Cliente, DB: Flujo 1: Registro de Nuevo Usuario
    Cliente->>Gateway: POST /api/v1/auth/register { email, username, password }
    Gateway->>DB: select(User).where(email == email OR username == username)
    DB-->>Gateway: None (Usuario no existente)
    Gateway->>Sec: get_password_hash(password)
    Sec-->>Gateway: Hash bcrypt generado
    Gateway->>DB: INSERT INTO users VALUES (...)
    DB-->>Gateway: Usuario persistido
    Gateway-->>Cliente: 201 Created { UserResponse }
    end

    %% Login
    rect rgb(245, 255, 250)
    note over Cliente, DB: Flujo 2: Autenticación y Emisión de Token JWT
    Cliente->>Gateway: POST /api/v1/auth/login (OAuth2 Password Request Form)
    Gateway->>DB: select(User).where(username == username)
    DB-->>Gateway: Registro User
    Gateway->>Sec: verify_password(plain_password, hashed_password)
    Sec-->>Gateway: True (Credenciales válidas)
    Gateway->>Sec: create_access_token(subject=user.id, expires_delta=30m)
    Sec-->>Gateway: Token JWT firmado (HS256)
    Gateway-->>Cliente: 200 OK { access_token, token_type: "bearer" }
    end

    %% Petición Protegida
    rect rgb(255, 250, 245)
    note over Cliente, DB: Flujo 3: Ejecución de Petición Protegida (Tasks)
    Cliente->>Gateway: GET /api/v1/tasks?skip=0&limit=10 (Header: Authorization: Bearer <token>)
    Gateway->>Dep: Resolver get_current_user(token)
    Dep->>Sec: jwt.decode(token, SECRET_KEY, ALGORITHM)
    Sec-->>Dep: Payload { sub: user_id, exp: ... }
    Dep->>DB: select(User).where(id == user_id)
    DB-->>Dep: Instancia User activo
    Dep-->>Gateway: Inyección de current_user
    Gateway->>DB: select(Task).where(Task.owner_id == current_user.id)
    DB-->>Gateway: Lista de tareas del usuario autenticado
    Gateway-->>Cliente: 200 OK { PaginatedResponse[TaskResponse] }
    end
```

---

## 5. Matriz de Control de Acceso (RBAC / Propiedad)

| Recurso | Endpoint | Método | Autenticación Requerida | Regla de Autorización / Scope |
| :--- | :--- | :---: | :---: | :--- |
| **Salud del Sistema** | `/health` | `GET` | No | Acceso público para balanceadores / Kubernetes |
| **Información Raíz** | `/` | `GET` | No | Acceso público con metadatos de la API |
| **Registro de Usuario** | `/api/v1/auth/register` | `POST` | No | Acceso público con validación de unicidad |
| **Login de Usuario** | `/api/v1/auth/login` | `POST` | No | Retorna token Bearer si las credenciales son válidas |
| **Perfil Propio** | `/api/v1/auth/me` | `GET` | Sí | Retorna exclusivamente el perfil del usuario firmante |
| **Categorías** | `/api/v1/categories` | `GET`, `POST` | Sí | Solo lista o crea categorías donde `owner_id == current_user.id` |
| **Categoría Específica** | `/api/v1/categories/{id}` | `GET`, `PUT`, `DELETE` | Sí | Restringido exclusivamente al usuario propietario |
| **Tareas** | `/api/v1/tasks` | `GET`, `POST` | Sí | Solo lista o crea tareas donde `owner_id == current_user.id` |
| **Tarea Específica** | `/api/v1/tasks/{id}` | `GET`, `PUT`, `DELETE` | Sí | Restringido exclusivamente al usuario propietario |

---

## 6. Arquitectura de Despliegue e Infraestructura Contenerizada

La arquitectura de infraestructura está basada en contenedores Docker mediante una topología desacoplada de dos niveles (*Two-Tier Architecture*):

```mermaid
flowchart LR
    subgraph Host ["Entorno Host / Servidor"]
        subgraph DockerBridge ["Red Bridge Privada (taskflow_network)"]
            subgraph ContenedorAPI ["taskflow_api (FastAPI / Uvicorn)"]
                APP["FastAPI Application"]
                ALEMBIC_CLI["Alembic Migrations Runner"]
                HEALTH_API["Healthcheck Probe"]
            end

            subgraph ContenedorDB ["taskflow_db (PostgreSQL 15 Alpine)"]
                PG_ENGINE["PostgreSQL Engine"]
                PG_HEALTH["pg_isready Probe"]
            end
        end

        VOL[("Volumen Persistente: postgres_data")]
    end

    CLIENTES[Clientes HTTP] -->|Puerto 8000:8000| APP
    APP -->|Conexión Segura Puerto 5432| PG_ENGINE
    PG_ENGINE --- VOL
    ALEMBIC_CLI -->|Upgrade Head al inicio| PG_ENGINE
```

### Características de la Infraestructura:
1. **Multi-Stage Build:** `Dockerfile` utiliza una etapa `builder` con herramientas de compilación para instalar dependencias y una etapa final `production` minimalista basada en `python:3.10-slim`.
2. **Principio de Menor Privilegio:** La aplicación se ejecuta dentro del contenedor bajo el usuario de sistema `appuser` (no-root).
3. **Sincronización Determinista del Arranque:** El contenedor `api` declara una dependencia estricta `depends_on: { db: { condition: service_healthy } }`. La aplicación no inicia hasta que PostgreSQL supera el test `pg_isready`.
4. **Migraciones Continuas:** Al iniciar el contenedor `api`, se ejecutan automáticamente las migraciones pendientes con `alembic upgrade head` antes del arranque del servidor Uvicorn.
