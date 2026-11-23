# Video 3 — «Buscar / filtrar» (10 min)

**Integrante 3.** Ancla única: búsqueda y filtrado del catálogo.
**No mencionar** los otros dos botones en ningún momento. Mostrar todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué hay que verificar |
|---|---|---|
| `app/templates/pages/buscar.html` | `11` | `window.SIMUL_CONTENT = {{ simul_content | tojson }}` |
| `app/templates/pages/buscar.html` | `50-63` | campo `id="search-input"` |
| `app/templates/pages/buscar.html` | `146-152` | `id="search-count"` |
| `app/templates/pages/buscar.html` | `190-193` | `id="search-results"` |
| `app/templates/pages/buscar.html` | `216-218` | botón `id="search-clear"` |
| `app/static/js/pages/buscar.js` | `18` | `CATALOGO = window.SIMUL_CONTENT` |
| `app/static/js/pages/buscar.js` | `29`, `36` | `#search-input` y `#search-clear` |
| `app/static/js/pages/buscar.js` | `43-48`, `49-...` | `publicados()` y `coincide()` |
| `app/routes/web_routes.py` | `91-...` | vista `buscar` |
| `app/routes/contenido_routes.py` | `39-...` | `GET /api/museo/contenido/` y sus `Query(...)` |
| `app/controllers/contenido_controller.py` | `20-...` | `listar` (normaliza `None`) |
| `app/services/contenido_service.py` | `74-...` | `listar` |
| `app/repositories/contenido_repository.py` | `13-...` | `@dataclass Pagina` |
| `app/repositories/contenido_repository.py` | `65-...` | `get_publicados` (count, order, offset, limit) |
| `app/repositories/contenido_repository.py` | `369-...` | `_aplicar_filtros` (`ilike`, `IN`, `extract`) |
| `app/models/types.py` | `6-...` | `YearType` (YEAR en MySQL / SMALLINT en SQLite) |
| `db/DDL.sql` | `108-109` | `idx_contenido_estado`, `idx_contenido_tipo` |
| `db/DDL.sql` | `451-...` | vista `v_ranking` |
| `tests/test_app.py` | `511-525` | `test_ranking_y_catalogos` |

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

👉 **MOSTRAR:** `/buscar` ya cargado con el campo de búsqueda visible.

> "Soy **[NOMBRE]**. Voy a usar el buscador del museo para explicarles **todo el proyecto**: cómo está armado, cómo persiste, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

👉 **MOSTRAR:** editor en `buscar.html:50-63` y `buscar.js:18`, `:29`, `:43-49`; después escribir en el campo y ver cómo cambian los resultados.

> "En `/buscar` no hay un botón con id: la búsqueda salta con el evento `input` de `#search-input`, con `data-filter-category` y `data-filter-year`, y con `#search-clear`. En `buscar.js`, `publicados()` lee `Store.getContent()` y filtra `status === 'publicado'`; `coincide()` compara texto en título y etiquetas, categoría y año, con el caso «Antes de 2019». Jinja inyecta los datos desde `simul_data.py`. No hay ni un `fetch`: es `localStorage`, la capa visual del corte 2."

### [2:15] Ruta y validación — 0:45

👉 **MOSTRAR:** Swagger en `GET /api/museo/contenido/` con los parámetros desplegados; ejecutar con `anio=1800` para mostrar el 422.

> "`GET /api/museo/contenido/`, público. Swagger documenta los `Query(...)`: `q`, `categoria`, `tipo`, `anio` —mínimo 1900 y máximo 2100—, `page` (mínimo 1) y `per_page` (1 a 100). Si mando `anio=1800` → **422**: es validación declarativa, no un `if` dentro de la función. El controlador normaliza `None` a `page=1` y `per_page=12`. No hace falta token."

### [3:00] Servicio, repositorio y SQL — 1:30

👉 **MOSTRAR:** `contenido_repository.py:13`, `:66-...` y `:371-...`; resaltar `count()`, `offset/limit`, el techo de la división y el `IN (SELECT ...)`, además de `app/models/types.py:6`.

> "`get_publicados` filtra `estado == 'publicado'`, aplica filtros, hace `count()` para el total, ordena por `fec_crea.desc()` y aplica `offset((page-1)*per_page).limit(per_page)`. El resultado es un `@dataclass Pagina` con `pages = -(-total // per_page)`, el techo de la división. El texto usa `.ilike('%q%')` sobre `titulo` y `categoria` → `lower(...) LIKE lower(...)` en MySQL. El año vive en tablas de subtipo, así que se usa `id_contenido.in_(select(...))` y `extract('year', fecha)`. **¿Por qué `IN` y no `JOIN`?** Porque un `JOIN` duplicaría la fila de contenido. `estado`, `tipo`, `categoria` y `fec_crea` tienen índice en modelo y DDL; `YearType` crea `YEAR` en MySQL y `SMALLINT` en el SQLite de desarrollo."

### [4:30] Respuesta — 0:45

👉 **MOSTRAR:** ejecutar en Swagger con `q=museo&anio=2024` y mostrar el 200 con `items`, `page`, `pages` y `total`.

> "Ejecuto con `q=museo&anio=2024` → **HTTP 200**, con `{success, message, data: {items, page, pages, total}}`. Cada item usa los mismos campos del prototipo —`tipo`, `titulo`, `categoria`, `anio`, `imagen`, `autor`—: ahí está la coherencia con el corte 2. El middleware instala sesión por petición, hace `commit` si el código es < 400 y `rollback` si no."

### [5:15] Persistencia — 1:00

👉 **MOSTRAR:** DBeaver con la consulta del respaldo y las filas `estado='publicado'`; ampliar los índices de `db/DDL.sql:108-109` y la vista `v_ranking`.

> "En DBeaver verifico que las filas devueltas tienen `estado='publicado'` y que los índices del DDL están creados sobre las columnas que filtra la consulta. Muestro también la vista del catálogo definida en `db/DDL.sql`."

### [6:15] Arquitectura y base de datos — 1:00

👉 **MOSTRAR:** `app/__init__.py:208-238` y `db/DDL.sql:94-118`, `:355-370`, `:451-...`.

> "Salgo del botón para mostrar el resto. El backend tiene **7 capas**: `routes` define endpoints y dependencias, `controllers` arma la respuesta, `services` concentra las reglas de negocio, `repositories` construye consultas, `models` mapea tablas, `schemas` valida con Pydantic y `utils` tiene seguridad, respuestas y roles. `create_app()` ensambla routers, middlewares y errores. La base tiene **25 tablas y 2 vistas** en `db/DDL.sql`: ENUM de estados, `YEAR`, FK con `ON DELETE` explícito, índices en columnas consultadas y el compuesto `idx_notif_usuario_leida`. El DDL se monta como *init script* de MySQL, así que la BD nace igual al diagrama E-R del corte 2. Conexión DBeaver: `127.0.0.1:3307`, `simul_db`, `simul_user` / `simul_password`."

### [7:15] API REST y evidencia — 1:00

👉 **MOSTRAR:** `/docs` y `/openapi.json`; `app/__init__.py:114-177`.

> "Bajo `/api/museo` hay **30 rutas y 37 operaciones** en autenticación, contenido, validación, gamificación, administración y museo. Están los cinco métodos —GET, POST, PUT, PATCH y DELETE— con 200/201, 401, 403, 404, 409 y 422. FastAPI genera `/docs` y `/openapi.json` desde los decoradores. Los errores globales dan siempre el mismo sobre: 422 con `details`, código HTTP para excepciones de Starlette y 500 genérico con `logger.exception` en servidor, **sin traza al cliente**. En `/docs` ejecuto la búsqueda con parámetros y veo el **200** con `items`, `page`, `pages` y `total`: esa es la evidencia."

### [8:15] Seguridad — 0:30

👉 **MOSTRAR:** `app/utils/roles.py:191` y `app/utils/security.py:23-71`; si alcanza, `contenido_routes.py:155` (`usuario_opcional`).

> "El login emite JWT con PBKDF2 + salt en `app/utils/security.py`, sin `werkzeug`. Las rutas protegidas usan `Depends(requiere_usuario)` y el rol se comprueba con `rol_nombre`. Los esquemas de salida no exponen `password_hash`: `UsuarioOut` lo dice en su docstring. El detalle de contenido usa `usuario_opcional`: funciona sin token y solo añade `es_favorito` si viene uno."

### [8:45] Pruebas, Docker y coherencia — 0:45

👉 **MOSTRAR:** terminal con `pytest -q` → 19 passed; `docker-compose.yml:16-18` y `:28-44`; README con el diagrama E-R.

> "`docker compose up --build` levanta `simul_app` en 5000 y `simul_db` en 3307, con healthcheck e init script. Cargo con `docker compose exec app python db/seed.py` y corro `pytest -q`: **19 pruebas** en SQLite temporal. Y la coherencia: los RF del corte 1, las pantallas del corte 2 y este backend usan las mismas entidades y nombres de campo."

### [9:30] Cierre — 0:30

👉 **MOSTRAR:** volver a `/docs` y al buscador en `/buscar`; hablar mirando a cámara.

> "Los 6 criterios: (1) arquitectura modular de 7 capas, (2) SQLAlchemy + MySQL con 25 tablas espejo del E-R, (3) REST completo con CRUD y Swagger, (4) reglas de negocio, validación, JWT/roles y errores sin exposición, (5) evidencia en Swagger, Docker y 19 tests, y (6) trazabilidad de los tres cortes. Con eso doy por terminada la demostración."

## Respaldo (no leer)

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
