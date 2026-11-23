# SIMUL — Backend (FastAPI + SQLAlchemy + MySQL)

Documentación del **tercer corte**: la API REST del Museo Digital Interactivo.

> Este documento describe el estado **actual** del backend. La visión general
> del proyecto y la trazabilidad de los tres cortes están en
> [`ARQUITECTURA.md`](ARQUITECTURA.md).

---

## 1. Tecnologías

- **Python 3.12** + **FastAPI** (ASGI) + **Uvicorn**
- **SQLAlchemy 2.0** (ORM, estilo declarativo moderno)
- **MySQL 8.4** (driver PyMySQL)
- **Pydantic v2** (validación de entrada y serialización de salida)
- **PyJWT** (autenticación)
- **Docker / Docker Compose**
- **Pytest** + `TestClient` (pruebas)

Documentación interactiva: **`/docs`** (Swagger UI) y **`/redoc`**.

---

## 2. Arquitectura por capas

```
┌────────────┐   ┌───────────────┐   ┌───────────┐   ┌───────────────┐   ┌─────────┐
│  routes    │ → │  controllers  │ → │  services │ → │ repositories  │ → │  models │
│ (HTTP/API) │   │ (orquestación)│   │ (negocio) │   │ (consultas BD)│   │  (ORM)  │
└────────────┘   └───────────────┘   └───────────┘   └───────────────┘   └─────────┘
```

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Routes** | `app/routes/` | Define los `APIRouter`, los verbos HTTP, los esquemas de entrada y las dependencias de seguridad. No tiene lógica de negocio. |
| **Controllers** | `app/controllers/` | Recibe la petición, resuelve el usuario autenticado y llama al service. Devuelve la respuesta con el sobre estándar. |
| **Services** | `app/services/` | Reglas de negocio: puntos, niveles, insignias, validación, permisos finos, transacciones. |
| **Repositories** | `app/repositories/` | Única capa que consulta la base de datos (SQLAlchemy). |
| **Models** | `app/models/` | Las 25 tablas del modelo E-R como clases ORM. |
| **Schemas** | `app/schemas/` | Modelos Pydantic de entrada (validación) y salida (serialización). |

### Fábrica de aplicación

`app/__init__.py → create_app()` construye la app e instala:

1. **Middleware de sesión**: abre una sesión SQLAlchemy por petición, hace
   `commit` si la respuesta es `< 400` y `rollback` si no, y siempre cierra la
   sesión. La sesión se guarda en un `ContextVar` (accesible vía `db.session`).
2. **Manejadores de error** con el sobre uniforme:
   - `HTTPException` → `{success, message}`
   - `RequestValidationError` → `{success, message, details}` (422)
   - `Exception` → 500 genérico (sin filtrar detalles internos)
3. **Estáticos** (`/static`) y **routers** (vistas HTML + API `/api/museo/*`).

---

## 3. Capa de datos

`app/extensions.py` expone una fachada `db` con la ergonomía declarativa de
SQLAlchemy (`db.Model`, `db.Column`, `db.relationship`, `db.session`) sobre la
base declarativa y la sesión por petición.

- **Sesión por petición**: la instala el middleware.
- **Sesión fuera de petición**: `with sesion_bd():` (usada por `db/seed.py` y
  las pruebas).
- **Tipos portables**: `YearType` mapea a `YEAR` en MySQL y a `SMALLINT` en
  SQLite (para el arranque local sin MySQL).

### Correspondencia con el diseño E-R

`db/DDL.sql` implementa el diagrama entidad-relación
([`diagrama-ER.jpeg`](diagrama-ER.jpeg)): **25 tablas + 2 vistas**, con claves
foráneas, `ENUM` y `YEAR` tal como aparecen en el diagrama. Los modelos ORM
replican esas mismas tablas, columnas, relaciones e índices.

Vistas del diseño:

- `v_bandeja_validacion` — contenido pendiente con autor e imagen.
- `v_ranking` — ranking de usuarios por puntos y nivel.

---

## 4. Autenticación y seguridad

- **Hash de contraseñas**: `app/utils/security.py` usa
  `PBKDF2-HMAC-SHA256` con sal aleatoria de 16 bytes y 260 000 iteraciones
  (solo biblioteca estándar). Comparación en tiempo constante
  (`hmac.compare_digest`). El `password_hash` nunca se serializa.
- **JWT**: `app/utils/roles.py` firma tokens HS256 con `sub = id_usuario`,
  `type = access` y expiración configurable.
- **Dependencias**: `requiere_usuario` (exige token válido de usuario activo) y
  `usuario_opcional` (rutas públicas con sesión opcional).
- **Roles**: `estudiante`, `docente`, `admin`, `egresado`. Las operaciones
  sensibles (bandeja de validación, aprobar/rechazar, gestión de usuarios,
  KPIs, eliminar contenido) verifican `rol_nombre == "admin"`.
- **Códigos HTTP**: `200/201` éxito · `401` sin autenticar · `403` sin permisos
  · `404` no encontrado · `409` conflicto (p. ej. correo duplicado) · `422`
  validación de campos.

---

## 5. Endpoints

Toda la API cuelga de `/api/museo`. Resumen por módulo:

| Módulo | Prefijo | Operaciones |
|---|---|---|
| Autenticación | `/api/museo/auth` | `register`, `login`, `me` |
| Contenido | `/api/museo/contenido` | listar, crear, detalle, `PUT`, `PATCH`, `DELETE`, mis-aportes, favoritos, evidencias, comentarios, reacciones |
| Validación | `/api/museo/validacion` | bandeja, aprobar, rechazar, historial |
| Gamificación | `/api/museo/gamificacion` | ranking, niveles, insignias, historial |
| Administración | `/api/museo/admin` | usuarios (listar/actualizar), KPIs |
| Museo | `/api/museo` | home, timeline, hall, categorías, años, notificaciones |

La tabla completa de métodos, rutas y permisos está en el
[`README.md`](../README.md#api-rest) y en Swagger (`/docs`).

---

## 6. Ejecución

### Docker (recomendado)

```bash
docker compose up --build
docker compose exec app python db/seed.py   # datos de demostración
```

- API + Swagger: http://localhost:5000/docs
- MySQL: `localhost:3307` (usuario `simul_user`)

### Local

```bash
pip install -r requirements.txt
uvicorn run:app --reload
```

Sin `DATABASE_URL` la app usa SQLite (`simul_local.db`). Si copiaste
`.env.example` a `.env`, la app lo carga automáticamente.

---

## 7. Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

`tests/conftest.py` fija `DATABASE_URL` a SQLite temporal antes de importar la
app y siembra los catálogos. `tests/test_app.py` cubre:

- documentación OpenAPI y vistas HTML,
- registro/login/perfil y validaciones de campos,
- CRUD de contenido y control de permisos,
- flujo de validación (aprobar/rechazar con motivo obligatorio),
- gamificación (puntos al publicar) y funciones sociales,
- restricciones de rol (401/403).

---

## 8. Estructura de archivos

```
app/
├── __init__.py            # create_app()
├── config.py              # Config
├── extensions.py          # Base, engine, sesión, fachada db
├── models/                # 25 tablas (SQLAlchemy)
├── schemas/               # Pydantic (entrada/salida)
├── repositories/          # acceso a datos
├── services/              # reglas de negocio
├── controllers/           # orquestación
├── routes/                # APIRouters
├── utils/
│   ├── security.py        # hash de contraseñas
│   ├── roles.py           # JWT + dependencias de auth
│   ├── response.py        # sobre {success, message, data}
│   └── templados.py       # url_for y render de plantillas
├── data/                  # catálogos iniciales para las plantillas (corte 2)
├── templates/             # 21 vistas Jinja2
└── static/                # CSS/JS/imágenes; js/api.js es el cliente de /api/museo
db/
├── DDL.sql                # 25 tablas + 2 vistas (MySQL)
└── seed.py                # datos de demostración
tests/
├── conftest.py
└── test_app.py
```
