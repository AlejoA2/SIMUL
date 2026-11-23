# Video 1 — «Aprobar y publicar» (10 min)

**Integrante 1.** Ancla única: aprobación del administrador.
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
| `app/static/js/api.js` | `50-92`, `105-121` | petición HTTP, consulta de la bandeja y llamada de aprobación |
| `app/static/js/pages/admin_validacion.js` | `156-159` | botón creado con `data-approve` |
| `app/static/js/pages/admin_validacion.js` | `197-223` | acción al hacer clic |
| `app/static/js/pages/admin_validacion.js` | `347-356` | captura del clic |
| `app/routes/validacion_routes.py` | `47-68` | entrada de la operación |
| `app/controllers/validacion_controller.py` | `41-52`, `96-113` | controlador y llamada al servicio |
| `app/services/validacion_service.py` | `32`, `80-160` | valor de puntos y regla principal |
| `app/services/validacion_service.py` | `249-277` | comprobaciones de permiso y estado |
| `app/services/validacion_service.py` | `306-326` | nivel e insignias |
| `app/repositories/contenido_repository.py` | `58-63` | lectura del contenido |
| `app/repositories/validacion_repository.py` | `36-44` | escritura del registro |
| `app/models/contenido.py` | `6-45` | campos de estado y validador |
| `app/models/historial_puntos.py` | `6-40` | movimiento de puntos |
| `app/models/usuario.py` | `136-139` | nombre del rol |
| `app/schemas/simul_auth_schema.py` | `91-112` | datos de usuario que se devuelven |
| `tests/test_app.py` | `433-463` | prueba de esta operación |

Más los archivos comunes del apartado 3 de `00_ANTES_DE_GRABAR.md`.

## Guion

### [0:00] Acuerdo previo — 1:00

> "Me voy a la pantalla de inicio antes de empezar: es la entrega del corte 2. La sesión se guarda en el navegador, pero las acciones ya están conectadas: el botón llama a la API, la API guarda en MySQL y la misma operación se prueba en Swagger. Arrancamos en Flask y pasamos a FastAPI, que genera la documentación solo. Los tres diremos lo mismo."

### [1:00] Presentación — 0:15

> "Me voy a `/admin/validacion`, con la sesión de administrador abierta. Soy **[NOMBRE]** y voy a usar el botón **«Aprobar y publicar»** para explicarles **todo el proyecto**: cómo está armado, cómo guarda, cómo se prueba y cómo se conecta con los cortes anteriores."

### [1:15] Capa visual — 1:00

> "Me voy al editor, a `app/templates/pages/admin_validacion.html`, líneas 50 a 60, para ver el contador, y a la línea 94, donde se dibuja la lista. Abro `app/static/js/pages/admin_validacion.js`, líneas 156 a 159: el botón se crea con `data-approve`. Entre 197 y 223 está la acción: llama a la API, vuelve a consultar la bandeja y muestra el aviso. Me voy a `app/static/js/api.js`, líneas 113 a 121, para ver la llamada `POST /validacion/{id}/aprobar`. Hago clic y el contador baja porque la API ya guardó el cambio."

### [2:15] De la pantalla al servidor — 0:45

> "Ahora me voy a `app/routes/validacion_routes.py`, líneas 47 a 68. Ahí entra `POST /api/museo/validacion/{id}/aprobar`: pide sesión iniciada y las observaciones son opcionales; sin token, responde **401**. Sigo en `app/controllers/validacion_controller.py`, líneas 41 a 52 y 96 a 113: el controlador reconoce al usuario y llama a la parte que contiene la regla. El permiso de administrador no se comprueba aquí, sino más adentro, para que no se pueda saltar."

### [3:00] La regla de negocio — 1:15

> "Me voy a `app/services/validacion_service.py`. La línea 32 fija los **100 puntos**; entre 80 y 160 está la regla; entre 249 y 277, las comprobaciones; y entre 306 y 326, el nivel y las insignias. Si quien decide no es administrador, **403**; si no existe, **404**; y si ya no está pendiente, **409**. Después, en un solo paso: estado publicado, quién lo hizo y cuándo, una fila en el registro, aviso al autor, 100 puntos y nivel actualizado. O se hace todo, o no se hace nada."

### [4:15] Datos y respuesta — 1:00

> "Me voy a `app/repositories/contenido_repository.py`, líneas 58 a 63, y a `app/repositories/validacion_repository.py`, líneas 36 a 44: uno lee el contenido y el otro escribe el registro, sin confirmar por su cuenta. En `app/models/contenido.py`, 6 a 45, y en `app/models/historial_puntos.py`, 6 a 40, están los campos que se tocan. En `app/static/js/api.js`, líneas 50 a 92, se ve cómo se envía el token y se lee la respuesta. En Swagger aparece **200** con el contenido publicado y el validador, nunca la contraseña. La app confirma al terminar; si falla, deshace."

### [5:15] Persistencia — 1:00

> "Me voy a DBeaver y ejecuto una consulta por una: el contenido con su estado y los puntos del autor, la fila del registro de decisiones y el movimiento de **más 100 puntos**. Si los tres aparecen, no es solo una respuesta bonita: quedó guardado."

### [6:15] Arquitectura y base de datos — 1:00

> "Me voy a `app/__init__.py`, líneas 208 a 238. El backend está en **siete partes**: entrada, orden del trabajo, reglas, consulta a la base, modelos, formatos y utilidades. En `db/DDL.sql`, líneas 94 a 118 y 355 a 408, están las tablas; entre 433 y 464, las dos vistas. Son **25 tablas y 2 vistas**, con índices en las columnas más usadas. El SQL se entrega a MySQL al crear el contenedor, igual al diagrama del corte 2. En DBeaver: `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`."

### [7:15] API REST y evidencia — 1:00

> "Me voy al navegador, a `/docs` y `/openapi.json`. Bajo `/api/museo` hay **30 rutas y 37 operaciones** de ingreso, contenido, validación, puntos, administración y museo, con los cinco métodos y respuestas 200, 201, 401, 403, 404, 409 y 422. Los errores traen siempre el mismo formato; el 422 señala el campo y un fallo interno solo muestra un mensaje general. Al ejecutar desde `/docs` veo código y cuerpo: esa es la evidencia."

### [8:15] Seguridad — 0:30

> "Me voy a `app/static/js/pages/login.js`, líneas 117 a 150: la página envía correo y clave, recibe el token y lo guarda para las siguientes peticiones. En `app/utils/security.py`, líneas 23 a 46 y 49 a 85, la contraseña se guarda como huella con valor aleatorio, nunca en texto plano. En `app/utils/roles.py`, línea 191, está la sesión; en `app/models/usuario.py`, 136 a 139, el rol. Los datos devueltos, en `app/schemas/simul_auth_schema.py`, 91 a 112, no incluyen la contraseña."

### [8:45] Pruebas, Docker y coherencia — 0:45

> "Me voy a la terminal: `pytest -q` da **19 pruebas** en una base temporal, sin tocar MySQL. En `docker-compose.yml`, líneas 14 a 24 y 27 a 44, se ve la app en el puerto 5000 y la base en el 3307 con el SQL inicial. Los requisitos del corte 1, las pantallas del corte 2 y este servicio usan las mismas entidades y nombres."

### [9:30] Cierre — 0:30

> "Me voy de nuevo a `/docs` y a la tarjeta. Los **6 criterios**: siete partes, MySQL con 25 tablas y 2 vistas, API con Swagger, reglas y permisos, evidencia en Swagger, Docker y 19 pruebas, y coherencia entre los tres cortes. Termino aquí."

## Respaldo (no leer)

```sql
SELECT c.id_contenido, c.titulo, c.estado, c.fec_valid, u.puntos_total
FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
WHERE c.id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT puntos, motivo FROM historial_puntos
WHERE id_contenido = <ID> ORDER BY fecha DESC;
```

- Los niveles van por rangos de puntos y la insignia se da al superar el umbral.
- Quien consulta no guarda; guarda la parte que contiene la regla.

**Preguntas propias de este botón:** ¿un docente puede decidir? → 403.
¿Cómo sabés que son 100? → valor fijo en el servicio y fila en el historial.
¿Dónde queda el motivo? → en el contenido y en el registro de decisiones.
¿Se puede decidir dos veces? → 409.
