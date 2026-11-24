# Video 3 — «Buscar / filtrar» (11 min)

**Integrante 3.** Ancla única: la búsqueda del catálogo.
**No mencionar** los otros dos botones en ningún momento. Recorré todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué vas a señalar |
|---|---|---|
| `app/templates/pages/buscar.html` | `11-17`, `50-63` | listas de apoyo y campo de texto |
| `app/templates/pages/buscar.html` | `93-132`, `146-152`, `190-193`, `216-218` | filtros, contador, grilla y limpieza |
| `app/static/js/pages/buscar.js` | `41-54`, `56-69`, `71-86` | tarjeta, parámetros y pintado |
| `app/static/js/pages/buscar.js` | `92-121`, `203-220`, `234-243` | consulta, eventos y limpieza |
| `app/static/js/api.js` | `16-17`, `50-92`, `214-226` | dirección base, petición y armado de la consulta |
| `app/routes/web_routes.py` | `90-108` | vista HTML del buscador |
| `app/routes/contenido_routes.py` | `37-100` | entrada del listado y parámetros |
| `app/routes/contenido_routes.py` | `162-177` | detalle público con sesión opcional |
| `app/controllers/contenido_controller.py` | `20-49`, `51-60`, `271-280` | valores por defecto y detalle |
| `app/services/contenido_service.py` | `74-105`, `107-137` | armar la respuesta y el detalle |
| `app/services/contenido_service.py` | `590-607`, `863-929` | resumen de tarjeta, año, imagen y descripción |
| `app/repositories/contenido_repository.py` | `12-28`, `75-115` | sobre de página y consulta con total |
| `app/repositories/contenido_repository.py` | `380-459` | filtros de texto, categoría, tipo y año |
| `app/models/contenido.py` | `6-88` | entidad contenido, estado y fecha |
| `app/models/types.py` | `6-28` | año como YEAR en MySQL |
| `app/schemas/contenido_schema.py` | `109-121`, `259-276` | rango del año y formatos de salida |
| `app/utils/response.py` | `14-31`, `34-59` | sobre de respuesta y de error |
| `app/utils/roles.py` | `191`, `195` | sesión obligatoria y opcional |
| `app/utils/security.py` | `30-46`, `49-85` | huella de la clave y comparación segura |
| `app/__init__.py` | `128-157`, `208-239` | detalle del 422 y routers |
| `db/DDL.sql` | `94-118`, `108-111` | tabla contenido e índices |
| `db/DDL.sql` | `19-413`, `433-448`, `451-464` | 25 tablas y las dos vistas |
| `tests/test_app.py` | `20-39`, `511-525` | documentación OpenAPI y catálogos |
| `docker-compose.yml` | `14-24`, `27-44` | app en 5000, MySQL en 3307 y DDL inicial |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [00:48] Acuerdo previo — 0:48

> "Antes de empezar, recuerdo que esto es la entrega del tercer corte. En el corte uno definimos las entidades y las reglas; en el corte dos quedaron las pantallas. Hoy esas pantallas ya no viven solas: el botón llama a una dirección `/api/museo`, esa dirección guarda en MySQL y la misma operación se ejecuta en Swagger. Los tres usamos el mismo backend y las mismas credenciales. Yo voy a recorrer todo el proyecto desde una sola acción: la búsqueda."

### [01:11] Presentación — 0:23

> "Me voy a `/buscar`, con el campo de texto bien visible. Soy **[NOMBRE]** y hoy recorro el proyecto entero desde el buscador: cómo está armado, cómo guarda, cómo se prueba y cómo se conecta con los cortes anteriores."

### [02:13] La pantalla — 1:02

> "Abro `app/templates/pages/buscar.html`, líneas 11 a 17: ahí están las listas de categorías, años y slugs. En 50 a 63 está el campo de texto; en 93 a 132, los filtros laterales; en 146 a 152, el contador; en 190 a 193, la cuadrícula; y en 216 a 218, el botón de limpiar. Me voy a `app/static/js/pages/buscar.js`, líneas 41 a 54: cada fila se convierte en tarjeta con título, año, imagen y autor. Escribo una palabra y la lista cambia. La vista HTML que prepara todo está en `app/routes/web_routes.py`, 90 a 108."

### [03:18] Del campo a la dirección — 1:05

> "Sigo en `buscar.js`, 56 a 69: el campo y los filtros arman `GET /api/museo/contenido/` con `q`, `categoria`, `tipo`, `anio`, `page` y `per_page`. La pantalla manda `q`, `categoria`, `anio` y `per_page` en cien para traer todo; `tipo` y `page` también se pueden mandar en la dirección. En 92 a 121 se dispara la consulta y en 71 a 86 se pintan la grilla y el contador. Si falla la conexión, aparece el aviso y la lista queda vacía. Me voy a `app/static/js/api.js`, 16 y 214 a 226: ahí se arma la dirección completa y en 50 a 92 se lee la respuesta."

### [04:10] El endpoint público — 0:52

> "Me voy a `app/routes/contenido_routes.py`, líneas 37 a 100: entra `GET /api/museo/contenido/`, sin sesión. Los parámetros son texto, categoría exacta, tipo, año entre 1900 y 2100, página desde 1 y tamaño entre 1 y 100. Con `anio=1800` aparece 422 y el mensaje nombra el campo: el rango está declarado en 62 a 67. La respuesta 200 trae `items`, `page`, `pages` y `total`. Cada ítem trae tipo, título, categoría, año, imagen, descripción y autor: lo mismo que vimos en el corte dos."

### [05:17] Las siete capas — 1:07

> "Recorro las siete capas, una por una. Entrada: `app/routes/contenido_routes.py`, 37 a 100, y `app/routes/web_routes.py`, 90 a 108. Orden del trabajo: `app/controllers/contenido_controller.py`, 20 a 49, que pone página 1 y doce elementos por defecto. Reglas: `app/services/contenido_service.py`, 74 a 105. Acceso a datos: `app/repositories/contenido_repository.py`, 12 a 28 y 75 a 115. Modelos: `app/models/contenido.py`, 6 a 88, y `app/models/types.py`, 6 a 28. Formatos: `app/schemas/contenido_schema.py`, 259 a 276, y `app/utils/response.py`, 14 a 31. Utilidades: `app/utils/roles.py`, 191 y 195, y `app/utils/security.py`, 30 a 85."

### [06:16] La consulta y la base — 0:59

> "Me voy al repositorio, líneas 86 a 115: solo se lee `estado='publicado'`; se cuenta el total, se ordena por fecha y se pagina de forma explícita. En 389 a 398, el texto compara sin importar mayúsculas. En 400 a 410, categoría y tipo son exactos. El año vive en tablas aparte, por eso se usa una lista de identificadores y no se juntan tablas, para no duplicar filas; está en 412 a 457. En `app/models/types.py`, 6 a 28, el año se guarda como YEAR. Los índices están en `db/DDL.sql`, 108 a 111."

### [07:09] La respuesta y el detalle — 0:53

> "Vuelvo a `app/services/contenido_service.py`, 95 a 105 y 590 a 607: el servicio arma el sobre con `items`, `page`, `pages` y `total`, y cada resumen trae los campos de la tarjeta. Después me voy a `app/routes/contenido_routes.py`, 162 a 177: `GET /api/museo/contenido/{id}` entra sin sesión; si viene una, solo añade el favorito. Si el identificador no existe o no está publicado para quien consulta, el servicio responde 404, en 113 a 133. Lo muestro en Swagger: 200 con la ficha completa."

### [08:01] Swagger, paso a paso — 0:52

> "Ahora abro `/docs`. Busco `GET /api/museo/contenido/`, hago clic en Try it out, pongo `q=proyecto&anio=2023` — un término que sé que devuelve filas — y ejecuto. Aparece 200 con `items`, `page`, `pages` y `total`. Repito con `anio=1800`: 422 con el nombre del campo. Después ejecuto `GET /api/museo/contenido/{id}` con un identificador de la lista: 200. Abro `/openapi.json` y cuento: 30 rutas y 37 operaciones. En `app/__init__.py`, 128 a 157, se arma el 422 con el detalle del campo."

### [08:45] DBeaver — 0:44

> "Me voy a DBeaver, conectado a `127.0.0.1:3307`. La búsqueda no escribe: compruebo que las filas tengan `estado='publicado'` y que los índices del DDL estén sobre esas columnas, en `db/DDL.sql`, 108 a 111. Las filas que veo coinciden con lo que devolvió Swagger. Al final del DDL, en 433 a 448 y 451 a 464, están las dos vistas `v_bandeja_validacion` y `v_ranking`: consultas guardadas, no tablas nuevas."

### [09:36] Arquitectura y Docker — 0:51

> "Me voy a `app/__init__.py`, 208 a 239: ahí están los `include_router` con el prefijo `/api/museo`. El prefijo se repite en los seis routers de la API. Siete capas arriba, 25 tablas y 2 vistas abajo en `db/DDL.sql`, de la línea 19 a la 464. En `docker-compose.yml`, 14 a 24 y 27 a 44, la app queda en el puerto 5000 y MySQL en el 3307, con el DDL como script inicial. Coherencia total con los cortes uno y dos."

### [10:09] Seguridad — 0:33

> "Seguridad: en `app/utils/security.py`, 30 a 85, la clave se guarda como huella con valor aleatorio y se compara de forma segura. El token sirve para lo privado; el listado es público. La respuesta no incluye la clave. En `app/utils/roles.py`, 191 y 195, la sesión es opcional solo donde corresponde."

### [10:38] Pruebas — 0:29

> "En la terminal, `.\.venv\Scripts\python.exe -m pytest -q` da 19 pruebas en una base temporal, sin tocar MySQL. El comando corto `pytest -q` da el mismo resultado. En `tests/test_app.py`, 20 a 39, está la de la documentación, y en 511 a 525, la de catálogos."

### [11:04] Cierre — 0:26

> "Cierro con los 6 criterios: siete capas; MySQL con 25 tablas y 2 vistas; API con Swagger, 30 y 37; reglas y permisos; evidencia en Swagger, Docker y 19 pruebas; y coherencia entre los tres cortes. Me quedo en el buscador. Termino aquí."

## Respaldo (no leer)

Consulta equivalente a la búsqueda con texto y año:

```sql
SELECT c.id_contenido, c.titulo, c.categoria, c.estado, c.fec_crea
FROM contenido c
WHERE c.estado = 'publicado'
  AND (LOWER(c.titulo) LIKE LOWER('%proyecto%')
       OR LOWER(c.categoria) LIKE LOWER('%proyecto%'))
  AND (
        c.id_contenido IN (
          SELECT a.id_contenido FROM acontecimiento a WHERE a.anio = 2023
        ) OR c.id_contenido IN (
          SELECT p.id_contenido FROM premio p WHERE p.anio = 2023
        ) OR c.id_contenido IN (
          SELECT p.id_contenido FROM proyecto p WHERE p.anio = 2023
        ) OR c.id_contenido IN (
          SELECT av.id_contenido FROM avance_investigacion av
          WHERE av.anio = 2023
        ) OR c.id_contenido IN (
          SELECT e.id_contenido FROM evento e
          WHERE YEAR(e.fecha_evento) = 2023
        ) OR c.id_contenido IN (
          SELECT n.id_contenido FROM noticia n
          WHERE YEAR(n.fecha_publicacion) = 2023
        )
      )
ORDER BY c.fec_crea DESC
LIMIT 100;
```

- El sobre con total y páginas está en `contenido_repository.py`, 12 a 28 y 98 a 115.
- `pages` sale de total entre tamaño, hacia arriba: `-(-total // per_page)`, línea 114.
- El detalle público con sesión opcional está en `contenido_routes.py`, 162 a 177; el
  marcador de favorito se arma en `contenido_service.py`, 681 a 687.
- Las dos vistas del DDL son `v_bandeja_validacion` y `v_ranking`.
- El SQL entra a MySQL como `/docker-entrypoint-initdb.d/01_schema.sql`.

**Preguntas propias de este botón:** ¿por qué una lista de identificadores y no juntar
tablas? → cada subtipo guarda el año a su manera; juntar tablas repetiría la fila
base. ¿De dónde salen los resultados? → de MySQL por `GET /api/museo/contenido/`; el
navegador solo pinta la respuesta. ¿`anio=1800`? → 422, porque la ruta pide un año
entre 1900 y 2100. ¿La búsqueda escribe? → no, solo lee filas publicadas. ¿Y si no
hay coincidencias? → 200 con `items` vacío, `total` en cero y el aviso «Sin
resultados».
