# SIMUL — Museo Digital Interactivo

Backend **FastAPI + SQLAlchemy + MySQL** del Museo Digital Interactivo del
programa de Ingeniería de Sistemas de la Universidad Libre.

Este repositorio corresponde al **tercer corte**: el frontend del segundo corte
(21 páginas HTML con Jinja2) se conserva y sobre él se construyó la **API REST
completa**, con arquitectura por capas, base de datos MySQL que implementa el
modelo entidad-relación del proyecto y pruebas automatizadas.

---

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework web | **FastAPI** (ASGI, OpenAPI/Swagger automático) |
| Servidor | Uvicorn |
| ORM | **SQLAlchemy 2.0** |
| Base de datos | **MySQL 8.4** |
| Validación | Pydantic v2 |
| Autenticación | JWT (PyJWT) |
| Contenedores | **Docker** + Docker Compose |
| Plantillas | Jinja2 (vistas del museo) |
| Pruebas | Pytest + TestClient |

---

## Arranque rápido (Docker)

Requisito: Docker Desktop en marcha.

```bash
docker compose up --build
```

Esto levanta dos servicios:

- **`simul_db`** → MySQL 8.4 en `localhost:3307`. La primera vez ejecuta
  `db/DDL.sql`, que crea las **25 tablas y 2 vistas** del diseño E-R.
- **`simul_app`** → la API en `http://localhost:5000`.

Una vez arriba:

| Recurso | URL |
|---|---|
| Swagger UI (probar la API) | http://localhost:5000/docs |
| ReDoc | http://localhost:5000/redoc |
| OpenAPI JSON | http://localhost:5000/openapi.json |
| Museo (vistas HTML) | http://localhost:5000/ |

### Cargar los datos de demostración

```bash
# Desde la raíz del proyecto, con los contenedores arriba:
docker compose exec app python db/seed.py
```

El seed puebla las tablas con el contenido del museo (roles, niveles,
insignias, usuarios, contenido con sus subtipos, comentarios, reacciones,
puntos…). Todos los usuarios de demostración usan la contraseña **`1234`**.

> ¿Ya tenías datos de una versión anterior? Reinicia el volumen para que el
> DDL se ejecute de nuevo: `docker compose down -v && docker compose up --build`.

---

## Arranque local (sin Docker)

Sirve para desarrollar la API con recarga automática. Si no defines
`DATABASE_URL`, la app usa **SQLite** (`instance/simul.db`) como respaldo.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
uvicorn run:app --reload        # http://localhost:5000/docs
```

Para conectar a MySQL, copia `.env.example` a `.env` y ajusta `DATABASE_URL`
(ver la sección [Variables de entorno](#variables-de-entorno)).

---

## Arquitectura por capas

El backend sigue una separación estricta de responsabilidades; cada petición
atraviesa las capas en este orden:

```
 routes  →  controllers  →  services  →  repositories  →  models
 (HTTP)     (orquestan)     (negocio)     (consultan BD)   (ORM)
```

```
app/
├── __init__.py        # fábrica create_app(): middlewares, errores, routers
├── config.py          # Config (DATABASE_URL, JWT_*)
├── extensions.py      # Base, engine, sesión por petición, fachada `db`
├── models/            # 25 tablas del modelo E-R (SQLAlchemy)
├── schemas/           # validación/serialización (Pydantic)
├── repositories/      # única capa que consulta la base de datos
├── services/          # reglas de negocio (puntos, validación, permisos)
├── controllers/       # reciben la petición y llaman a los services
├── routes/            # APIRouters: rutas REST + vistas HTML
├── utils/             # JWT/roles, respuesta estándar, hashing, url_for
├── data/              # datos mock del frontend (segundo corte)
├── templates/         # 21 vistas Jinja2 del museo
└── static/            # CSS, JS e imágenes

db/
├── DDL.sql            # script MySQL: 25 tablas + 2 vistas (diseño E-R)
└── seed.py            # datos de demostración

tests/                 # pruebas de la API (pytest)
docs/                  # documentación técnica
```

Detalle completo en [`docs/BACKEND.md`](docs/BACKEND.md).

---

## API REST

Toda la API vive bajo el prefijo **`/api/museo`** y se documenta
automáticamente en **`/docs`**. Respuestas con sobre uniforme:

```json
{ "success": true,  "message": "OK",            "data": { } }
{ "success": false, "message": "Datos inválidos", "details": { } }
```

### Autenticación — `/api/museo/auth`

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/register` | Registro (rol `estudiante` o `docente`) |
| POST | `/login` | Inicio de sesión → access token JWT |
| GET | `/me` | Usuario del token vigente 🔒 |

### Contenido — `/api/museo/contenido`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Listar contenido publicado (filtros `q`, `categoria`, `tipo`, `anio`, paginación) |
| POST | `/` | Registrar contenido (nace *pendiente*) 🔒 |
| GET | `/{id}` | Detalle de un contenido |
| PUT | `/{id}` | Actualizar (autor o admin) 🔒 |
| PATCH | `/{id}` | Actualización parcial 🔒 |
| DELETE | `/{id}` | Eliminar (solo admin) 🔒 |
| GET | `/mis-aportes` | Contenido del usuario autenticado 🔒 |
| GET | `/favoritos` | Favoritos del usuario 🔒 |
| POST | `/{id}/evidencias` | Adjuntar evidencia (foto/video/doc) 🔒 |
| GET/POST | `/{id}/comentarios` | Comentarios del contenido |
| POST | `/{id}/reaccion` | Reaccionar (like…) 🔒 |
| POST | `/{id}/favorito` | Marcar/desmarcar favorito 🔒 |

### Validación — `/api/museo/validacion`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/bandeja` | Contenido pendiente (solo admin) 🔒 |
| POST | `/{id}/aprobar` | Publicar (+100 puntos al autor) 🔒 |
| POST | `/{id}/rechazar` | Rechazar — **motivo obligatorio** 🔒 |
| GET | `/{id}/historial` | Trazabilidad de decisiones (solo admin) 🔒 |

### Gamificación — `/api/museo/gamificacion`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/ranking` | Ranking por puntos |
| GET | `/niveles` | Catálogo de niveles |
| GET | `/insignias` | Catálogo de insignias |
| GET | `/mi-historial` | Historial de puntos propio 🔒 |
| GET | `/historial/{usuario_id}` | Historial (propio o admin) 🔒 |

### Administración — `/api/museo/admin`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/usuarios` | Listar/filtrar usuarios (solo admin) 🔒 |
| PUT/PATCH | `/usuarios/{id}` | Cambiar estado/rol/nombre (solo admin) 🔒 |
| GET | `/kpis` | Indicadores del panel (solo admin) 🔒 |

### Vistas transversales — `/api/museo`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/home`, `/timeline`, `/hall`, `/categorias`, `/anios` | Datos del museo |
| GET | `/notificaciones` | Notificaciones del usuario 🔒 |
| POST | `/notificaciones/{id}/leer` | Marcar como leída 🔒 |

> 🔒 = requiere cabecera `Authorization: Bearer <token>`.

---

## Seguridad y roles

- **Contraseñas** con hash `PBKDF2-HMAC-SHA256` (sal aleatoria, 260 000
  iteraciones) — nunca se guardan ni se devuelven en texto plano.
- **JWT** (HS256) con expiración configurable; el botón *Authorize* de Swagger
  permite probar los endpoints protegidos.
- **Roles**: `estudiante`, `docente`, `admin`, `egresado`. La validación de
  contenido y la administración de usuarios son **exclusivas del admin**.
- **Códigos HTTP** coherentes: `200/201` éxito, `401` sin autenticar, `403` sin
  permisos, `404` no encontrado, `409` conflicto, `422` validación.

---

## Base de datos

- `db/DDL.sql` es la implementación del **diseño entidad-relación** (el diagrama
  está en [`docs/diagrama-ER.jpeg`](docs/diagrama-ER.jpeg)):
  **25 tablas + 2 vistas** (`v_bandeja_validacion`, `v_ranking`), con claves
  foráneas, índices y tipos `ENUM`/`YEAR`.
- `db/seed.py` carga datos de demostración reales del museo.
- En Docker, el DDL se ejecuta automáticamente la primera vez (init script);
  la app además crea las tablas que falten al arrancar (`create_all`).

---

## Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | `sqlite:///instance/simul.db` | Cadena de conexión (en Docker: MySQL) |
| `JWT_SECRET_KEY` | `simul-development-secret-key-change-me` | Clave para firmar JWT (**cámbiala en producción**) |
| `JWT_ACCESS_TOKEN_EXPIRES` | `3600` | Duración del token (segundos) |

---

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

Las pruebas usan SQLite temporal (no tocan MySQL) y cubren documentación
OpenAPI, autenticación, CRUD de contenido, validaciones, roles y el flujo de
validación con gamificación. Evidencia manual de la API: **Swagger**
(`/docs`) y la colección **Postman** en
[`docs/postman/SIMUL.postman_collection.json`](docs/postman/SIMUL.postman_collection.json).

---

## Documentación

- [`docs/BACKEND.md`](docs/BACKEND.md) — arquitectura del backend, capas y API.
- [`docs/guias/GUION_VIDEO_TERCER_CORTE.md`](docs/guias/GUION_VIDEO_TERCER_CORTE.md)
  — guiones de los 3 integrantes para el video (recorrido botón → MySQL).
- [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) — análisis general (nota: sus
  secciones sobre el backend describen el estado previo a FastAPI).
- [`docs/FRONTEND.md`](docs/FRONTEND.md), [`docs/PAGINAS.md`](docs/PAGINAS.md),
  [`docs/ESTILOS.md`](docs/ESTILOS.md), [`docs/DATOS.md`](docs/DATOS.md).

---

## Coherencia entre cortes

1. **Corte 1 (requerimientos y diseño).** Los requisitos `RF-*`/`RNF-*` y el
   diagrama E-R ([`docs/diagrama-ER.jpeg`](docs/diagrama-ER.jpeg)) se documentan
   en `docs/` y se implementan en el código.
2. **Corte 2 (frontend).** Las 21 páginas Jinja2 y los datos del museo viven en
   `app/templates`, `app/static` y `app/data/simul_data.py`.
3. **Corte 3 (backend).** La API REST implementa ese mismo dominio sobre MySQL,
   con el modelo de datos del diseño y los datos del museo como semilla.
