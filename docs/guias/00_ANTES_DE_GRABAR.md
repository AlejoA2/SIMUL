# 00 — Antes de iniciar a grabar (común a los 3)

Leelo una vez antes de grabar tu video. Después abrí **tu** archivo
(`VIDEO_1_APROBAR.md`, `VIDEO_2_RECHAZAR.md` o `VIDEO_3_BUSCAR.md`), que tiene su
propia lista de archivos y líneas.

## 1. Configuración mínima

```bash
docker compose up --build
docker compose exec app python db/seed.py     # solo si la BD está vacía
pytest -q                                     # debe dar 19 passed
```

| Recurso | Valor |
|---|---|
| Swagger / OpenAPI | `http://localhost:5000/docs` y `/openapi.json` |
| API | `http://localhost:5000/api/museo/...` |
| MySQL (DBeaver) | `127.0.0.1:3307` · db `simul_db` · usuario `simul_user` · password `simul_password` |
| Admin de demo | `l.jimenez@unilibre.edu.co` / `1234` |

Si Docker no está arriba, Swagger da *Connection refused*.

## 2. Acuerdo previo — lo dicen los TRES, idéntico (0:00 – 1:00)

> "Aclaración antes de empezar: la interfaz HTML es la entrega del **corte 2** y
> persiste en `localStorage`; el backend del **corte 3** expone esa misma operación
> como API REST y la demostramos en **Swagger contra MySQL**. El botón
> visual no llama a la API —lo dejamos así para conservar el entregable anterior—,
> pero la operación sí está implementada capa por capa y persiste. Arrancamos en
> Flask en el corte 2 y migramos a **FastAPI**, que da Swagger automático y
> validación con Pydantic. Los tres diremos lo mismo."

## 3. Archivos y líneas que TODOS deben tener listos

Tenerlos abiertos en el editor (o al menos poder ir a ellos rápido). Son el
"tronco común" que aparece en los 3 videos.

| Archivo | Líneas | Qué contiene / para qué se muestra |
|---|---|---|
| `docker-compose.yml` | `16-18` | servicio `simul_app`, puerto `5000:5000` |
| `docker-compose.yml` | `28-44` | MySQL 8.4, puerto `3307:3306`, volumen, init script del DDL, healthcheck |
| `app/__init__.py` | `114-127` | handler de `StarletteHTTPException` |
| `app/__init__.py` | `128-158` | handler de `RequestValidationError` → 422 con `details` |
| `app/__init__.py` | `159-177` | handler de `Exception` → 500 genérico, sin traza |
| `app/__init__.py` | `208-238` | `include_router`: prefijos `/api/museo/...` |
| `app/utils/response.py` | `14-33` | `success()` → sobre `{success, message, data}` |
| `app/utils/response.py` | `34-...` | `error()` → sobre de error |
| `app/utils/roles.py` | `191`, `195` | `requiere_usuario` y `usuario_opcional` |
| `app/utils/security.py` | `23-46`, `49-85` | PBKDF2 + `verify_password`, sin `werkzeug` |
| `db/DDL.sql` | `94-118` | tabla `contenido` (ENUM, índices `idx_contenido_estado/tipo`) |
| `db/DDL.sql` | `355-370` | tabla `notificacion`, índice compuesto `idx_notif_usuario_leida` |
| `db/DDL.sql` | `375-389` | tabla `validacion_log` |
| `db/DDL.sql` | `394-408` | tabla `historial_puntos` |
| `db/DDL.sql` | `433-450` | vista `v_bandeja_validacion` |
| `db/DDL.sql` | `451-...` | vista `v_ranking` |
| `tests/test_app.py` | `20-41`, `511-525` | documentación OpenAPI y catálogos |

## 4. Cómo leer cada bloque del guion

Cada bloque del video tiene este formato:

```
### [mm:ss] Título del bloque
> "Me voy al archivo tal, líneas tantas a tantas… y después hago tal cosa."
```

La hora es **acumulada**: `[1:00]` significa "a partir del minuto 1". Todo lo que
está entre comillas **se dice en voz alta**, incluidos el nombre del archivo y el
rango de líneas. No hay instrucciones aparte: cuando el texto dice «me voy a…»,
movete al editor, a Swagger, a DBeaver o a la terminal y mostrás eso mismo.

## 5. Checklist rápido

- [ ] Docker `up` y `/docs` responde.
- [ ] DBeaver conectado a `127.0.0.1:3307`.
- [ ] Editor con los archivos de la tabla 3 **y los de tu video**.
- [ ] Acuerdo previo memorizado (lo dicen los tres igual).
