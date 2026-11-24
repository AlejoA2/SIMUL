# Video 3 — «Buscar / filtrar» (11 min)

**Integrante 3.** Ancla única: la búsqueda del catálogo. **No mencionar** los otros
dos botones. Recorrer el proyecto entero desde este botón, demostrando dominio de la
arquitectura y cumpliendo la rúbrica.

**Cómo leer:**

- **`[PANTALLA: ...]`** y **`[CÓDIGO: archivo → líneas]`** en negrita = indicación,
  **no se lee**. Cada bloque dice si mostrás la página o el código, y un solo archivo
  por bloque.
- Todo lo demás se lee en voz alta, con calma, en frases cortas.
- Los `[mm:ss]` son tiempos de referencia. El material de «Respaldo» **no se lee**.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md).

## Antes de iniciar a grabar

Abrir estos archivos en el editor (una sola vez, para no perder tiempo buscando):

| Archivo | Líneas |
|---|---|
| `app/templates/pages/buscar.html` | 50-63, 93-132, 147, 190-193 |
| `app/static/js/pages/buscar.js` | 56-69, 71-86, 92 |
| `app/static/js/api.js` | 16, 50-92, 214-226 |
| `app/routes/contenido_routes.py` | 37-100 |
| `app/controllers/contenido_controller.py` | 20-49 |
| `app/services/contenido_service.py` | 74-105, 590 |
| `app/repositories/contenido_repository.py` | 75-115, 380-459 |
| `app/models/contenido.py` | 6-88 |
| `db/DDL.sql` | 94-118, 108-111 |
| `app/__init__.py` | 208-239 |
| `tests/test_app.py` | 20, 511 |
| `docker-compose.yml` | 14-24, 27-44 |

---

## Guion

### [00:48] Intro — mi botón — 0:40

**[PANTALLA: `http://localhost:5000/buscar`]**

Soy [NOMBRE]. Esto es el tercer corte: el corte uno definió las entidades y las
reglas, el corte dos dejó las pantallas, y hoy esas pantallas hablan con el servidor.
Voy a recorrer todo el proyecto desde un solo botón: el de buscar. Escribo «proyecto»
y la grilla pasa de 21 tarjetas a 2. Ese viaje —del campo a la base y de vuelta— es
lo que voy a explicar.

### [01:28] La página: el HTML (capa de presentación) — 0:40

**[CÓDIGO: `app/templates/pages/buscar.html` → líneas 50 a 63]**

Primero la capa de presentación: este es el HTML de la página. Acá está el campo de
búsqueda, con id `search-input`. En el mismo archivo están los filtros de categoría
y año —líneas 93 a 132—, el contador `search-count` —línea 147— y la grilla
`search-results` —líneas 190 a 193—, que está vacía hasta que llegan los datos. Esta
capa solo muestra: no decide nada y no habla con la base.

### [02:08] El JavaScript del buscador — 0:45

**[CÓDIGO: `app/static/js/pages/buscar.js` → líneas 56 a 69 y 92]**

Segunda parada, todavía en el navegador. Cada tecla que escribo dispara la función
`buscar` —línea 92 de este archivo—. Esa función arma los parámetros: el texto va en
`q`, la categoría en `categoria`, el año en `anio` —líneas 56 a 69— y llama a la API.
Cuando llega la respuesta, la función `pintar` —líneas 71 a 86— llena la grilla y
actualiza el contador. Concepto: el navegador no toca la base; pide y pinta.

### [02:53] El cliente de la API — 0:35

**[CÓDIGO: `app/static/js/api.js` → líneas 214 a 226]**

Tercera parada: `SIMULApi.contenido` convierte esos parámetros en la dirección
`/api/museo/contenido/?q=proyecto&anio=2023`. La base de todas las llamadas,
`/api/museo`, está en la línea 16 de este archivo, y la función `request` —líneas 50
a 92— hace el `fetch` y devuelve el campo `data`. Hasta acá, el navegador. Ahora
empieza el servidor.

### [03:28] Capa 1 · Rutas — la puerta de entrada — 0:45

**[CÓDIGO: `app/routes/contenido_routes.py` → líneas 37 a 100]**

Primera capa del servidor: rutas, la puerta de entrada de la API. En la línea 37
está declarado `GET /api/museo/contenido`. Esta capa solo recibe y valida: el año
tiene que estar entre 1900 y 2100 —líneas 62 a 67—, así que `anio=1800` responde 422
sin pasar a ninguna otra capa. Es un endpoint público, con sesión opcional —línea
44—. Al final, la función llama al controlador —líneas 92 a 100—.

### [04:13] Capa 2 · Controladores — 0:35

**[CÓDIGO: `app/controllers/contenido_controller.py` → líneas 20 a 49]**

Segunda capa: controladores. Coordinan y aplican permisos; no tocan la base. El
método `listar` pone los valores por defecto —página 1 y 12 elementos, líneas 45 a
48— y si alguien pide ver pendientes sin ser admin, responde 403 —líneas 31 a 37—.
Para la búsqueda pública, solo pasa todo al servicio.

### [04:48] Capa 3 · Servicios — 0:40

**[CÓDIGO: `app/services/contenido_service.py` → líneas 74 a 105]**

Tercera capa: servicios, las reglas del negocio. El método `listar` le pide al
repositorio la página publicada —línea 85 de este archivo— y arma la respuesta:
`items`, `page`, `pages` y `total`. Además, cada fila se convierte en resumen de
tarjeta en la línea 590 de este archivo: título, categoría, año, imagen y autor. Eso
es exactamente lo que después se ve en la grilla de la página.

### [05:28] Capa 4 · Repositorios — 0:45

**[CÓDIGO: `app/repositories/contenido_repository.py` → líneas 75 a 115 y 380 a 459]**

Cuarta capa: repositorios, la única capa que genera SQL. `get_publicados` filtra
solo lo publicado —líneas 86 a 88—, cuenta el total, ordena por fecha y pagina con
`offset` y `limit`. Los filtros del botón están en `_aplicar_filtros` —líneas 380 a
459—: el texto compara título o categoría sin distinguir mayúsculas, y el año se
resuelve con subconsultas porque cada subtipo guarda el año a su manera.

### [06:13] Capa 5 · Modelos y MySQL — 0:40

**[CÓDIGO: `app/models/contenido.py` → líneas 6 a 88, y después `db/DDL.sql` → líneas 94 a 118]**

Quinta capa: el modelo. La clase `Contenido` es una clase de SQLAlchemy, el espejo
en Python de la tabla contenido —tipo, título, categoría, estado y fechas—. Y la
tabla real está en `db/DDL.sql`, línea 94, con los índices de la búsqueda en las
líneas 108 a 111: estado, tipo, categoría y fecha. Aquí está la verdad: MySQL, con
25 tablas y 2 vistas. Esta búsqueda solo lee; nunca escribe.

### [06:53] De vuelta en la página — 0:35

**[PANTALLA: `/buscar` — escribir `proyecto`]**

La respuesta vuelve por las mismas capas, en orden inverso, y el JavaScript pinta la
grilla. Se refleja en la página así: el contador dice «2 resultados encontrados» y
aparecen las dos tarjetas. Si escribo algo sin coincidencias, aparece «Sin
resultados» con su botón Limpiar. Ese es el circuito completo: del campo a MySQL y de
vuelta a la página.

### [07:28] Swagger — la misma prueba, sin navegador — 0:50

**[PANTALLA: `http://localhost:5000/docs`]**

El mismo circuito, ahora desde la documentación. En `GET /api/museo/contenido/` hago
Try it out con `q=proyecto` y `anio=2023`: responde 200 con `items`, `page`, `pages`
y `total` —dos filas, las mismas que acabo de ver en la página—. Cambio a
`anio=1800`: 422 con `details.query.anio`, que nombra el campo. Con `id=1` en
`GET /api/museo/contenido/{id}`: 200 con la ficha completa. Y en `/openapi.json`:
30 rutas y 37 operaciones.

### [08:18] MySQL — las mismas filas — 0:40

**[PANTALLA: DBeaver, `127.0.0.1:3307`, base `simul_db`]**

Y la misma búsqueda en la base de datos. Corro la consulta —está en
`VIDEO_3_PASOS.md`, sección 4—: da 2 filas, ids 1 y 12, exactamente las que devolvió
Swagger. `SHOW INDEX` muestra los índices que acabo de señalar en el DDL. La
búsqueda no escribe nada: solo lee filas publicadas.

### [08:58] Arquitectura, FastAPI y Docker — 0:45

**[CÓDIGO: `app/__init__.py` → líneas 208 a 239]**

Este es el armado general: acá se montan los routers con el prefijo `/api/museo`.
Siete capas en total —rutas, controladores, servicios, repositorios, modelos,
esquemas y utilidades— y abajo MySQL con 25 tablas y 2 vistas. Criterio 1 de la
rúbrica, arquitectura: este recorrido. Criterio 3, FastAPI con Swagger: está, porque
FastAPI genera la documentación sola y trae la validación de parámetros incluida. En
`docker-compose.yml` la app corre en el puerto 5000 y MySQL en el 3307, con el DDL
como script inicial. Y es coherente con los cortes uno y dos: mismas entidades,
mismas pantallas, mismas credenciales.

### [09:43] Seguridad — 0:35

**[PANTALLA: Swagger]**

Criterio 4, seguridad. El catálogo es público; lo personal pide token. Ejecuto
`GET /gamificacion/mi-historial` sin Authorize: 401. Hago login con el admin, copio
el token, lo pego en Authorize y repito: 200. Las claves se guardan como huella en
`app/utils/security.py` y nunca salen en una respuesta; los roles y permisos están en
`app/utils/roles.py`.

### [10:18] Pruebas — 0:25

**[PANTALLA: terminal]**

Criterio 5, pruebas y Docker. En la terminal, `pytest -q` da 19 pruebas en una base
temporal, sin tocar MySQL; están en `tests/test_app.py`, con la de OpenAPI en la
línea 20. Y Docker levanta todo con `docker compose up -d`.

### [10:43] Cierre — los 6 criterios — 0:30

Cierro con los seis criterios: uno, arquitectura por capas; dos, MySQL con
SQLAlchemy, 25 tablas y 2 vistas; tres, API REST con GET, POST, PUT, PATCH y DELETE
documentada en Swagger —30 rutas y 37 operaciones—; cuatro, validaciones, reglas y
permisos —422, 401 y 403—; cinco, evidencia en Swagger, Docker y 19 pruebas; y seis,
coherencia entre los tres cortes. Todo demostrado desde un solo botón: el de buscar.
Termino aquí.

---

## Respaldo (no leer)

Consulta equivalente a la búsqueda con texto y año (la que se corre en DBeaver):

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

- El sobre con total y páginas está en `contenido_repository.py`, 12 a 28; `pages`
  sale de `-(-total // per_page)`, línea 114.
- Las dos vistas del DDL son `v_bandeja_validacion` y `v_ranking`.
- El SQL entra a MySQL como `/docker-entrypoint-initdb.d/01_schema.sql`.

**Preguntas propias de este botón:** ¿por qué subconsultas y no un `join`? → cada
subtipo guarda el año a su manera; juntar tablas repetiría la fila base y el total
mentiría. ¿De dónde salen los resultados? → de MySQL por `GET /api/museo/contenido/`;
el navegador solo pinta. ¿`anio=1800`? → 422, porque la ruta pide un año entre 1900
y 2100. ¿La búsqueda escribe? → no, solo lee filas publicadas. ¿Y sin coincidencias?
→ 200 con `items` vacío y el aviso «Sin resultados».
