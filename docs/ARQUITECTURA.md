# SIMUL — Arquitectura y trazabilidad

**Museo Digital Interactivo** · Facultad de Ingeniería de Sistemas · Universidad Libre

Este documento describe el estado **actual** del proyecto después del tercer
corte: una API REST FastAPI sobre MySQL que convive con las vistas HTML del
segundo corte. La documentación detallada del backend está en
[`BACKEND.md`](BACKEND.md) y los guiones de entrega en
[`guias/README.md`](guias/README.md).

---

## 1. Stack actual

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework web | FastAPI (ASGI, Swagger/OpenAPI automático) |
| Servidor | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Base de datos | MySQL 8.4 (driver PyMySQL) |
| Validación | Pydantic v2 |
| Autenticación | JWT (PyJWT) + PBKDF2 de la biblioteca estándar |
| Plantillas | Jinja2 (vistas HTML del corte 2) |
| Pruebas | Pytest + `TestClient` |
| Contenedores | Docker + Docker Compose |

---

## 2. Arquitectura por capas

Cada petición de la API atraviesa las mismas capas, en un solo sentido:

```
routes  →  controllers  →  services  →  repositories  →  models
 HTTP      orquestación     negocio      consultas BD      ORM
```

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Routes | `app/routes/` | `APIRouter`, verbos HTTP, esquemas Pydantic y dependencias de seguridad. |
| Controllers | `app/controllers/` | Resuelven el usuario y delegan en el service; devuelven el sobre estándar. |
| Services | `app/services/` | Puntos, niveles, insignias, validación, permisos y reglas de negocio. |
| Repositories | `app/repositories/` | Única capa que consulta la base de datos. |
| Models | `app/models/` | Clases ORM que reproducen el modelo entidad-relación. |
| Schemas | `app/schemas/` | Validación de entrada y serialización de salida. |

La fábrica `create_app()` en [`app/__init__.py`](../app/__init__.py) instala el
middleware de sesión,
los tres manejadores de error, los estáticos y los routers. La sesión SQLAlchemy
vive en un `ContextVar` y se expone como `db.session`.

---

## 3. Base de datos

- [`db/DDL.sql`](../db/DDL.sql) es la fuente de verdad: **25 tablas y 2 vistas**
  (`v_bandeja_validacion` y `v_ranking`), con claves foráneas, `ENUM` y `YEAR`.
- Los modelos ORM replican ese diseño. `create_all()` cubre un arranque desde
  cero; las vistas SQL solo las crea el DDL.
- [`db/seed.py`](../db/seed.py) puebla las tablas desde
  `app/data/simul_data.py`: la misma fuente de datos que usaba el frontend del
  corte 2. Todas las cuentas demo usan la contraseña `1234`.
- Diagrama entidad-relación: [`diagrama-ER.jpeg`](diagrama-ER.jpeg).

---

## 4. API REST y Swagger

Toda la API cuelga de `/api/museo`: **30 rutas y 37 operaciones** repartidas en
autenticación, contenido, validación, gamificación, administración y vistas del
museo. Están los cinco verbos HTTP y los códigos `200/201`, `401`, `403`,
`404`, `409` y `422`.

La evidencia manual se hace en **Swagger**, sin herramientas adicionales:

| Recurso | URL |
|---|---|
| Swagger UI | http://localhost:5000/docs |
| ReDoc | http://localhost:5000/redoc |
| Especificación OpenAPI | http://localhost:5000/openapi.json |

Las respuestas usan el sobre `{success, message, data|details}`. Los errores de
validación devuelven `details` por campo; los errores internos se registran en
servidor y al cliente solo llega un `500` genérico.

---

## 5. Seguridad

- Contraseñas: `PBKDF2-HMAC-SHA256` con sal aleatoria y comparación en tiempo
  constante (`app/utils/security.py`). El `password_hash` nunca se serializa.
- JWT HS256 con `sub = id_usuario`, `type = access` y expiración configurable
  (`app/utils/roles.py`).
- Dependencias `requiere_usuario` y `usuario_opcional`.
- Roles: `estudiante`, `docente`, `egresado` y `admin`. Bandeja de validación,
  aprobar/rechazar, KPIs, gestión de usuarios y borrado de contenido exigen
  `admin`.

---

## 6. Frontend conservado del corte 2

Las **21 vistas Jinja2** y su CSS/JS siguen en `app/templates` y `app/static`.
Sus datos viven en `app/data/simul_data.py` y se entregan a la página como JSON
para que JavaScript filtre y busque en `localStorage`: esas páginas **no llaman
a la API**. Esto es intencional y se explica así en los videos, para no
destruir el entregable anterior.

La migración de Flask a FastAPI fue una decisión deliberada del tercer corte:
el enunciado menciona Flask en algunos criterios, pero el código runtime no
contiene `import flask`. Jinja2 se conserva únicamente como motor de plantillas.

---

## 7. Trazabilidad de requerimientos

| Código | Requisito | Dónde se ve hoy |
|---|---|---|
| RF-USR-01/02/03 | Registro, login, perfil y dashboard por rol | `/api/museo/auth/*` + vistas `login`, `registro`, `perfil` |
| RF-EXP-01/02/04 | Explorar, buscar/filtrar, favoritos | `/api/museo/contenido`, `/api/museo`, vistas `explorar`, `buscar`, `favoritos` |
| RF-DSH-01..04 | Dashboards y KPIs | `/api/museo/admin/kpis`, vistas `dashboard_*` |
| RF-COM-01/02 | Registro de contenido por tipo | `/api/museo/contenido` y sus subtipos |
| RF-PRY-01/02 | Propuestas y proyectos asesorados | tipos de contenido `proyecto` y vistas asociadas |
| RF-VAL-01/03/04 | Bandeja, motivo al rechazar, publicación | `/api/museo/validacion/*` y `validacion_log` |
| RF-GAM-01..04 | Puntos, niveles, insignias, ranking | `/api/museo/gamificacion/*` y `historial_puntos` |
| RF-HIS-01 | Línea del tiempo | `/api/museo/timeline` y vista `index` |
| RNF-ACC-01 | Texto alternativo obligatorio | validación Pydantic de evidencias |
| RNF-SEG-02/04 | Control por rol y sesión | dependencias de auth + `guardPage()` en el frontend |

---

## 8. Ejecución, Docker y pruebas

```bash
docker compose up --build
docker compose exec app python db/seed.py
```

- API y Swagger: `http://localhost:5000/docs`
- MySQL: `localhost:3307` (`simul_db`, usuario `simul_user`)

Las **19 pruebas** (`pytest -q`) usan SQLite temporal y no tocan MySQL: cubren
documentación OpenAPI, autenticación, CRUD, validaciones, roles y gamificación.
La demostración en video usa Swagger, DBeaver y Docker; no se necesita ninguna
colección ni cliente externo.
