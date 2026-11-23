# Video 2 — «Rechazar» (12 min)

**Integrante 2.** Ancla única: el rechazo. Todo el proyecto se recorre desde ese botón.

Leé antes `00_ANTES_DE_GRABAR.md` para Docker, credenciales y acuerdo.

## Guion

### [00:48] Acuerdo previo — 0:48

> "Antes de empezar, recuerdo que esto es la entrega del tercer corte. En el corte uno definimos las entidades y las reglas; en el corte dos quedaron las pantallas. Hoy esas pantallas ya no viven solas: el botón llama a una dirección `/api/museo`, esa dirección guarda en MySQL y la misma operación se ejecuta en Swagger. Los tres usamos el mismo backend y las mismas credenciales. Yo voy a recorrer todo el proyecto desde una sola acción: el rechazo."

### [01:14] Presentación — 0:26

> "Me voy a `/admin/validacion` con la sesión del administrador abierta. Soy **[NOMBRE]**. Acá está el botón **«Rechazar»**. Voy a usarlo para mostrarles el proyecto entero: la pantalla, la API, MySQL, Swagger, las pruebas y cómo se conecta con los cortes uno y dos."

### [02:50] La pantalla y el botón — 1:36

> "Me voy al editor, a `app/templates/pages/admin_validacion.html`, líneas 7 a 9 y 50 a 60: ahí está el contador y el armado de la página. En la línea 94 se dibuja la lista. Abro `app/static/js/pages/admin_validacion.js`, líneas 160 a 163: el botón se crea con `data-reject` y dice «Rechazar». Entre 229 y 260 está la ventana del motivo, con el aviso de al menos cinco caracteres. Entre 262 y 309 está la acción: tomo el texto, lo limpio y llamo a `SIMULApi.rechazar`. En `app/static/js/api.js`, líneas 204 a 212, esa llamada es `POST /api/museo/validacion/{id}/rechazar` con `observaciones`. La captura del clic está en 347 a 356. Vuelvo a la pantalla: aprieto **Rechazar** en el contenido 13, escribo el motivo «Falta la evidencia fotográfica», confirmo, y el contador baja de 6 a 5. Ese clic ya escribió en MySQL; ahora les muestro la misma llamada desde Swagger."

### [03:48] Entrada, formato y sesión — 0:58

> "Me voy a `app/routes/validacion_routes.py`, líneas 71 a 91: ahí entra `POST /api/museo/validacion/{id}/rechazar`. El cuerpo trae `observaciones`. La ruta pide sesión; sin token responde **401**. El ingreso real está en `POST /api/museo/auth/login`: `app/routes/simul_auth_routes.py`, 51 a 61. En Swagger pongo el correo `l.jimenez@unilibre.edu.co` y la clave `1234`; el servicio, en `app/services/usuario_service.py`, 105 a 143, devuelve el token. En `app/static/js/api.js`, 129 a 138, ese token queda guardado en el navegador y viaja en cada petición."

### [04:43] La bandeja real — 0:55

> "Antes de rechazar, me voy a `GET /api/museo/validacion/bandeja`. La ruta está en `app/routes/validacion_routes.py`, 30 a 40; el controlador, en `app/controllers/validacion_controller.py`, 16 a 39; la consulta, en `app/repositories/validacion_repository.py`, 11 a 21. Responde **200** con seis pendientes: los ids 7, 13, 14, 15, 16 y 17. Es lo mismo que muestra la vista `v_bandeja_validacion`, en `db/DDL.sql`, 433 a 448. Tras el clic en el 13, la fila salió de la bandeja y el contador bajó de 6 a 5."

### [05:39] El motivo se revisa dos veces — 0:56

> "El motivo se revisa dos veces. En la ventana, `app/static/js/pages/admin_validacion.js`, 275 a 282, menos de cinco caracteres ni sale. En `app/schemas/contenido_schema.py`, 174 a 186, `observaciones` va de 5 a 1000. En Swagger, con `{}`, aparece **422** y el detalle nombra el campo `observaciones`. Ese mensaje se arma en `app/__init__.py`, 128 a 157. Si pongo cinco espacios, el formato los cuenta, pero la regla los limpia en `app/services/validacion_service.py`, 278 a 289, y vuelve el **422** por motivo obligatorio. Esa es la segunda revisión."

### [06:29] Las siete capas — 0:50

> "Me voy a `app/__init__.py`, 208 a 239: ahí se enganchan los routers con el prefijo `/api/museo`. El proyecto tiene siete capas. Uno, entrada: `app/routes/validacion_routes.py`. Dos, orden del trabajo: `app/controllers/validacion_controller.py`. Tres, reglas: `app/services/validacion_service.py`. Cuatro, acceso a datos: `app/repositories/validacion_repository.py`. Cinco, modelos: `app/models/contenido.py`, `validacion_log.py` y `notificacion.py`. Seis, formatos: `app/schemas/contenido_schema.py` y `simul_auth_schema.py`. Siete, utilidades: `app/utils/roles.py`, `response.py` y `security.py`."

### [07:24] La regla y los errores — 0:55

> "Me voy a `app/services/validacion_service.py`, 162 a 214: la regla pone el estado `rechazado`, guarda quién decidió con `id_validador`, la fecha en `fec_valid` y el motivo en `observaciones`. Escribe la fila en `validacion_log` con `accion='rechaza'` y avisa al autor. Todo se confirma junto; si algo falla, se deshace. Acá no hay movimiento de puntos. Sin sesión da **401**; en 249 a 277 están el **403**, el **404** y el **409**; el **422** ya lo vimos por el motivo. La comprobación de administrador está adentro, así no se puede saltar."

### [08:26] Historial y aviso al autor — 1:02

> "Me voy a `GET /api/museo/validacion/{id}/historial`. En la ruta, `app/routes/validacion_routes.py`, 98 a 108, solo se pide sesión. Pero en `app/controllers/validacion_controller.py`, 67 a 90, la línea 83 exige rol de administrador: en Swagger, con un estudiante da **403** y con el admin da **200**. El servicio lee el registro en `app/services/validacion_service.py`, 220 a 243, y el repositorio en `app/repositories/validacion_repository.py`, 23 a 34. El autor, mientras tanto, lee el motivo en `GET /api/museo/contenido/mis-aportes`, `app/routes/contenido_routes.py`, 107 a 118, y `app/services/contenido_service.py`, 139 a 162."

### [09:30] Swagger y OpenAPI — 1:04

> "Me voy al navegador, a `/docs`. Ubico `POST /api/museo/validacion/{id}/rechazar`, doy «Try it out» y trabajo sobre el id 14, otro pendiente de la cola. Primero dejo `{}`, **422** con el nombre del campo. Después escribo un motivo válido, por ejemplo «Falta la evidencia fotográfica», y sale **200** con el estado rechazado. Es la misma llamada que hizo el botón, pero escrita a mano; el 13 ya quedó rechazado desde la pantalla. Luego ejecuto `GET /api/museo/validacion/14/historial`: **200**, con la fila nueva. Abro `/openapi.json` y digo la cifra: **30 rutas y 37 operaciones**. Esa es la evidencia de la API."

### [10:44] DBeaver, base y Docker — 1:14

> "Me voy a DBeaver, a `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`. Primera consulta: `contenido` 13 debe tener `estado='rechazado'`, `observaciones` con el motivo, `id_validador=5` y `fec_valid` con fecha. Segunda: en `validacion_log` hay una fila nueva con `accion='rechaza'`, `id_admin=5`, `id_contenido=13`, fecha y motivo. Tercera: en `notificacion` hay una fila para el autor con el mensaje del contenido rechazado. En `db/DDL.sql` están las **25 tablas y 2 vistas**, con índices en estado, tipo y usuario. En `docker-compose.yml`, 14 a 24 y 27 a 44, la app está en el puerto 5000 y MySQL en el 3307; el DDL entra como script inicial. Las entidades y nombres son los mismos de los cortes uno y dos."

### [11:49] Seguridad y pruebas — 1:05

> "Me voy a `app/utils/security.py`, 23 a 46 y 49 a 85: la clave se guarda como huella con valor aleatorio y se compara de forma segura. En `app/utils/roles.py`, 47 a 65, se emite el token; en 170 a 175, sin token hay **401**. Los roles se leen en `app/models/usuario.py`, 136 a 139, y la respuesta, en `app/schemas/simul_auth_schema.py`, 96 a 120, no incluye la clave. En la terminal ejecuto `pytest -q`: **19 pruebas** en una base temporal. En `tests/test_app.py`, 323 a 358, está la prueba del motivo; en 361 a 375, la del permiso del historial."

### [12:24] Cierre — 0:35

> "Me voy de nuevo a `/docs` y a la ventana del motivo. Los **6 criterios**: siete capas; MySQL con 25 tablas y 2 vistas; API con Swagger de 30 rutas y 37 operaciones; reglas y permisos; evidencia en Swagger, Docker y 19 pruebas; y coherencia entre los tres cortes. Arranco por el rechazo, recorro todo y termino acá."

## Respaldo (no leer)

```sql
SELECT id_contenido, titulo, estado, observaciones, id_validador, fec_valid
FROM contenido WHERE id_contenido = 13;
-- esperado: estado='rechazado', observaciones con el motivo,
-- id_validador=5, fec_valid con fecha

SELECT id_log, accion, observaciones, fecha_decision, id_admin, id_contenido
FROM validacion_log WHERE id_contenido = 13 ORDER BY fecha_decision DESC;
-- esperado: fila nueva con accion='rechaza', id_admin=5,
-- id_contenido=13, fecha y motivo

SELECT id_notif, id_usuario, tipo, mensaje, fecha_envio
FROM notificacion WHERE id_contenido = 13 ORDER BY fecha_envio DESC;
-- esperado: fila para el autor, tipo='rechazado'
-- y mensaje del contenido rechazado
```

**Preguntas propias de este botón**

- ¿422 o 400? → 422: es validación del campo `observaciones`.
- ¿Por qué dos revisiones del motivo? → la ventana responde al instante; el formato y la regla cubren el resto.
- ¿Quién puede ver el historial? → solo administrador; con estudiante, 403.
- ¿Por qué no hay puntos? → esa regla no forma parte del rechazo.
- ¿Qué pasa si repito la operación? → 409: ya no está pendiente.
