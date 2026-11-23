# Video 2 — «Rechazar» (10 min)

**Integrante 2.** Ancla única: rechazo con motivo obligatorio.
**No mencionar** los otros dos botones en ningún momento. Mostrar todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué hay que verificar |
|---|---|---|
| `app/static/js/pages/admin_validacion.js` | `167-170` | botón con `data-reject` |
| `app/static/js/pages/admin_validacion.js` | `251-283` | `modalRechazo`, `#reject-reason`, `#reject-confirm` |
| `app/static/js/pages/admin_validacion.js` | `284-334` | función `rechazar(id)` y validación `.trim()` |
| `app/static/js/pages/admin_validacion.js` | `374-383` | delegación del click (`closest('[data-reject]')`) |
| `app/templates/pages/admin_validacion.html` | `8`, `50-60`, `94` | cola y contador |
| `app/schemas/contenido_schema.py` | `161-169` | `DecisionIn` (observaciones opcional) |
| `app/schemas/contenido_schema.py` | `170-182` | `RechazoIn` (`min_length=5`, `max_length=1000`) |
| `app/routes/validacion_routes.py` | `70-99` | endpoint `rechazar` y cuerpo `RechazoIn` |
| `app/routes/validacion_routes.py` | `102-...` | endpoint `historial` |
| `app/controllers/validacion_controller.py` | `54-66` | `rechazar` |
| `app/controllers/validacion_controller.py` | `67-95`, `83` | `historial` y su control de rol |
| `app/services/validacion_service.py` | `162-219` | método `rechazar` (sin llamadas a gamificación) |
| `app/services/validacion_service.py` | `220-248` | método `historial` |
| `app/services/validacion_service.py` | `249-277` | `_cargar` (403 / 404 / 409) |
| `app/services/validacion_service.py` | `278-290` | `_observaciones`: `.strip()` y 422 propio |
| `app/services/validacion_service.py` | `291-304` | `_notificar` |
| `app/repositories/validacion_repository.py` | `23-35` | `get_logs_de` |
| `app/models/validacion_log.py` | `6-...` | `accion ENUM('aprueba','rechaza')` |
| `tests/test_app.py` | `323-360` | `test_rechazo_exige_motivo` |
| `tests/test_app.py` | `361-377` | `test_historial_validacion_solo_admin` |

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

👉 **MOSTRAR:** `/admin/validacion` con sesión admin y una tarjeta pendiente visible.

> "Soy **[NOMBRE]**. Voy a usar el botón **«Rechazar»** para explicarles **todo el proyecto**: cómo está armado, cómo persiste, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

👉 **MOSTRAR:** editor en `admin_validacion.js:167-170` y `:251-283`; después volver a la tarjeta, hacer clic en «Rechazar» y dejar el motivo vacío para que aparezca el mensaje rojo.

> "En la tarjeta está `data-reject` → `rechazar(id)`. Abre un modal con `<textarea id=\"reject-reason\">`, etiqueta **«Observaciones \*»** y el botón «Confirmar rechazo». Si lo dejo vacío aparece *«Escribe el motivo del rechazo: es obligatorio (RNF-SEG-04)»*, código del corte 1. Detalle importante: el JS solo valida **no vacío** con `.trim()`; la longitud mínima la valida el backend. Otra vez: `localStorage`, capa visual del corte 2."

### [2:15] Ruta y contrato — 0:30

👉 **MOSTRAR:** Swagger en `POST /api/museo/validacion/{id}/rechazar`, con el *Request body* desplegado; editor en `contenido_schema.py:170-182`.

> "`POST /api/museo/validacion/{id}/rechazar`, con `Depends(requiere_usuario)` → **401** sin token. El cuerpo es `RechazoIn`, con `observaciones` **required**, `min_length=5` y `max_length=1000`, definido en `contenido_schema.py` con `Field(...)`. FastAPI lo muestra en el *Request body* de Swagger. El controlador comprueba usuario y delega en `service.rechazar`."

### [3:00] Validación y respuesta 422 — 0:45

👉 **MOSTRAR:** ejecutar en Swagger con `{}` y señalar el **422** con `details`; editor en `app/__init__.py:128-158`.

> "Mando `{}` → **HTTP 422** con `{success: false, message: 'Datos inválidos', details: {observaciones: [...]}}`. Ese 422 no lo escribe el endpoint: **FastAPI valida antes de entrar** con Pydantic v2 y el manejador global arma el `details` por campo. Es un código semántico, no un 400 genérico."

### [3:45] Servicio — 1:15

👉 **MOSTRAR:** `validacion_service.py:162-219` y `:278-290`; resaltar que en todo el método no aparece ninguna llamada a gamificación.

> "`_cargar` repite **403** si no es admin, **404** si no existe y **409** si ya no está pendiente. Luego `_observaciones` limpia con `.strip()` y hay una **segunda defensa**: si queda vacío, el servicio devuelve su propio 422 — cinco espacios pasan `min_length=5`, pero `.strip()` los vuelve cadena vacía—. Después: estado `rechazado`, `id_validador`, `fec_valid`, `observaciones`, `ValidacionLog(accion='rechaza')`, notificación al autor, un commit y `success(..., 'Contenido rechazado')`. **No hay ni una llamada a gamificación: la regla premia publicar, no rechazar.** Repito el id → **409**."

### [5:00] Auditoría y seguridad — 1:15

👉 **MOSTRAR:** ejecutar `GET …/{id}/historial` en Swagger; `validacion_controller.py:67-95` y `:83`; `app/utils/security.py:23-71`.

> "`GET …/{id}/historial` muestra `accion: 'rechaza'` con el mismo texto; aunque el router solo pide JWT, el controlador exige `rol_nombre == 'admin'` y da 403 si no. Errores: 401 sin token, 422 validación, 500 genérico con `logger.exception` en servidor y **sin traza expuesta**. `AutorOut` solo expone id, nombre y foto; `UsuarioOut` dice literalmente *«Serialización de usuario SIN password_hash»*."

### [6:15] Arquitectura y base de datos — 1:00

👉 **MOSTRAR:** `app/__init__.py:208-238` y `db/DDL.sql:375-389`, `:433-450`.

> "Salgo del botón para mostrar el resto. El backend tiene **7 capas**: `routes` define endpoints y dependencias, `controllers` arma la respuesta, `services` concentra las reglas de negocio, `repositories` construye consultas, `models` mapea tablas, `schemas` valida con Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`."

### [7:15] API REST y evidencia — 1:00

👉 **MOSTRAR:** `/docs` y `/openapi.json`; `app/__init__.py:114-177`; ejecutar en Swagger el request con `{}` para ver el 422.

> "Bajo `/api/museo` hay **30 rutas y 37 operaciones** en autenticación, contenido, validación, gamificación, administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y `/openapi.json` desde los decoradores. Los errores globales dan siempre el mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500 genérico con `logger.exception` en servidor, **sin traza al cliente**. En `/docs` ejecuto el request con un cuerpo inválido y veo el **422** con su `details`, y con un motivo válido veo el **200**: esa es la evidencia."

### [8:15] Seguridad — 0:30

👉 **MOSTRAR:** `app/utils/roles.py:191` y `app/utils/security.py:23-71`.

> "El login emite JWT con PBKDF2 + salt en `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring."

### [8:45] Pruebas, Docker y coherencia — 0:45

👉 **MOSTRAR:** terminal con `pytest -q` → 19 passed (resaltar `tests/test_app.py:323-377`); `docker-compose.yml:16-18` y `:28-44`.

> "`docker compose up --build` levanta `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19 pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas del corte 2 y este backend usan las mismas entidades y nombres de campo."

### [9:30] Cierre — 0:30

👉 **MOSTRAR:** volver a `/docs` y al modal en `/admin/validacion`; hablar mirando a cámara.

> "Los 6 criterios: (1) arquitectura modular de 7 capas, (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición, (5) evidencia en Swagger, Docker y 19 tests, y (6) trazabilidad de los tres cortes. Con eso doy por terminada la demostración."

## Respaldo (no leer)

```sql
SELECT id_contenido, titulo, estado, observaciones, fec_valid, id_validador
FROM contenido WHERE id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT id_notificacion, tipo, mensaje FROM notificacion
WHERE id_contenido = <ID> ORDER BY fecha_envio DESC;
```

- Doble validación: JS = respuesta inmediata; Pydantic = contrato de la API;
  servicio = defensa en profundidad para espacios en blanco.
- `v_bandeja_validacion` filtra `WHERE c.estado='pendiente'`: al rechazar, la fila
  desaparece de la vista. El autor lee el motivo en «Mis aportes» (RNF-SEG-04).
- En Swagger: ejecutá el request con `{}` para ver el 422 y con un motivo ≥ 5
  caracteres para ver el 200.

**Preguntas propias de este botón:** ¿422 o 400? → 422 es validación semántica.
¿No es redundante validar tres veces? → defensa en profundidad. ¿Quién lee el
motivo? → autor en Mis aportes y admin en `/historial`. ¿Quién ve el historial? →
solo admin, 403 si no. ¿Por qué no suma puntos? → regla de negocio deliberada.
