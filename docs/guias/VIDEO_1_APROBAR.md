# Video 1 — «Aprobar y publicar» (10 min)

**Integrante 1.** Ancla única: aprobación del administrador.
**No mencionar** los otros dos botones en ningún momento. Mostrar todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué hay que verificar |
|---|---|---|
| `app/templates/pages/admin_validacion.html` | `8` | `window.SIMUL_QUEUE = {{ simul_queue | tojson }}` |
| `app/templates/pages/admin_validacion.html` | `50-60` | contador `id="queue-counter"` («6 pendientes») |
| `app/templates/pages/admin_validacion.html` | `94` | contenedor `id="queue-list"` |
| `app/static/js/pages/admin_validacion.js` | `163-170` | botón con `data-approve` |
| `app/static/js/pages/admin_validacion.js` | `204-250` | función `aprobar(id)` |
| `app/static/js/pages/admin_validacion.js` | `374-383` | delegación del click (`closest('[data-approve]')`) |
| `app/routes/validacion_routes.py` | `47-73` | endpoint `aprobar` y sus decoradores |
| `app/controllers/validacion_controller.py` | `41-53`, `96-120` | `aprobar` y `_decidir` |
| `app/services/validacion_service.py` | `32` | `PUNTOS_PUBLICAR = 100` |
| `app/services/validacion_service.py` | `80-160` | método `aprobar` |
| `app/services/validacion_service.py` | `249-277` | `_cargar` (403 / 404 / 409) |
| `app/services/validacion_service.py` | `291-326` | `_notificar` y `_refrescar_gamificacion` |
| `app/repositories/contenido_repository.py` | `58-63` | `get_by_id` con `db.session.get` |
| `app/repositories/validacion_repository.py` | `36-...` | `add_log` (solo `add`, sin commit) |
| `app/models/contenido.py` | `6-...` | ENUM `estado`, FK `id_validador` |
| `app/models/validacion_log.py` | `6-...` | ENUM `accion` |
| `app/models/historial_puntos.py` | `6-...` | movimiento de puntos |
| `app/models/notificacion.py` | `6-20` | índice `idx_notif_usuario_leida` |
| `app/models/usuario.py` | `137` | propiedad `rol_nombre` |
| `tests/test_app.py` | `433-463` | `test_aprobar_suma_puntos_y_publica` |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [0:00] Acuerdo previo — 1:00

👉 **MOSTRAR:** pantalla de inicio del museo o `/docs`; no hace falta abrir código todavía.

> "Aclaración antes de empezar: la interfaz HTML es la entrega del **corte 2** y
> persiste en `localStorage`; el backend del **corte 3** expone esa misma operación
> como API REST y la demostramos en **Swagger contra MySQL**. El botón
> visual no llama a la API —lo dejamos así para conservar el entregable anterior—,
> pero la operación sí está implementada capa por capa y persiste. Arrancamos en
> Flask en el corte 2 y migramos a **FastAPI**, que da Swagger automático y
> validación con Pydantic. Los tres diremos lo mismo."

### [1:00] Presentación — 0:15

👉 **MOSTRAR:** `/admin/validacion` ya cargado, con sesión admin. Resaltar el contador `id="queue-counter"` (`admin_validacion.html:50-60`).

> "Soy **[NOMBRE]**. Voy a usar el botón **«Aprobar y publicar»** para explicarles **todo el proyecto**: cómo está armado, cómo persiste, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

👉 **MOSTRAR:** primero el editor en `admin_validacion.js:163-170` (el `data-approve`); después volver a la tarjeta y hacer clic en «Aprobar y publicar» para que se vea el toast.

> "Estoy en `/admin/validacion`: lo sirve FastAPI con una plantilla Jinja desde `web_routes.py`. El botón no tiene `id`: se genera en `admin_validacion.js` con `data-approve`, y el click se captura por delegación —`closest('[data-approve]')` → `aprobar(id)`—. Esa función hace `Store.upsertContent(status:'publicado')`, `Store.dropFromQueue` y un toast. Es `localStorage`: la capa visual del corte 2."

### [2:15] Ruta y controlador — 0:45

👉 **MOSTRAR:** editor en `validacion_routes.py:47-73` y luego `validacion_controller.py:41-53` y `:96-120`. En Swagger, abrir el endpoint y el `Authorize`.

> "La operación real es `POST /api/museo/validacion/{id}/aprobar`. El router lleva `Depends(requiere_usuario)`: sin token, **401**. La ruta recibe `DecisionIn | None` — observaciones opcionales, `Body(default=None)`—. El controlador `_decidir` obtiene al usuario con `usuario_actual()` y llama a `service.aprobar`. Detalle de diseño: el **rol no se comprueba aquí**, se comprueba en el servicio para que la regla no se pueda saltar desde otra ruta."

### [3:00] Servicio — 1:15

👉 **MOSTRAR:** `validacion_service.py:32` (constante), `:80-160` (método `aprobar`), `:249-277` (`_cargar`) y `:291-326` (notificación y gamificación). Resaltar el `commit` único al final.

> "`_cargar` devuelve **403** si `admin.rol_nombre != 'admin'` —propiedad que lee `self.rol.nombre`, en `usuario.py:137`—, **404** si no existe y **409** si `estado != 'pendiente'`: así no se decide dos veces. Después, en **una sola transacción**: estado `publicado`, `id_validador` y `fec_valid`; `ValidacionLog(accion='aprueba')`; notificación al autor; `registrar_movimiento(puntos=100)`, que suma `puntos_total` y escribe un `HistorialPuntos`; `_refrescar_gamificacion`, que recalcula el nivel por rangos y otorga insignias; y **un único commit**. O se hacen las seis cosas, o ninguna."

### [4:15] Repositorio, ORM y respuesta — 1:00

👉 **MOSTRAR:** `contenido_repository.py:58-63` y `validacion_repository.py:36-...`; luego ejecutar el endpoint en Swagger y mostrar el cuerpo 200 abajo.

> "`get_by_id` usa `db.session.get`, que aprovecha el mapa de identidad de SQLAlchemy. `add_log` solo hace `add`: no commitea. En `contenido.py`, `estado` es ENUM con índice y `id_validador` es FK con `ON DELETE SET NULL`. Ejecuto en Swagger → **HTTP 200**. El sobre es `{success, message, data}`, de `response.py:14-33`; aparece `estado: 'publicado'` y el validador como objeto, **nunca `password_hash`**. El middleware instala una sesión por petición, hace `commit` si el código es < 400 y `rollback` si no."

### [5:15] Persistencia — 1:00

👉 **MOSTRAR:** DBeaver con las tres consultas del respaldo ejecutadas una por una; resaltar `estado`, la fila `aprueba` y el `+100`.

> "En DBeaver muestro tres consultas: el contenido con su estado y los puntos del autor, la fila `aprueba` en `validacion_log` y el movimiento de **+100** en `historial_puntos`. Ahí está la prueba de que no es solo una respuesta bonita."

### [6:15] Arquitectura y base de datos — 1:00

👉 **MOSTRAR:** `app/__init__.py:208-238` (prefijos) y `db/DDL.sql:94-118`, `:355-370`, `:433-...` (tablas y vistas). Si alcanza, `docker-compose.yml:28-44`.

> "Salgo del botón para mostrar el resto. El backend tiene **7 capas**: `routes` define endpoints y dependencias, `controllers` arma la respuesta, `services` concentra las reglas de negocio, `repositories` construye consultas, `models` mapea tablas, `schemas` valida con Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`."

### [7:15] API REST y evidencia — 1:00

👉 **MOSTRAR:** `/docs` y `/openapi.json` en el navegador; `app/__init__.py:114-177` (los tres handlers).

> "Bajo `/api/museo` hay **30 rutas y 37 operaciones** en autenticación, contenido, validación, gamificación, administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y `/openapi.json` desde los decoradores. Los errores globales dan siempre el mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500 genérico con `logger.exception` en servidor, **sin traza al cliente**. En `/docs` ejecuto los endpoints y veo el código HTTP y el cuerpo de cada respuesta: esa es la evidencia."

### [8:15] Seguridad — 0:30

👉 **MOSTRAR:** `app/utils/security.py:23-71` y `app/utils/roles.py:191`; si alcanza, `app/schemas/simul_auth_schema.py:91-93` (docstring de `UsuarioOut`).

> "El login emite JWT con PBKDF2 + salt en `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring."

### [8:45] Pruebas, Docker y coherencia — 0:45

👉 **MOSTRAR:** terminal con `pytest -q` → 19 passed, `docker-compose.yml:16-18` y `:28-44`, y el README con el diagrama E-R.

> "`docker compose up --build` levanta `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19 pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas del corte 2 y este backend usan las mismas entidades y nombres de campo."

### [9:30] Cierre — 0:30

👉 **MOSTRAR:** volver a `/docs` y al botón en `/admin/validacion`; hablar mirando a cámara.

> "Los 6 criterios: (1) arquitectura modular de 7 capas, (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición, (5) evidencia en Swagger, Docker y 19 tests, y (6) trazabilidad de los tres cortes. Con eso doy por terminada la demostración."

## Respaldo (no leer)

```sql
SELECT c.id_contenido, c.titulo, c.estado, c.fec_valid, u.puntos_total
FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
WHERE c.id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT puntos, motivo FROM historial_puntos
WHERE id_contenido = <ID> ORDER BY fecha DESC;
```

- `get_nivel_por_puntos`: `>= mínimo y < máximo`, el último nivel incluye su máximo.
  Insignias: `puntos_requeridos <= puntos_total`.
- Los repositorios no commitean: el commit es del servicio; el middleware confirma la sesión.

**Preguntas propias de este botón:** ¿docente aprueba? → 403 en `_cargar`. ¿Cómo sabés
que son 100? → constante `PUNTOS_PUBLICAR` + fila en `historial_puntos`. ¿Dónde queda
el motivo? → `contenido.observaciones` y `validacion_log`. ¿Aprobar dos veces? → 409.
