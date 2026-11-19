# Guiones de video — Tercer corte SIMUL

## Reglas del formato (-leelas antes de grabar-)

- **3 videos separados, 10 minutos cada uno.** El profesor verá **30 minutos en total**.
- **Cada video habla de UN solo botón.** Quien explica aprobar **no menciona** rechazar ni buscar; quien explica rechazar **no menciona** aprobar ni buscar; quien explica buscar **no menciona** ninguno de los otros dos. El botón es la puerta de entrada, no el tema.
- **Los 3 demuestran dominio de TODO el proyecto**: las 7 capas, el DDL de 25 tablas y 2 vistas, la API completa, la seguridad, Docker, las pruebas, Postman y la trazabilidad con los tres cortes. La diferencia entre videos es **solo por dónde se entra**.
- Texto con `>` = **se dice en voz alta**. El material de respaldo **no se lee**: está para responder preguntas.
- Cada guion es **autocontenido**: podés grabar tu video sin leer los otros dos.

---

## Acuerdo previo — lo dicen los TRES, idéntico (0:00 – 1:00)

> "Aclaración antes de empezar: la interfaz HTML es la entrega del **corte 2** y
> persiste en `localStorage`; el backend del **corte 3** expone esa misma operación
> como API REST y la demostramos en **Swagger y Postman contra MySQL**. El botón
> visual no llama a la API —lo dejamos así para conservar el entregable anterior—,
> pero la operación sí está implementada capa por capa y persiste. Arrancamos en
> Flask en el corte 2 y migramos a **FastAPI**, que da Swagger automático y
> validación con Pydantic. Los tres diremos lo mismo."

---

# VIDEO 1 — Botón «Aprobar y publicar» (10:00)

**Ancla única:** aprobación del administrador. **No mencionar los otros dos botones.**

> **[1:00] Presentación.** Soy **[NOMBRE]**. Voy a usar el botón **«Aprobar y
> publicar»** para explicarles **todo el proyecto**: cómo está armado, cómo
> persiste, cómo se prueba y cómo se conecta con los cortes anteriores.
>
> **[1:15] Capa visual.** Estoy en `/admin/validacion`: lo sirve FastAPI con una
> plantilla Jinja desde `web_routes.py`. El botón no tiene `id`: se genera en
> `admin_validacion.js` con `data-approve`, y el click se captura por delegación —
> `closest('[data-approve]')` → `aprobar(id)`. Esa función hace
> `Store.upsertContent(status:'publicado')`, `Store.dropFromQueue` y un toast.
> Es `localStorage`: la capa visual del corte 2.
>
> **[2:15] Ruta y controlador.** La operación real es
> `POST /api/museo/validacion/{id}/aprobar`. El router lleva
> `Depends(requiere_usuario)`: sin token, **401**. La ruta recibe `DecisionIn |
> None` — observaciones opcionales, `Body(default=None)`—. El controlador
> `_decidir` obtiene al usuario con `usuario_actual()` y llama a `service.aprobar`.
> Detalle de diseño: el **rol no se comprueba aquí**, se comprueba en el servicio
> para que la regla no se pueda saltar desde otra ruta.
>
> **[3:00] Servicio — el corazón.** `_cargar` devuelve **403** si
> `admin.rol_nombre != 'admin'` —propiedad que lee `self.rol.nombre`—, **404** si
> no existe y **409** si `estado != 'pendiente'`: así no se decide dos veces.
> Después, en **una sola transacción**: estado `publicado`, `id_validador` y
> `fec_valid`; `ValidacionLog(accion='aprueba')`; notificación al autor;
> `registrar_movimiento(puntos=100)`, que suma `puntos_total` y escribe un
> `HistorialPuntos`; `_refrescar_gamificacion`, que recalcula el nivel por rangos
> y otorga insignias; y **un único commit**. O se hacen las seis cosas, o ninguna.
>
> **[4:15] Repositorio, ORM y respuesta.** `get_by_id` usa `db.session.get`, que
> aprovecha el mapa de identidad de SQLAlchemy. `add_log` solo hace `add`: no
> commitea. En `contenido.py`, `estado` es ENUM con índice y `id_validador` es FK
> con `ON DELETE SET NULL`. Ejecuto en Swagger → **HTTP 200**. El sobre es
> `{success, message, data}`, de `response.py`; aparece `estado: 'publicado'` y el
> validador como objeto, **nunca `password_hash`**. El middleware instala una
> sesión por petición, hace `commit` si el código es < 400 y `rollback` si no.
>
> **[5:15] Persistencia.** En DBeaver muestro tres consultas: el contenido con su
> estado y los puntos del autor, la fila `aprueba` en `validacion_log` y el
> movimiento de **+100** en `historial_puntos`. Ahí está la prueba de que no es
> solo una respuesta bonita.
>
> **[6:15] Arquitectura y base de datos.** Salgo del botón para mostrar el resto.
> El backend tiene **7 capas**: `routes` define endpoints y dependencias,
> `controllers` arma la respuesta, `services` concentra las reglas de negocio,
> `repositories` construye consultas, `models` mapea tablas, `schemas` valida con
> Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla
> routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en
> `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas
> consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init
> script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión
> DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`.
>
> **[7:15] API REST y evidencia.** Bajo `/api/museo` hay **30 rutas y 37
> operaciones** en autenticación, contenido, validación, gamificación,
> administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y
> DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y
> `/openapi.json` desde los decoradores. Los errores globales dan siempre el
> mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500
> genérico con `logger.exception` en servidor, **sin traza al cliente**. La
> colección Postman tiene **6 carpetas y 23 requests** con bearer `{{token}}`.
>
> **[8:15] Seguridad.** El login emite JWT con PBKDF2 + salt en
> `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan
> `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas
> de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring.
>
> **[8:45] Pruebas, Docker y coherencia.** `docker compose up --build` levanta
> `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo
> con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19
> pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas
> del corte 2 y este backend usan las mismas entidades y nombres de campo.
>
> **[9:30] Cierre.** Los 6 criterios: (1) arquitectura modular de 7 capas,
> (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD
> y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición,
> (5) evidencia en Swagger, Postman, Docker y 19 tests, y (6) trazabilidad de los
> tres cortes. Con eso doy por terminada la demostración.

### Respaldo del video 1 (no leer)

```sql
SELECT c.id_contenido, c.titulo, c.estado, c.fec_valid, u.puntos_total
FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
WHERE c.id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT puntos, motivo FROM historial_puntos
WHERE id_contenido = <ID> ORDER BY fecha DESC;
```

- `PUNTOS_PUBLICAR = 100` en `validacion_service.py`; `_observaciones()` aplica `.strip()`.
- `get_nivel_por_puntos`: `>= mínimo y < máximo`, el último nivel incluye su máximo.
  Insignias: `puntos_requeridos <= puntos_total`.
- Los repos no commitean: el commit es del servicio; el middleware confirma la sesión.

**Preguntas propias de este botón:** ¿docente aprueba? → 403 en `_cargar`. ¿Cómo sabés
que son 100? → constante + fila en `historial_puntos`. ¿Dónde queda el motivo? →
`contenido.observaciones` y `validacion_log`. ¿Aprobar dos veces? → 409.

---

# VIDEO 2 — Botón «Rechazar» (10:00)

**Ancla única:** rechazo con motivo obligatorio. **No mencionar los otros dos botones.**

> **[1:00] Presentación.** Soy **[NOMBRE]**. Voy a usar el botón **«Rechazar»**
> para explicarles **todo el proyecto**: cómo está armado, cómo persiste, cómo se
> prueba y cómo se conecta con los cortes anteriores.
>
> **[1:15] Capa visual.** En la tarjeta está `data-reject` → `rechazar(id)`. Abre
> un modal con `<textarea id="reject-reason">`, etiqueta **«Observaciones \*»** y
> el botón «Confirmar rechazo». Si lo dejo vacío aparece *«Escribe el motivo del
> rechazo: es obligatorio (RNF-SEG-04)»*, código del corte 1. Detalle importante:
> el JS solo valida **no vacío** con `.trim()`; la longitud mínima la valida el
> backend. Otra vez: `localStorage`, capa visual del corte 2.
>
> **[2:15] Ruta y contrato.** `POST /api/museo/validacion/{id}/rechazar`, con
> `Depends(requiere_usuario)` → **401** sin token. El cuerpo es `RechazoIn`, con
> `observaciones` **required**, `min_length=5` y `max_length=1000`, definido en
> `contenido_schema.py` con `Field(...)`. FastAPI lo muestra en el *Request body*
> de Swagger. El controlador comprueba usuario y delega en `service.rechazar`.
>
> **[3:00] Validación y respuesta 422.** Mando `{}` → **HTTP 422** con
> `{success: false, message: 'Datos inválidos', details: {observaciones: [...]}}`.
> Ese 422 no lo escribe el endpoint: **FastAPI valida antes de entrar** con
> Pydantic v2 y el manejador global arma el `details` por campo. Es un código
> semántico, no un 400 genérico.
>
> **[3:45] Servicio.** `_cargar` repite **403** si no es admin, **404** si no
> existe y **409** si ya no está pendiente. Luego `_observaciones` limpia con
> `.strip()` y hay una **segunda defensa**: si queda vacío, el servicio devuelve
> su propio 422 — cinco espacios pasan `min_length=5`, pero `.strip()` los vuelve
> cadena vacía—. Después: estado `rechazado`, `id_validador`, `fec_valid`,
> `observaciones`, `ValidacionLog(accion='rechaza')`, notificación al autor, un
> commit y `success(..., 'Contenido rechazado')`. **No hay ni una llamada a
> gamificación: la regla premia publicar, no rechazar.** Repito el id → **409**.
>
> **[5:00] Auditoría y seguridad.** `GET …/{id}/historial` muestra `accion:
> 'rechaza'` con el mismo texto; aunque el router solo pide JWT, el controlador
> exige `rol_nombre == 'admin'` y da 403 si no. Errores: 401 sin token, 422
> validación, 500 genérico con `logger.exception` en servidor y **sin traza
> expuesta**. `AutorOut` solo expone id, nombre y foto; `UsuarioOut` dice
> literalmente *«Serialización de usuario SIN password_hash»*.
>
> **[6:15] Arquitectura y base de datos.** Salgo del botón para mostrar el resto.
> El backend tiene **7 capas**: `routes` define endpoints y dependencias,
> `controllers` arma la respuesta, `services` concentra las reglas de negocio,
> `repositories` construye consultas, `models` mapea tablas, `schemas` valida con
> Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla
> routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en
> `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas
> consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init
> script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión
> DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`.
>
> **[7:15] API REST y evidencia.** Bajo `/api/museo` hay **30 rutas y 37
> operaciones** en autenticación, contenido, validación, gamificación,
> administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y
> DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y
> `/openapi.json` desde los decoradores. Los errores globales dan siempre el
> mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500
> genérico con `logger.exception` en servidor, **sin traza al cliente**. La
> colección Postman tiene **6 carpetas y 23 requests** con bearer `{{token}}`; en
> la carpeta de validación está el request negativo que produce el 422.
>
> **[8:15] Seguridad.** El login emite JWT con PBKDF2 + salt en
> `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan
> `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas
> de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring.
>
> **[8:45] Pruebas, Docker y coherencia.** `docker compose up --build` levanta
> `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo
> con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19
> pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas
> del corte 2 y este backend usan las mismas entidades y nombres de campo.
>
> **[9:30] Cierre.** Los 6 criterios: (1) arquitectura modular de 7 capas,
> (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD
> y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición,
> (5) evidencia en Swagger, Postman, Docker y 19 tests, y (6) trazabilidad de los
> tres cortes. Con eso doy por terminada la demostración.

### Respaldo del video 2 (no leer)

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
- Postman: duplicá el request negativo y cambiá el body por un motivo ≥ 5 caracteres.

**Preguntas propias de este botón:** ¿422 o 400? → 422 es validación semántica.
¿No es redundante validar tres veces? → defensa en profundidad. ¿Quién lee el
motivo? → autor en Mis aportes y admin en `/historial`. ¿Quién ve el historial? →
solo admin, 403 si no. ¿Por qué no suma puntos? → regla de negocio deliberada.

---

# VIDEO 3 — Botón «Buscar / filtrar» (10:00)

**Ancla única:** búsqueda y filtrado del catálogo. **No mencionar los otros dos botones.**

> **[1:00] Presentación.** Soy **[NOMBRE]**. Voy a usar el buscador del museo para
> explicarles **todo el proyecto**: cómo está armado, cómo persiste, cómo se
> prueba y cómo se conecta con los cortes anteriores.
>
> **[1:15] Capa visual.** En `/buscar` no hay un botón con id: la búsqueda salta
> con el evento `input` de `#search-input`, con `data-filter-category` y
> `data-filter-year`, y con `#search-clear`. En `buscar.js`, `publicados()` lee
> `Store.getContent()` y filtra `status === 'publicado'`; `coincide()` compara
> texto en título y etiquetas, categoría y año, con el caso «Antes de 2019».
> Jinja inyecta los datos desde `simul_data.py`. No hay ni un `fetch`: es
> `localStorage`, la capa visual del corte 2.
>
> **[2:15] Ruta y validación.** `GET /api/museo/contenido/`, público. Swagger
> documenta los `Query(...)`: `q`, `categoria`, `tipo`, `anio` —mínimo 1900 y
> máximo 2100—, `page` (mínimo 1) y `per_page` (1 a 100). Si mando `anio=1800`
> → **422**: es validación declarativa, no un `if` dentro de la función. El
> controlador normaliza `None` a `page=1` y `per_page=12`. No hace falta token.
>
> **[3:00] Servicio, repositorio y SQL.** `get_publicados` filtra
> `estado == 'publicado'`, aplica filtros, hace `count()` para el total, ordena
> por `fec_crea.desc()` y aplica `offset((page-1)*per_page).limit(per_page)`.
> El resultado es un `@dataclass Pagina` con `pages = -(-total // per_page)`,
> el techo de la división. El texto usa `.ilike('%q%')` sobre `titulo` y
> `categoria` → `lower(...) LIKE lower(...)` en MySQL. El año vive en tablas de
> subtipo, así que se usa `id_contenido.in_(select(...))` y `extract('year',
> fecha)`. **¿Por qué `IN` y no `JOIN`?** Porque un `JOIN` duplicaría la fila de
> contenido. `estado`, `tipo`, `categoria` y `fec_crea` tienen índice en modelo y
> DDL; `YearType` crea `YEAR` en MySQL y `SMALLINT` en el SQLite de desarrollo.
>
> **[4:30] Respuesta.** Ejecuto con `q=museo&anio=2024` → **HTTP 200**, con
> `{success, message, data: {items, page, pages, total}}`. Cada item usa los
> mismos campos del prototipo —`tipo`, `titulo`, `categoria`, `anio`, `imagen`,
> `autor`—: ahí está la coherencia con el corte 2. El middleware instala sesión
> por petición, hace `commit` si el código es < 400 y `rollback` si no.
>
> **[5:15] Persistencia.** En DBeaver verifico que las filas devueltas tienen
> `estado='publicado'` y que los índices del DDL están creados sobre las columnas
> que filtra la consulta. Muestro también la vista del catálogo definida en
> `db/DDL.sql`.
>
> **[6:15] Arquitectura y base de datos.** Salgo del botón para mostrar el resto.
> El backend tiene **7 capas**: `routes` define endpoints y dependencias,
> `controllers` arma la respuesta, `services` concentra las reglas de negocio,
> `repositories` construye consultas, `models` mapea tablas, `schemas` valida con
> Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla
> routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en
> `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas
> consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init
> script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión
> DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`.
>
> **[7:15] API REST y evidencia.** Bajo `/api/museo` hay **30 rutas y 37
> operaciones** en autenticación, contenido, validación, gamificación,
> administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y
> DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y
> `/openapi.json` desde los decoradores. Los errores globales dan siempre el
> mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500
> genérico con `logger.exception` en servidor, **sin traza al cliente**. La
> colección Postman tiene **6 carpetas y 23 requests** con bearer `{{token}}`;
> la credencial admin real es `l.jimenez@unilibre.edu.co` / `1234`.
>
> **[8:15] Seguridad.** El login emite JWT con PBKDF2 + salt en
> `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan
> `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas
> de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring.
> El detalle de contenido usa `usuario_opcional`: funciona sin token y solo añade
> `es_favorito` si viene uno.
>
> **[8:45] Pruebas, Docker y coherencia.** `docker compose up --build` levanta
> `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo
> con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19
> pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas
> del corte 2 y este backend usan las mismas entidades y nombres de campo.
>
> **[9:30] Cierre.** Los 6 criterios: (1) arquitectura modular de 7 capas,
> (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD
> y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición,
> (5) evidencia en Swagger, Postman, Docker y 19 tests, y (6) trazabilidad de los
> tres cortes. Con eso doy por terminada la demostración.

### Respaldo del video 3 (no leer)

```sql
SELECT ... FROM contenido
WHERE contenido.estado = 'publicado'
  AND (lower(contenido.titulo) LIKE lower('%museo%')
       OR lower(contenido.categoria) LIKE lower('%museo%'))
  AND contenido.id_contenido IN (
        SELECT evento.id_contenido FROM evento
        WHERE EXTRACT(year FROM evento.fecha_evento) = 2024)
ORDER BY contenido.fec_crea DESC LIMIT 12, 12;
```

- `Pagina` y `_aplicar_filtros` están en `contenido_repository.py`; el filtro de
  año usa `IN` sobre cuatro subtipos con columna `anio` y `extract` para otros dos.
- Vistas del DDL: `v_bandeja_validacion` y `v_ranking`. Init script montado en
  `/docker-entrypoint-initdb.d/01_schema.sql`.

**Preguntas propias de este botón:** ¿por qué `IN` y no `JOIN`? → evita duplicados.
¿Cómo calculás la paginación? → `count()`, `offset/limit` y techo. ¿`anio=1800`? →
422 por `Query(ge=1900)`. ¿Por qué no hay `fetch` en la web? → prototipo del corte
2; cambiar el `fetch` sería lo único a tocar, las capas no se modifican.

---

# Preguntas genéricas — las responden los TRES

| Pregunta | Respuesta corta |
|---|---|
| ¿Flask o FastAPI? | Arrancamos en Flask; migramos a FastAPI (lo pide el resumen de criterios): OpenAPI automático, Pydantic y async. Quedan las plantillas Jinja. |
| ¿Por qué el botón no llama a la API? | Coherencia con el corte 2: era un prototipo sin BD. Cambiar el `fetch` en el JS sería lo único necesario; `routes → controllers → services → repositories → models` no se toca. |
| ¿Quién hace el commit? | El servicio, una vez; el middleware confirma la sesión si status < 400 y hace rollback si no. |
| ¿Cómo saben que los modelos corresponden al E-R? | `db/DDL.sql` (25 tablas, 2 vistas, ENUM, YEAR, FK, índices) se monta como init script; los modelos ORM replican tablas, columnas, relaciones e índices. |
| ¿Dónde se maneja un error inesperado? | Handler global `Exception`: 500 genérico, `logger.exception` en servidor, sin traza al cliente. |

## Errores que NO deben decir

- ❌ "El botón guarda en MySQL" → guarda en `localStorage`; MySQL se demuestra en Swagger/Postman.
- ❌ "El repo hace el commit" → lo hace el servicio; el middleware confirma o revierte.
- ❌ "Es Flask" → es FastAPI; Flask fue el corte 2.
- ❌ "Es un 400 cualquiera" → los errores de validación son **422** con `details`.
- ❌ Inventar un `require_admin` → no existe; el rol se comprueba con `rol_nombre`.
