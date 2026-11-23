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
| `app/templates/pages/buscar.html` | `11`, `50-63`, `146-152`, `190-193`, `216-218` | datos, campo, contador, resultados y botón de limpiar |
| `app/static/js/pages/buscar.js` | `18`, `29`, `36` | datos cargados, campo y botón |
| `app/static/js/pages/buscar.js` | `43-47`, `49-77` | solo publicados y comparación de filtros |
| `app/routes/web_routes.py` | `90-108` | vista HTML del buscador |
| `app/routes/contenido_routes.py` | `35-86` | entrada de la consulta y filtros |
| `app/routes/contenido_routes.py` | `150-156` | detalle público con sesión opcional |
| `app/controllers/contenido_controller.py` | `20-36` | valores por defecto |
| `app/services/contenido_service.py` | `74-103` | armado de la respuesta |
| `app/repositories/contenido_repository.py` | `12-28` | resultado con total y páginas |
| `app/repositories/contenido_repository.py` | `65-104`, `369-448` | consulta y filtros |
| `app/models/types.py` | `6-28` | año en MySQL |
| `db/DDL.sql` | `108-109`, `451-464` | índices y vista del ranking |
| `tests/test_app.py` | `511-525` | prueba de catálogos y ranking |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [0:00] Acuerdo previo — 1:00

> "Me voy a la pantalla de inicio antes de empezar: es la entrega del corte 2 y guarda datos en el navegador. El corte 3 ofrece la misma acción como servicio, probado en Swagger contra MySQL. El buscador de la pantalla no llama al servicio; lo dejamos así para conservar lo anterior, pero la acción existe completa y consulta la base. Arrancamos en Flask y pasamos a FastAPI, que genera la documentación solo. Los tres diremos lo mismo."

### [1:00] Presentación — 0:15

> "Me voy a `/buscar`, con el campo de texto visible. Soy **[NOMBRE]** y voy a usar el buscador del museo para explicarles **todo el proyecto**: cómo está armado, cómo guarda, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

> "Me voy al editor, a `app/templates/pages/buscar.html`, línea 11, donde se entregan los datos; líneas 50 a 63 para el campo, 146 a 152 para el contador, 190 a 193 para los resultados y 216 a 218 para el botón de limpiar. Abro `app/static/js/pages/buscar.js`, línea 18, y las líneas 29 y 36; entre 43 y 47 se toma solo lo publicado y entre 49 y 77 se compara texto, categoría y año, incluso «Antes de 2019». Escribo en el campo y ves cómo cambia la lista. No hay llamada al servidor: es almacenamiento local del navegador, parte visual del corte 2."

### [2:15] De la pantalla al servidor — 0:45

> "Me voy a `app/routes/contenido_routes.py`, líneas 35 a 86: entra `GET /api/museo/contenido/`, que es público. Swagger muestra los filtros: texto, categoría, tipo, año entre **1900 y 2100**, página desde 1 y tamaño entre 1 y 100. Si mando `anio=1800`, aparece **422**. En `app/controllers/contenido_controller.py`, 20 a 36, los valores vacíos pasan a página 1 y 12 elementos. No hace falta iniciar sesión."

### [3:00] Servicio, consulta y base — 1:30

> "Me voy a `app/services/contenido_service.py`, líneas 74 a 103, y después a `app/repositories/contenido_repository.py`, líneas 12 a 28, 65 a 104 y 369 a 448. El servicio pide la página; la parte que consulta toma solo lo publicado, aplica filtros, cuenta el total, ordena por fecha y devuelve el bloque correspondiente. Las páginas se calculan con el total entre el tamaño, redondeado hacia arriba. El texto compara sin importar mayúsculas; el año vive en tablas aparte, por eso se usa una lista de identificadores y no se juntan tablas, para no duplicar filas. En `app/models/types.py`, 6 a 28, el año se guarda como YEAR en MySQL."

### [4:30] Respuesta — 0:45

> "Me voy a Swagger y ejecuto con `q=museo&anio=2024`: aparece **200** con `items`, `page`, `pages` y `total`. Cada elemento trae los campos del prototipo —tipo, título, categoría, año, imagen y autor—: ahí está la coherencia con el corte 2. La app confirma o deshace al terminar la petición."

### [5:15] Persistencia — 1:00

> "Me voy a DBeaver y compruebo que las filas tengan `estado='publicado'` y que los índices del DDL estén sobre esas columnas. En `db/DDL.sql`, líneas 451 a 464, muestro la vista del ranking, una consulta guardada con puntos y nivel. Las dos vistas de la base están al final del archivo."

### [6:15] Arquitectura y base de datos — 1:00

> "Me voy a `app/__init__.py`, líneas 208 a 238. El backend está en **siete partes**: entrada, orden del trabajo, reglas, consulta a la base, modelos, formatos y utilidades. En `db/DDL.sql`, líneas 94 a 118 y 355 a 408, están las tablas; entre 433 y 464, las dos vistas. Son **25 tablas y 2 vistas**, con índices en las columnas más usadas. El SQL se entrega a MySQL al crear el contenedor, igual al diagrama del corte 2. En DBeaver: `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`."

### [7:15] API REST y evidencia — 1:00

> "Me voy al navegador, a `/docs` y `/openapi.json`. Bajo `/api/museo` hay **30 rutas y 37 operaciones** de ingreso, contenido, validación, puntos, administración y museo, con los cinco métodos y respuestas 200, 201, 401, 403, 404, 409 y 422. Los errores traen siempre el mismo formato; el 422 señala el campo y un fallo interno solo muestra un mensaje general. Al ejecutar con parámetros veo el **200** con `items`, `page`, `pages` y `total`: esa es la evidencia."

### [8:15] Seguridad — 0:30

> "Me voy a `app/utils/roles.py`, línea 191: ahí está la comprobación de sesión para rutas privadas. En `app/routes/contenido_routes.py`, 150 a 156, el detalle permite entrar sin sesión; si viene una, solo añade el dato de favorito. La huella con valor aleatorio está en `app/utils/security.py`, 23 a 46 y 49 a 85, y los datos devueltos no incluyen la contraseña."

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
¿`anio=1800`? → 422 por el rango permitido. ¿Por qué no hay llamada al servidor en
la web? → es el prototipo del corte 2; cambiar eso sería lo único a tocar.
