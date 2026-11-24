# Video 3 — «Buscar / filtrar» (11 min)

**Integrante 3.** Ancla única: la búsqueda del catálogo.
**No mencionar** los otros dos botones en ningún momento. Recorré todo el proyecto a
través de este botón.

**Cómo leer este guion:** lo que está en **negrita dentro de corchetes** es indicación
de cámara o editor —no se lee en voz alta—. Todo lo demás es lo que hablas, en frases
cortas y con calma. Los `[mm:ss]` son los tiempos de referencia. Cada bloque dice
primero **en qué capa estás y para qué sirve**, después qué hace ahí el botón de
buscar, y al final dónde se señala el código.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué vas a señalar |
|---|---|---|
| `app/templates/pages/buscar.html` | `11-17`, `50-63` | listas de apoyo y campo de texto |
| `app/templates/pages/buscar.html` | `93-132`, `146-152`, `176-193`, `216-218` | filtros, contador, esqueleto, grilla y limpieza |
| `app/static/js/pages/buscar.js` | `18-22`, `41-54` | estado y tarjeta |
| `app/static/js/pages/buscar.js` | `56-69`, `71-86`, `92-122` | parámetros, pintado y consulta |
| `app/static/js/pages/buscar.js` | `191-246` | arranque y escuchadores |
| `app/static/js/api.js` | `16-17`, `50-92`, `214-226` | dirección base, petición y armado de la consulta |
| `app/routes/web_routes.py` | `90-108` | vista HTML del buscador |
| `app/routes/contenido_routes.py` | `37-100` | entrada del listado y parámetros |
| `app/routes/contenido_routes.py` | `162-177` | detalle público con sesión opcional |
| `app/controllers/contenido_controller.py` | `20-49`, `51-60` | valores por defecto y detalle |
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

---

## Guion

### [00:48] Acuerdo previo — 0:23

Antes de empezar, recuerdo que esto es la entrega del tercer corte. En el corte uno
definimos las entidades y las reglas; en el corte dos quedaron las pantallas. Hoy
esas pantallas ya no viven solas: el botón llama a una dirección de la API, esa
dirección consulta MySQL y la misma operación se puede ejecutar en Swagger. Los tres
usamos el mismo backend y las mismas credenciales. Yo voy a recorrer todo el proyecto
desde una sola acción: la búsqueda.

### [01:11] Mi botón: el campo de búsqueda (capa de presentación) — 1:02

**[PANTALLA: navegador en `http://localhost:5000/buscar` — señalar el campo de texto
rojo]**

Soy [NOMBRE] y hoy recorro el proyecto entero desde este botón: el campo de búsqueda
de /buscar. Es lo primero que ve el visitante, y es por acá por donde va a entrar
toda la explicación.

**[EDITOR: `app/templates/pages/buscar.html`, líneas 50 a 63]**

Este es el código del campo: un input con id `search-input`. Estamos en la **capa de
presentación**, el HTML. Esta capa solo muestra: no decide nada, no valida nada y no
habla con la base. Su trabajo es darle la forma al museo.

**[PANTALLA: señalar el resto de la página]**

En la misma plantilla están las otras piezas del botón. Los filtros de categoría y
año están en las líneas 93 a 132. El contador que arriba de la grilla dice «21
resultados encontrados» está en la línea 146, con id `search-count`. La cuadrícula
donde se pintan las tarjetas está en las líneas 190 a 193, con id `search-results`
—al abrir está vacía y oculta—; mientras carga se ve el esqueleto de las líneas 176
a 186. Y el botón «Limpiar filtros» está en la línea 216.

**[PANTALLA: escribir `proyecto` en el campo]**

Escribo «proyecto»: el contador pasa a «2 resultados encontrados» y la cuadrícula se
llena con dos tarjetas —Sistema de Monitoreo Ambiental con IoT y App para gestión de
notas—. Cada fila de la respuesta se convierte en tarjeta en
`app/static/js/pages/buscar.js`, líneas 41 a 54: título, año, imagen y autor.

**[EDITOR: `buscar.html`, líneas 11 a 17]**

Y arriba de la plantilla, en las líneas 11 a 17, el servidor inyecta las listas de
apoyo —categorías, años y slugs— para que los filtros no estén escritos a mano.

### [02:13] Quién prepara la página y quién escucha (vistas web + capa cliente) — 1:05

**[EDITOR: `app/routes/web_routes.py`, líneas 90 a 108]**

¿Quién entrega esta página? La capa de **vistas web**, que sirve los HTML. La función
`buscar`, en la línea 90, responde a `GET /buscar` y renderiza `pages/buscar.html`
con las listas de categorías y años y con la búsqueda inicial, si venía una en la
dirección. Concepto: esta ruta solo sirve el molde; los resultados todavía no salen
de acá.

**[EDITOR: `app/static/js/pages/buscar.js`, líneas 191 a 246]**

Cuando la página termina de cargar, entra la **capa cliente**, el JavaScript que
corre en el navegador. El buscador arranca en la línea 191, con el evento
`simul:ready`, y ahí se engancha todo: el campo escucha cada tecla —línea 203—, los
filtros laterales escuchan el clic —líneas 210 a 232—, y el botón limpiar
restablece todo —líneas 234 a 243—. En la línea 245 se hace la primera consulta,
para que al abrir ya aparezcan las 21 tarjetas.

Ojo con el concepto: el navegador no toca MySQL. Pide a la API y pinta lo que llega.

### [03:18] Del campo a la dirección: el viaje de la información — 0:52

**[EDITOR: `buscar.js`, líneas 56 a 69]**

Cada tecla llama a la función `buscar` —línea 92— y lo primero que hace es armar los
parámetros: el texto va en `q`, la categoría en `categoria`, el año en `anio`, y
`per_page` en 100 para traer todo de una vez.

**[EDITOR: `buscar.js`, líneas 92 a 122]**

Después `buscar` muestra el esqueleto de carga y llama a `SIMULApi.contenido(...)`.
Eso ya es una petición HTTP: el navegador está pidiendo, todavía no tiene nada.

**[EDITOR: `app/static/js/api.js`, líneas 214 a 226]**

`SIMULApi.contenido` está en `api.js`, línea 214: convierte los parámetros en texto
de dirección —`q=proyecto&anio=2023`— y arma `/contenido/` con ese sufijo.

**[EDITOR: `api.js`, línea 16 y líneas 50 a 92]**

Y en la línea 16 está la base de todo: `/api/museo`. La función `request`, líneas 50
a 92, hace el `fetch` contra `/api/museo/contenido/?q=...`, agrega el token si hay
sesión y devuelve el campo `data` de la respuesta. Concepto: esta es la única puerta
del navegador hacia el servidor; todas las pantallas del museo pasan por acá.

### [04:10] Capa 1 · Rutas — la puerta de entrada — 0:40

**[EDITOR: `app/routes/contenido_routes.py`, líneas 37 a 100]**

La petición cruzó la red y llegó al servidor. Entramos a la **capa de rutas**, la
puerta de entrada de la API. Acá, en la línea 37, está declarado
`GET /api/museo/contenido`: exactamente el mismo camino que acabamos de armar en el
navegador.

¿Qué hace esta capa y qué no? Recibe, lee los parámetros y valida —nada más. Fíjate
en los `Query`: el texto libre en la línea 47; el año, en las líneas 62 a 67, tiene
que ser como mínimo 1900 y como máximo 2100; el tamaño de página, en las líneas 79 a
84, entre 1 y 100. Si mando `anio=1800`, FastAPI corta acá mismo y responde 422
antes de que cualquier otra capa trabaje. La ruta no contiene reglas de negocio.

Un detalle de seguridad, en la línea 44: sesión opcional. El catálogo es público; si
el visitante trae token, se carga el usuario, y si no, sigue anónimo. Los formatos de
entrada y salida también tienen su capa de esquemas: `app/schemas/contenido_schema.py`,
líneas 109 a 121, declara el mismo rango de año para cuando se crea contenido. El
prefijo `/api/museo` está montado en `app/__init__.py`, líneas 216 a 219.

Y la función termina devolviendo `controller.listar(...)` con los siete argumentos
—líneas 92 a 100—. La información pasa a la siguiente capa.

### [04:50] Capa 2 · Controladores — coordinación y permisos — 0:30

**[EDITOR: `app/controllers/contenido_controller.py`, líneas 20 a 49]**

Segunda capa: **controladores**. Coordinan entre la ruta y el servicio; no hablan con
la base ni arman SQL. En la línea 20 está `listar`. Con la búsqueda hace tres cosas:
convierte los números, pone los valores por defecto —página 1 y doce elementos por
página, líneas 45 a 48— y aplica una regla de acceso: si alguien pide ver pendientes
o rechazados sin ser admin, responde 403 —líneas 31 a 37—. Para la búsqueda pública,
solo pasa el filtro al servicio.

### [05:20] Capa 3 · Servicios — las reglas del negocio — 0:40

**[EDITOR: `app/services/contenido_service.py`, líneas 74 a 105]**

Tercera capa: **servicios**, donde viven las reglas del negocio. `listar`, en la
línea 74, le pide al repositorio la página publicada —línea 85— y con lo que vuelve
arma la respuesta: `items`, `page`, `pages` y `total` —líneas 95 a 105—.

**[EDITOR: `contenido_service.py`, líneas 590 a 607]**

Cada fila se convierte en un resumen de tarjeta en la línea 590: id, tipo, título,
categoría, estado, fecha, año, imagen, descripción y autor. Es exactamente lo que
después pinta `buscar.js`. El servicio también calcula el año de cada subtipo
—líneas 863 a 929—, porque cada tipo lo guarda a su manera.

Y el formato de la respuesta, el sobre `{success, message, data}`, lo genera
`app/utils/response.py`, líneas 14 a 31: es el mismo sobre que consume el navegador.

### [06:00] Capa 4 · Repositorios — el único que habla con la base — 0:40

**[EDITOR: `app/repositories/contenido_repository.py`, líneas 75 a 115]**

Cuarta capa: **repositorios**, la única que consulta la tabla contenido. En la línea
75 está `get_publicados`. Primero filtra: solo estado `publicado` —líneas 86 a 88—.
Cuenta el total —línea 99—, ordena por fecha de creación —línea 103— y pagina de
forma explícita con `offset` y `limit` —líneas 104 y 105—. El sobre `Pagina`, en las
líneas 12 a 28, es el formato en el que suben los datos al servicio.

**[EDITOR: `contenido_repository.py`, líneas 380 a 459]**

Los filtros del botón están en `_aplicar_filtros`. El texto, líneas 389 a 398:
compara título o categoría sin importar mayúsculas —`ilike`—. Categoría y tipo,
líneas 400 a 410: coincidencia exacta. Y el año, líneas 412 a 457: cada subtipo
guarda el año a su manera —cuatro en columna `anio`, evento y noticia en su fecha—,
así que se pide una lista de identificadores con subconsultas. ¿Por qué no juntar
todas las tablas en un solo `join`? Porque la fila base se repetiría por cada
coincidencia y el total mentiría.

### [06:40] Capa 5 · Modelos — el espejo de la tabla en MySQL — 0:29

**[EDITOR: `app/models/contenido.py`, líneas 6 a 88]**

Quinta capa: **modelos**. La clase `Contenido` es el espejo en Python de la tabla
contenido: tipo con sus siete valores, título, categoría, estado con sus tres valores
—pendiente, publicado, rechazado— y la fecha de creación, con sus índices.

**[EDITOR: `db/DDL.sql`, líneas 94 a 118]**

Y el espejo real: la tabla en MySQL, en `db/DDL.sql`, línea 94, con sus claves
foráneas al autor y al validador. Los índices de búsqueda están en las líneas 108 a
111 —estado, tipo, categoría y fecha—. El año se guarda como `YEAR` de MySQL, en
`app/models/types.py`, líneas 6 a 28. Esta consulta no escribe nada: solo lee filas
publicadas.

### [07:09] La vuelta: de MySQL a la pantalla — 0:52

**[PANTALLA: navegador /buscar — escribir `proyecto` otra vez]**

La información vuelve por las mismas capas, en orden inverso. MySQL devuelve las
filas; el repositorio las convierte en objetos; el servicio arma el sobre con
`items`, `page`, `pages` y `total`; la ruta lo devuelve como JSON con el sobre
`{success, message, data}`; `api.js` entrega el campo `data`; y `buscar.js`, en la
línea 71, pinta la cuadrícula y actualiza el contador —líneas 81 a 85—.

**[PANTALLA: el contador dice «2 resultados encontrados»]**

Ahí está: el contador, que es el id `search-count` de `buscar.html` línea 146, dice
«2 resultados encontrados». Si escribo algo sin coincidencias, la grilla se oculta y
aparece el estado vacío con su botón «Limpiar filtros» —`buscar.html`, líneas 197 a
219—. Si la conexión falla, `buscar.js` muestra un aviso —líneas 114 a 118— y la
lista queda vacía.

**[EDITOR: `app/routes/contenido_routes.py`, líneas 162 a 177]**

Y para cerrar el círculo: al hacer clic en una tarjeta entra
`GET /api/museo/contenido/{id}`, en la línea 162 de las rutas —misma capa de
entrada—, y baja por controlador, línea 51, y servicio, línea 107, que devuelve 404
si el id no existe o si el contenido no está publicado —líneas 113 a 133—. La
sesión, si viene, solo sirve para marcar el favorito.

### [08:01] Swagger: la misma búsqueda, sin navegador — 0:44

**[PANTALLA: `http://localhost:5000/docs`]**

Ahora muestro que este mismo flujo existe sin mi pantalla: abro `/docs`, la
documentación que FastAPI genera sola.

**[ACCIONES: clic en `GET /api/museo/contenido/` → Try it out]**

Escribo `q=proyecto` y `anio=2023` y ejecuto: responde 200 con `items`, `page`,
`pages` y `total` —dos filas, las mismas que vio la pantalla—. Cambio el año a 1800
y ejecuto de nuevo: 422 con `details.query.anio`, que nombra el campo. Ese detalle
lo arma `app/__init__.py`, líneas 128 a 157.

**[ACCIONES: `GET /api/museo/contenido/{id}` con `id=1` → 200 con la ficha]**

Y en una pestaña nueva, `/openapi.json`: 30 rutas y 37 operaciones.

### [08:45] MySQL: las mismas filas — 0:51

**[PANTALLA: DBeaver, `127.0.0.1:3307`, base `simul_db`]**

Ahora bajo a la base de datos, la capa de abajo de todo. La búsqueda no escribe:
solo lee. Corro la consulta equivalente —está en VIDEO_3_PASOS, sección 4— y da
2 filas: ids 1 y 12, exactamente las mismas que devolvió Swagger. Con `SHOW INDEX`
confirmo los índices de estado, tipo, categoría y fecha que acabo de señalar en el
DDL. Y al final del DDL, líneas 433 a 464, están las dos vistas,
`v_bandeja_validacion` y `v_ranking`: consultas guardadas, no tablas nuevas.

### [09:36] Arquitectura, FastAPI y Docker — 0:33

**[EDITOR: `app/__init__.py`, líneas 208 a 239]**

El recorrido de capas cerró. Acá están los `include_router`: el de páginas web y los
seis de la API con el prefijo `/api/museo`. Siete capas arriba —rutas, controladores,
servicios, repositorios, modelos, esquemas y utilidades— y abajo 25 tablas y 2 vistas
en `db/DDL.sql`, de la línea 19 a la 464.

El criterio tres de la rúbrica pide FastAPI con Swagger: está, porque FastAPI genera
la documentación OpenAPI sola. ¿Por qué FastAPI y no Flask? Porque FastAPI trae la
validación de parámetros y la documentación incluidas, que es justo lo que este
corte evalúa. En `docker-compose.yml`, líneas 14 a 24 y 27 a 44, la app corre en el
puerto 5000 y MySQL en el 3307, con el DDL como script inicial. Coherencia total con
los cortes uno y dos: mismas entidades, mismas pantallas, mismas credenciales.

### [10:09] Seguridad — 0:29

**[PANTALLA: Swagger, sin tocar Authorize]**

Seguridad. El listado es público: lo vimos, 200 sin token. Lo personal pide token.
Ejecuto `GET /gamificacion/mi-historial` sin Authorize: 401. Hago login con el
admin, copio el token, lo pego en Authorize —sin la palabra `Bearer`— y repito:
200. Las claves se guardan como huella en `app/utils/security.py`, líneas 30 a 85,
y nunca salen en la respuesta. La sesión obligatoria y la opcional están en
`app/utils/roles.py`, líneas 191 y 195.

### [10:38] Pruebas — 0:26

En la terminal, con el entorno activado, `pytest -q` da 19 pruebas en una base
temporal, sin tocar MySQL. En `tests/test_app.py`, líneas 20 a 39, está la prueba de
que la documentación OpenAPI responde; y en 511 a 525, la de los catálogos de
búsqueda.

### [11:04] Cierre — 0:26

Cierro con los seis criterios de la rúbrica: arquitectura por capas; MySQL con 25
tablas y 2 vistas; API REST con los cinco métodos —GET, POST, PUT, PATCH y DELETE— y
Swagger con 30 rutas y 37 operaciones; reglas, validaciones y seguridad —422, 401,
403—; pruebas en Swagger, Docker y 19 pruebas automatizadas; y coherencia entre los
tres cortes. Todo lo viste pasar por un solo botón: el de buscar. Termino aquí.

---

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
