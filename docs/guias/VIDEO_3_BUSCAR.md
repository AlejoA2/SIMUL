# Video 3 — «Buscar / filtrar» (10 min)

**Integrante 3.** Ancla única: búsqueda y filtrado del catálogo.
**No mencionar** los otros dos botones en ningún momento. Recorre todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué vas a señalar |
|---|---|---|
| `app/templates/pages/buscar.html` | `11`, `50-63`, `146-152`, `190-193`, `216-218` | datos de apoyo, campo, contador, resultados y botón de limpiar |
| `app/static/js/pages/buscar.js` | `41-54` | respuesta de la API convertida en tarjeta |
| `app/static/js/pages/buscar.js` | `56-69`, `92-120` | filtros enviados y consulta a la API |
| `app/static/js/pages/buscar.js` | `71-86` | pintado de la lista y del contador |
| `app/static/js/api.js` | `50-92`, `214-226` | petición HTTP y armado de la consulta |
| `app/routes/web_routes.py` | `90-108` | vista HTML del buscador |
| `app/routes/contenido_routes.py` | `37-100` | entrada de la consulta y filtros |
| `app/routes/contenido_routes.py` | `162-171` | detalle público con sesión opcional |
| `app/controllers/contenido_controller.py` | `20-49` | valores por defecto |
| `app/services/contenido_service.py` | `74-105` | armado de la respuesta |
| `app/repositories/contenido_repository.py` | `12-28` | resultado con total y páginas |
| `app/repositories/contenido_repository.py` | `65-104`, `369-448` | consulta y filtros |
| `app/models/types.py` | `6-28` | año en MySQL |
| `db/DDL.sql` | `108-109`, `451-464` | índices y vista del ranking |
| `tests/test_app.py` | `511-525` | prueba de catálogos y ranking |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [0:00] Acuerdo previo — 1:00

> "Me voy a la pantalla de inicio antes de empezar: es la entrega del corte 2. La sesión se guarda en el navegador, pero las acciones ya están conectadas: el botón llama a la API, la API guarda en MySQL y la misma operación se prueba en Swagger. Arrancamos en Flask y pasamos a FastAPI, que genera la documentación solo. Los tres diremos lo mismo."

### [1:00] Presentación — 0:15

> "Me voy a `/buscar`, con el campo de texto visible. Soy **[NOMBRE]** y voy a usar el buscador del museo para explicarles **todo el proyecto**: cómo está armado, cómo guarda, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

> "Me voy al editor, a `app/templates/pages/buscar.html`, línea 11 y líneas 50 a 63: ahí están las listas de apoyo y el campo. Sigo en 146 a 152, 190 a 193 y 216 a 218 para el contador, la cuadrícula y el botón de limpiar. Abro `app/static/js/pages/buscar.js`, líneas 41 a 54: cada fila se convierte en tarjeta con título, año, imagen y autor; entre 56 y 69 se arman los filtros y entre 92 y 120 se consulta la API. Escribo una palabra y la lista cambia con lo que devolvió MySQL. Me voy a `app/static/js/api.js`, 214 a 226, para ver la dirección armada."

### [2:15] De la pantalla al servidor — 0:45

> "Me voy a `app/routes/contenido_routes.py`, líneas 37 a 100: entra `GET /api/museo/contenido/`, que es público. Swagger muestra los filtros: texto, categoría, tipo, año entre **1900 y 2100**, página desde 1 y tamaño entre 1 y 100. Si mando `anio=1800`, aparece **422** con el nombre del campo. En `app/controllers/contenido_controller.py`, 20 a 49, los valores vacíos pasan a página 1 y 12 elementos. La vista HTML está en `app/routes/web_routes.py`, 90 a 108: solo prepara la página."

### [3:00] Servicio, consulta y base — 1:30

> "Me voy a `app/services/contenido_service.py`, líneas 74 a 105, y a `app/repositories/contenido_repository.py`, 12 a 28, 75 a 115 y 380 a 459. El servicio pide la página; la consulta toma solo lo publicado, aplica filtros, cuenta el total, ordena por fecha y devuelve ese bloque. El texto compara sin importar mayúsculas. El año vive en tablas aparte, por eso se usa una lista de identificadores y no se juntan tablas, para no duplicar filas; en `app/models/types.py`, 6 a 28, se guarda como YEAR. «Antes de 2019» se filtra después, porque no es un año exacto."

### [4:30] Respuesta — 0:45

> "Me voy a Swagger y ejecuto con `q=museo&anio=2024`: aparece **200** con `items`, `page`, `pages` y `total`. Cada elemento trae tipo, título, categoría, año, imagen y autor: ahí está la coherencia con el corte 2. Vuelvo a `buscar.js`, líneas 71 a 86: con esos campos se pinta la cuadrícula y el contador. Si falla la consulta, aparece un aviso y la lista queda vacía."

### [5:15] Persistencia — 1:00

> "Me voy a DBeaver y compruebo que las filas tengan `estado='publicado'` y que los índices del DDL estén sobre esas columnas, en `db/DDL.sql`, líneas 108 a 109. La búsqueda no escribe nada: solo lee lo que quedó guardado cuando el contenido se publicó. En líneas 451 a 464 muestro la vista del ranking, una consulta guardada con puntos y nivel. Las dos vistas de la base están al final del archivo."

### [6:15] Arquitectura y base de datos — 1:00

> "Me voy a `app/__init__.py`, líneas 208 a 238. El backend está en **siete partes**: entrada, orden del trabajo, reglas, consulta a la base, modelos, formatos y utilidades. En `db/DDL.sql`, líneas 94 a 118 y 355 a 408, están las tablas; entre 433 y 464, las dos vistas. Son **25 tablas y 2 vistas**, con índices en las columnas más usadas. El SQL se entrega a MySQL al crear el contenedor, igual al diagrama del corte 2. En DBeaver: `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`."

### [7:15] API REST y evidencia — 1:00

> "Me voy al navegador, a `/docs` y `/openapi.json`. Bajo `/api/museo` hay **30 rutas y 37 operaciones** de ingreso, contenido, validación, puntos, administración y museo, con los cinco métodos y respuestas 200, 201, 401, 403, 404, 409 y 422. Los errores traen siempre el mismo formato; el 422 señala el campo y un fallo interno solo muestra un mensaje general. Al ejecutar con parámetros veo el **200** con `items`, `page`, `pages` y `total`: esa es la evidencia."

### [8:15] Seguridad — 0:30

> "Me voy a `app/utils/roles.py`, línea 191: ahí se comprueba la sesión en rutas privadas. En `app/routes/contenido_routes.py`, 162 a 171, el detalle entra sin sesión; si viene una, solo añade el favorito. La huella con valor aleatorio está en `app/utils/security.py`, 23 a 46 y 49 a 85, y los datos devueltos no incluyen la contraseña. El buscador es público; el ingreso guarda el token para lo privado."

### [8:45] Pruebas, Docker y coherencia — 0:45

> "Me voy a la terminal: `pytest -q` da **19 pruebas** en una base temporal, sin tocar MySQL. En `tests/test_app.py`, 511 a 525, están las de catálogos y ranking. En `docker-compose.yml`, 14 a 24 y 27 a 44, se ve la app en el puerto 5000 y la base en el 3307 con el SQL inicial. Los requisitos del corte 1, las pantallas del corte 2 y este servicio usan las mismas entidades y nombres."

### [9:30] Cierre — 0:30

> "Me voy de nuevo a `/docs` y al buscador. Los **6 criterios**: siete partes, MySQL con 25 tablas y 2 vistas, API con Swagger, reglas y permisos, evidencia en Swagger, Docker y 19 pruebas, y coherencia entre los tres cortes. Termino aquí."

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

- El resultado con total y páginas está en `contenido_repository.py`.
- El filtro de año usa una lista de identificadores para no repetir filas.
- Las dos vistas del DDL son `v_bandeja_validacion` y `v_ranking`.
- El archivo SQL se monta como `/docker-entrypoint-initdb.d/01_schema.sql`.

**Preguntas propias de este botón:** ¿por qué una lista y no juntar tablas? →
evita duplicados. ¿Cómo se calculan las páginas? → total entre tamaño, hacia arriba.
¿`anio=1800`? → 422 por el rango permitido. ¿La lista sale del navegador? → no:
sale de MySQL por `/api/museo/contenido`; el navegador solo pinta la respuesta.
