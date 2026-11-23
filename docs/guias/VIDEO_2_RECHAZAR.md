# Video 2 — «Rechazar» (10 min)

**Integrante 2.** Ancla única: rechazo con motivo obligatorio.
**No mencionar** los otros dos botones en ningún momento. Recorre todo el proyecto a
través de este botón.

Leé antes [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md) (Docker, credenciales y
acuerdo previo).

## Antes de iniciar a grabar

Tener abiertos estos archivos en el editor, exactamente en estas líneas:

| Archivo | Líneas | Qué vas a señalar |
|---|---|---|
| `app/templates/pages/admin_validacion.html` | `8`, `50-60`, `94` | datos de la cola, contador y lista |
| `app/static/js/pages/login.js` | `117-150` | inicio de sesión contra la API y guardado del token |
| `app/static/js/api.js` | `50-92`, `204-212` | petición HTTP y llamada de rechazo con el motivo |
| `app/static/js/pages/admin_validacion.js` | `160-163` | botón creado con `data-reject` |
| `app/static/js/pages/admin_validacion.js` | `229-260` | ventana para escribir el motivo |
| `app/static/js/pages/admin_validacion.js` | `262-309` | acción al confirmar |
| `app/static/js/pages/admin_validacion.js` | `347-356` | captura del clic |
| `app/schemas/contenido_schema.py` | `174-186` | motivo obligatorio de 5 a 1000 caracteres |
| `app/routes/validacion_routes.py` | `71-91` | entrada de la operación |
| `app/routes/validacion_routes.py` | `98-108` | consulta del historial |
| `app/controllers/validacion_controller.py` | `54-65` | acción del controlador |
| `app/controllers/validacion_controller.py` | `67-90`, `96-105`, `115-119` | historial y comprobación de rol |
| `app/services/validacion_service.py` | `162-219` | regla principal |
| `app/services/validacion_service.py` | `220-248` | lectura del historial |
| `app/services/validacion_service.py` | `249-277` | comprobaciones de permiso y estado |
| `app/services/validacion_service.py` | `278-290` | limpieza del motivo |
| `app/services/validacion_service.py` | `291-304` | aviso al autor |
| `app/repositories/validacion_repository.py` | `23-35` | lectura del registro |
| `tests/test_app.py` | `323-360`, `361-377` | motivo obligatorio y permiso |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [0:00] Acuerdo previo — 1:00

> "Me voy a la pantalla de inicio antes de empezar: es la entrega del corte 2. La sesión se guarda en el navegador, pero las acciones ya están conectadas: el botón llama a la API, la API guarda en MySQL y la misma operación se prueba en Swagger. Arrancamos en Flask y pasamos a FastAPI, que genera la documentación solo. Los tres diremos lo mismo."

### [1:00] Presentación — 0:15

> "Me voy a `/admin/validacion`, con la sesión de administrador abierta y una tarjeta pendiente visible. Soy **[NOMBRE]** y voy a usar el botón **«Rechazar»** para explicarles **todo el proyecto**: cómo está armado, cómo guarda, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

> "Me voy al editor, a `app/templates/pages/admin_validacion.html`, líneas 50 a 60 y 94, para ver el contador y la lista. Abro `app/static/js/pages/admin_validacion.js`, líneas 160 a 163: el botón se crea con `data-reject`. Entre 229 y 260 está la ventana para escribir el motivo y entre 262 y 309 la acción al confirmar. Hago clic y dejo el motivo vacío para que aparezca el aviso rojo. La pantalla pide al menos cinco caracteres y la API vuelve a exigirlos. Me voy a `app/static/js/api.js`, líneas 204 a 212: el motivo viaja en la petición y la bandeja se refresca con lo que hay en MySQL."

### [2:15] De la pantalla al servidor — 0:30

> "Me voy a `app/routes/validacion_routes.py`, líneas 71 a 91: entra `POST /api/museo/validacion/{id}/rechazar`, pide sesión iniciada y el cuerpo debe traer `observaciones`. En `app/schemas/contenido_schema.py`, 170 a 182, se exigen entre **5 y 1000 caracteres**; en Swagger se ve en el *Request body*. El controlador reconoce al usuario y pasa los datos a la parte que contiene la regla."

### [3:00] Validación y respuesta 422 — 0:45

> "Me voy a Swagger y dejo el cuerpo vacío, con `{}`: aparece **422** con el detalle del campo. Después me voy a `app/__init__.py`, líneas 128 a 158, donde se arma ese mensaje con el nombre del campo que falló. La comprobación ocurre antes de entrar a la regla, por eso es 422 y no 400."

### [3:45] La regla de negocio — 1:15

> "Me voy a `app/services/validacion_service.py`, líneas 162 a 219. Las comprobaciones están en 249 a 277: **403** si no es administrador, **404** si no existe, **409** si ya no está pendiente. Entre 278 y 290 se limpia el texto: cinco espacios cuentan cinco caracteres, pero al quitarlos queda vacío y también da **422**. Luego se guarda el estado rechazado, quién decidió, cuándo y el motivo, la fila en el registro y el aviso al autor, todo de una vez. La regla de puntos no interviene en esta decisión. Si repito la identificación, aparece el **409**."

### [5:00] Auditoría y seguridad — 1:15

> "Me voy a Swagger y ejecuto `GET /api/museo/validacion/{id}/historial`. Después me voy a `app/controllers/validacion_controller.py`, líneas 67 a 90, y señalo la 83: aunque la ruta solo pide sesión, el controlador exige rol de administrador y da **403** si no. Paso por `app/services/validacion_service.py`, 220 a 248, y por `app/repositories/validacion_repository.py`, 23 a 35: ahí se lee el registro. En `app/utils/security.py`, 23 a 46 y 49 a 85, la contraseña se guarda como huella con valor aleatorio; los datos devueltos no la incluyen."

### [6:15] Arquitectura y base de datos — 1:00

> "Me voy a `app/__init__.py`, líneas 208 a 238. El backend está en **siete partes**: entrada, orden del trabajo, reglas, consulta a la base, modelos, formatos y utilidades. En `db/DDL.sql`, líneas 375 a 408, está el registro de decisiones y el historial de puntos; entre 433 y 464, las dos vistas. Son **25 tablas y 2 vistas**, con índices en las columnas más usadas. El SQL se entrega a MySQL al crear el contenedor, igual al diagrama del corte 2. En DBeaver: `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`."

### [7:15] API REST y evidencia — 1:00

> "Me voy al navegador, a `/docs` y `/openapi.json`. Bajo `/api/museo` hay **30 rutas y 37 operaciones** de ingreso, contenido, validación, puntos, administración y museo, con los cinco métodos y respuestas 200, 201, 401, 403, 404, 409 y 422. Los errores traen siempre el mismo formato; el 422 señala el campo y un fallo interno solo muestra un mensaje general. En `/docs`, con el cuerpo vacío veo el **422** y con un motivo válido el **200**: esa es la evidencia."

### [8:15] Seguridad — 0:30

> "Me voy a `app/static/js/pages/login.js`, líneas 117 a 150: la página pide el token y lo guarda para las siguientes peticiones. En `app/utils/roles.py`, línea 191, está la comprobación de sesión. En `app/models/usuario.py`, 136 a 139, se lee el rol; en `app/schemas/simul_auth_schema.py`, 91 a 112, los datos devueltos no incluyen la contraseña. La huella con valor aleatorio está en `app/utils/security.py`, 23 a 46 y 49 a 85."

### [8:45] Pruebas, Docker y coherencia — 0:45

> "Me voy a la terminal: `pytest -q` da **19 pruebas** en una base temporal, sin tocar MySQL. En `tests/test_app.py`, 323 a 377, están las del motivo obligatorio y del permiso para ver el historial. En `docker-compose.yml`, 14 a 24 y 27 a 44, se ve la app en el puerto 5000 y la base en el 3307 con el SQL inicial. Los requisitos del corte 1, las pantallas del corte 2 y este servicio usan las mismas entidades y nombres."

### [9:30] Cierre — 0:30

> "Me voy de nuevo a `/docs` y a la ventana del motivo. Los **6 criterios**: siete partes, MySQL con 25 tablas y 2 vistas, API con Swagger, reglas y permisos, evidencia en Swagger, Docker y 19 pruebas, y coherencia entre los tres cortes. Termino aquí."

## Respaldo (no leer)

```sql
SELECT id_contenido, titulo, estado, observaciones, fec_valid, id_validador
FROM contenido WHERE id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT id_notificacion, tipo, mensaje FROM notificacion
WHERE id_contenido = <ID> ORDER BY fecha_envio DESC;
```

- Doble revisión del motivo: la pantalla responde al instante, la API exige el
  formato y la regla limpia los espacios en blanco.
- La bandeja solo muestra lo pendiente; al rechazar, la fila sale de ahí y el autor
  lee el motivo en «Mis aportes».

**Preguntas propias de este botón:** ¿422 o 400? → 422 es validación del contenido.
¿No es redundante revisar tres veces? → cada capa cubre un caso distinto.
¿Quién lee el motivo? → el autor en «Mis aportes» y el administrador en el historial.
¿Quién ve el historial? → solo administrador, 403 si no. ¿Por qué no hay puntos? →
la regla de puntos no forma parte de esta decisión.
