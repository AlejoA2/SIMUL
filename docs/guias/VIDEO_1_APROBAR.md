# Video 1 — Aprobar y publicar (12 min)

Guion para leer en voz alta. Un solo ancla: la aprobación. Los tiempos son acumulados.

### [00:48] Acuerdo previo — 0:48

> "Antes de empezar, recuerdo que esto es la entrega del tercer corte. En el corte uno definimos las entidades y las reglas; en el corte dos quedaron las pantallas. Hoy esas pantallas ya no viven solas: el botón llama a una dirección `/api/museo`, esa dirección guarda en MySQL y la misma operación se ejecuta en Swagger. Los tres usamos el mismo backend y las mismas credenciales. Yo voy a recorrer todo el proyecto desde una sola acción: la aprobación."

### [01:10] Presentación — 0:22

> "Estoy en `http://localhost:5000/admin/validacion`, con la sesión abierta. Soy **[NOMBRE]**. Acá está el botón **Aprobar y publicar**. Con esa sola acción recorro la pantalla, la API, las reglas, la base, Swagger y las pruebas."

### [02:50] La capa visual — 1:40

> "Me voy al editor. En `app/templates/pages/admin_validacion.html`, líneas 50 a 60, está el contador: en la 59 sale el número que viene del servidor y en la 94, el contenedor de la lista. Abro `app/static/js/pages/admin_validacion.js`: entre 41 y 68 la bandeja se pide a la API; entre 155 y 159 se dibuja el botón **Aprobar y publicar** con su identificador; entre 197 y 223 está la acción, que llama a la API, avisa y vuelve a cargar la bandeja; entre 348 y 354 el clic se captura en el contenedor. Y en `app/static/js/api.js`, líneas 194 a 202, esa acción se convierte en `POST /api/museo/validacion/{id}/aprobar`, con observaciones opcionales. Vuelvo a la pantalla, con 6 pendientes, y hago clic en **Aprobar y publicar** del contenido 7. El aviso confirma, la tarjeta desaparece y el contador baja a 5. Ese clic ya escribió en MySQL; ahora les muestro la misma llamada desde Swagger."

### [04:03] Ingreso real y bandeja — 1:13

> "Antes de esa llamada necesito sesión. En `app/static/js/pages/login.js`, líneas 117 a 153, la pantalla manda correo y clave a `POST /api/museo/auth/login`. Uso `l.jimenez@unilibre.edu.co` y clave `1234`, las credenciales del administrador 5. En `app/static/js/api.js`, líneas 129 a 138 y 19 a 28, el token que devuelve el servidor se guarda en el navegador, en `simul.token`, y de ahí sale en cada petición. Sin ese token, la puerta responde 401. Con la sesión puesta, abro `GET /api/museo/validacion/bandeja`: responde 200 con 6 pendientes, los ids 7, 13, 14, 15, 16 y 17. Tras el clic que acabo de hacer, esa misma consulta da 5."

### [05:23] Las siete capas — 1:20

> "Me voy a `app/__init__.py`, líneas 208 a 239, donde se enganchan los routers con el prefijo `/api/museo`. Adentro hay siete capas. Entrada: `app/routes/validacion_routes.py`, 47 a 68. Orden del trabajo: `app/controllers/validacion_controller.py`, 41 a 52 y 96 a 113. Reglas: `app/services/validacion_service.py`, 80 a 156. Acceso a datos: `app/repositories/validacion_repository.py`, 11 a 40, y `contenido_repository.py`, 68 a 73. Modelos: `app/models/contenido.py`, 55 a 88; `historial_puntos.py`, 21 a 48; `validacion_log.py`, 20 a 51. Formatos: `app/schemas/contenido_schema.py`, 165 a 171 y 232 a 253, y `simul_auth_schema.py`, 53 a 58 y 96 a 120. Utilidades: `app/utils/roles.py`, 47 a 65 y 101 a 111; `response.py`, 14 a 59; y `security.py`, 23 a 85."

### [06:34] La regla de negocio — 1:11

> "Entro a la regla. En `app/services/validacion_service.py`, línea 32, el premio es fijo: 100 puntos. Entre 80 y 156 pasa todo: el contenido queda en estado publicado, se guarda quién decide —el id 5— y cuándo; se escribe la fila de decisión con acción `aprueba`; se avisa al autor; se suman los 100 puntos con el motivo de la publicación; y se recalculan nivel e insignias entre 306 y 326. Antes, entre 249 y 276, se comprueban el permiso y el estado. Sin sesión, 401; si quien decide no es administrador, 403; si el contenido no existe, 404; si ya salió de la bandeja, 409. Todo se confirma junto: si algo falla, no queda a medias."

### [07:56] Swagger, la prueba en vivo — 1:22

> "Ahora sí, al navegador: `http://localhost:5000/docs`. Ubico `POST /api/museo/validacion/{id}/aprobar`, toco **Try it out**, pongo el id 13 —otro pendiente de la misma cola— y ejecuto. Arriba, en **Authorize**, pegué el token que dio el ingreso, sin la palabra Bearer. La respuesta es 200 y el cuerpo trae el contenido publicado y el validador, con nombre e id; nunca la clave. Es la misma llamada que hizo el botón, pero escrita a mano. Después abro `http://localhost:5000/openapi.json`: hay 30 rutas y 37 operaciones, con respuestas 200, 201, 401, 403, 404, 409 y 422. Para cerrar el círculo, ejecuto `GET /api/museo/contenido/{id}` con el 7 y lo veo publicado. Y vuelvo a la bandeja: el contador quedó en 4, uno por el clic y otro por Swagger."

### [08:45] La huella en MySQL — 0:49

> "Me voy a DBeaver, en `127.0.0.1:3307`, base `simul_db`, y refresco. Primero, el contenido 7: `estado=publicado`, `id_validador=5`, `fec_valid` con fecha, y su autora Valentina con `puntos_total=1340`, antes 1240. Segundo, `validacion_log`: una fila con `accion='aprueba'`, `id_admin=5`, `id_contenido=7` y su fecha. Tercero, `historial_puntos`: una fila con `puntos=100`, `id_usuario=1`, `id_contenido=7` y el motivo `Publicación en el museo: Propuesta: Sistema Blockchain para Titulos Academicos`. Las tres consultas están al final, por si quieren repetirlas."

### [09:40] Arquitectura y base — 0:55

> "Un paso más atrás. `docker-compose.yml`, líneas 14 a 24, levanta la app en el puerto 5000; entre 27 y 44, MySQL 8.4 en el 3307, con `db/DDL.sql` montado como script inicial. En `db/DDL.sql`, entre 19 y 424 están las 25 tablas, con índices en estado, tipo, fecha y relaciones; entre 433 y 464, las 2 vistas: bandeja y ranking. Las entidades y los nombres son los del corte 1; las pantallas son las del corte 2; hoy las dos se apoyan en esta misma API."

### [10:32] Seguridad — 0:52

> "Seguridad, en tres ideas. La clave no se guarda tal cual: en `app/utils/security.py`, entre 23 y 85, queda como huella con un valor aleatorio, y la comparación es segura: no filtra nada por el tiempo que tarda. El token sale del ingreso y viaja en cada llamada; en `app/utils/roles.py`, línea 191, está la puerta de rol, y la regla vuelve a comprobar el permiso por adentro. Y las respuestas, en `app/schemas/simul_auth_schema.py`, 96 a 120, no devuelven la clave."

### [11:02] Pruebas — 0:30

> "En la terminal: `.\.venv\Scripts\python.exe -m pytest -q`, o simplemente `pytest -q`. Da 19 pruebas en una base temporal, sin tocar MySQL. En `tests/test_app.py`, entre 433 y 461, está la prueba de esta operación: crea contenido, aprueba y comprueba que el autor ganó exactamente 100 puntos."

### [11:37] Cierre — 0:35

> "Cierro con los 6 criterios: siete capas separadas; MySQL con 25 tablas y 2 vistas; API con Swagger, 30 rutas y 37 operaciones; reglas y permisos bien puestos; evidencia en Swagger, en Docker y en las 19 pruebas; y coherencia entre los tres cortes. La aprobación que vimos al principio es la misma que quedó guardada. Termino acá."

## Respaldo (no leer)

```sql
-- 1. Contenido 7 y su autor
SELECT c.id_contenido, c.estado, c.id_validador, c.fec_valid,
       u.nombre AS autor, u.puntos_total
FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
WHERE c.id_contenido = 7;
-- Esperado: publicado | 5 | fecha | Valentina Moreno | 1340 (antes 1240)

-- 2. Decisión del administrador
SELECT accion, id_admin, id_contenido, fecha_decision
FROM validacion_log
WHERE id_contenido = 7 AND accion = 'aprueba';
-- Esperado: aprueba | 5 | 7 | fecha

-- 3. Movimiento de puntos
SELECT puntos, id_usuario, id_contenido, motivo, fecha
FROM historial_puntos
WHERE id_contenido = 7 AND puntos = 100;
-- Esperado: 100 | 1 | 7 | Publicación en el museo: Propuesta: Sistema Blockchain para Titulos Academicos | fecha
```

- Si el contador sigue en 6, falta la sesión o la llamada no llegó a `/api/museo`.
- Si el estado sigue pendiente, la operación no se confirmó: revisar permiso y estado antes de repetir.
- El nivel y las insignias se recalculan con el total ya sumado.

**Preguntas propias de este botón**

- ¿Un docente puede decidir? No: la regla pide rol administrador y responde 403.
- ¿Cuántos puntos lleva el autor? 100 fijos, y la fila del historial lo confirma.
- ¿Quién queda registrado? El id 5, en el contenido y en la bitácora.
- ¿Se puede aprobar dos veces? No: si ya no está pendiente, responde 409.
