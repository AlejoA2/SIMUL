# 00 — Antes de grabar (común a los 3 videos)

Leelo una vez antes de grabar. Después abrí **tu** guion:
`VIDEO_1_APROBAR.md`, `VIDEO_2_RECHAZAR.md` o `VIDEO_3_BUSCAR.md`.

La idea es simple: los tres muestran **el mismo backend**. Cada video entra por una
acción distinta y recorre las siete capas, la base, Swagger, la seguridad, Docker y
las pruebas. No cambien nada del código mientras graban.

---

## 1. Levantar todo

En la raíz del proyecto:

```powershell
docker compose up -d --build
docker compose exec app python db/seed.py     # solo si la base está vacía
.\.venv\Scripts\python.exe -m pytest -q       # debe dar: 19 passed
```

Comprobación rápida de que la app está mirando MySQL y no el respaldo local:

```powershell
docker compose exec app printenv DATABASE_URL
```

Debe decir:

```text
mysql+pymysql://simul_user:simul_password@db:3306/simul_db
```

Si en otra máquina sale `sqlite:///simul_local.db`, el botón guarda en un archivo
local y DBeaver nunca ve el cambio. Ahí hay que levantar con Docker o copiar
`.env.example` a `.env` con la cadena MySQL de ese archivo.

---

## 2. Datos fijos para los tres

| Recurso | Valor |
|---|---|
| Swagger | `http://localhost:5000/docs` |
| Especificación | `http://localhost:5000/openapi.json` |
| API base | `http://localhost:5000/api/museo` |
| MySQL en DBeaver | `127.0.0.1:3307` · base `simul_db` · usuario `simul_user` · clave `simul_password` |
| Admin de demo | `l.jimenez@unilibre.edu.co` / `1234` |
| Id del admin | `5` — Ing. Laura Jimenez |
| Autor de ejemplo | Valentina Moreno, `id_usuario = 1`, empieza con `1240` puntos |
| Contenido de ejemplo para aprobar | `7` — "Propuesta: Sistema Blockchain para Titulos Academicos" |
| Contenido de ejemplo para rechazar | `13` — "Sistema Blockchain para Verificacion de Titulos Academicos" |
| Pendientes al empezar | `6`: ids `7, 13, 14, 15, 16, 17` |
| Puntos por publicar | `100` |
| Total de la API | `30 rutas` y `37 operaciones` |
| Base del diseño | `25 tablas` y `2 vistas` |
| Pruebas | `19` |

Usá **siempre `localhost:5000`** en el navegador. Si hacés login en
`127.0.0.1:5000` y después abrís `localhost:5000/admin/validacion`, el navegador
no comparte el token y la bandeja aparece vacía. Es el mismo error que vimos:
`GET /api/museo/validacion/bandeja` termina en `401`.

---

## 2b. Restaurar el estado antes de cada video

Cada video **escribe en MySQL**. Antes de grabar **cada** video, volvé a dejar la
base en los 6 pendientes originales. Pegá esto en DBeaver y ejecutalo:

```sql
UPDATE contenido
   SET estado='pendiente', id_validador=NULL, fec_valid=NULL, observaciones=NULL
 WHERE id_contenido IN (7,13,14);

DELETE FROM validacion_log
 WHERE id_contenido IN (7,13,14) AND DATE(fecha_decision)=CURDATE();

DELETE FROM historial_puntos
 WHERE id_contenido IN (7,13,14) AND DATE(fecha)=CURDATE();

DELETE FROM notificacion
 WHERE id_contenido IN (7,13,14)
   AND DATE(fecha_envio)=CURDATE()
   AND tipo IN ('aprobado','rechazado');

UPDATE usuario SET puntos_total=1240 WHERE id_usuario=1;  -- Valentina Moreno
UPDATE usuario SET puntos_total=0    WHERE id_usuario=2;  -- Juan Perez
```

Después refrescá DBeaver con **F5** y confirmá que el conteo vuelve a dar **6**.
Esto es necesario porque el video 1 aprueba el 7 desde la pantalla y el 13 desde
Swagger, y el video 2 rechaza el 13 desde la pantalla y el 14 desde Swagger.

---

## 3. Acuerdo previo — lo dicen los TRES, igual

Cada integrante reemplaza solo **[ANCLA]** por su acción: `la aprobación`,
`el rechazo` o `la búsqueda`. El resto, textual.

> "Antes de empezar, recuerdo que esto es la entrega del tercer corte. En el corte
> uno definimos las entidades y las reglas; en el corte dos quedaron las pantallas.
> Hoy esas pantallas ya no viven solas: el botón llama a una dirección `/api/museo`,
> esa dirección guarda en MySQL y la misma operación se ejecuta en Swagger. Los tres
> usamos el mismo backend y las mismas credenciales. Yo voy a recorrer todo el
> proyecto desde una sola acción: **[ANCLA]**."

---

## 4. Mapa de endpoints que se deben mostrar

No hace falta ejecutar todos, pero sí **abrirlos en Swagger y nombrarlos**. Cada
video ejecuta los suyos con *Try it out*.

| Endpoint | Para qué sirve | Video |
|---|---|---|
| `POST /api/museo/auth/login` | Obtener el token con el admin | 1, 2, 3 |
| `GET /api/museo/validacion/bandeja` | Ver la cola pendiente | 1, 2 |
| `POST /api/museo/validacion/{id}/aprobar` | Publicar y sumar puntos | 1 |
| `POST /api/museo/validacion/{id}/rechazar` | Guardar el motivo del rechazo | 2 |
| `GET /api/museo/validacion/{id}/historial` | Leer la decisión; solo admin | 2 |
| `GET /api/museo/contenido/` | Listar publicados con filtros | 3 |
| `GET /api/museo/contenido/{id}` | Ver el detalle público | 1, 3 |
| `GET /api/museo/contenido/mis-aportes` | Ver el motivo desde el autor | 2 |
| `GET /api/museo/admin/kpis` | Indicadores reales | 1, 2 |
| `GET /api/museo/gamificacion/ranking` | Puntos y nivel | 1 |

Códigos que deben aparecer: `200`, `201`, `401`, `403`, `404`, `409`, `422`.

---

## 5. Cómo se muestra Swagger (los tres)

1. Abrir `http://localhost:5000/docs`.
2. Buscar el endpoint por su nombre en la lista.
3. Tocar **Try it out**. Si pide token, arriba en **Authorize** se pega el valor
   que devolvió `POST /api/museo/auth/login`sin la palabra `Bearer`.
4. Ejecutar y leer en voz alta el código y el cuerpo.
5. Abrir `http://localhost:5000/openapi.json` y decir: **30 rutas, 37 operaciones**.

En el navegador, el token queda en `simul.token`. La sesión visible queda en
`simul.user`. Si el token falta o vence — dura 1 hora — vuelve a ingresar.

---

## 6. Cómo se muestra DBeaver (los tres)

1. Conectar a `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`.
2. Dejar abierta la pestaña de resultados y apretar **F5** o refrescar antes de
   cada lectura. DBeaver puede mostrar el resultset anterior.
3. Si el conteo no cambia, comprobar que el contenedor `simul_app` esté arriba y
   que `DATABASE_URL` no apunte a SQLite.

> **Si sale `Access denied for user 'inventory_user'...`:** es la conexión
> vieja del proyecto inventory, que ya no existe. Los datos actuales son
> `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`, clave
> `simul_password`: click derecho → **Editar conexión** → pestaña *Principal* →
> corregir base, usuario y clave → **Probar conexión**.

> **Si al abrir una tabla (por ejemplo `avance_investigacion`) sale
> `Public key retrieval is not allowed`:** MySQL 8 usa la autenticación
> `caching_sha2_password` y el controlador necesita la clave pública del
> servidor. Arreglo (una sola vez por conexión):
>
> 1. Click derecho en la conexión → **Editar conexión**.
> 2. Pestaña **Propiedades del controlador** (*Driver properties*).
> 3. Buscar `allowPublicKeyRetrieval` y ponerle el valor **`true`**
>    (doble clic en la columna del valor). Si no aparece, agregarla con el
>    botón **+** (*Add new property*).
> 4. **Aceptar** y reconectar (click derecho → **Reconectar**).
>
> Después las tablas y columnas se abren sin pedir más nada.

Consultas base:

```sql
SELECT COUNT(*) AS pendientes,
       GROUP_CONCAT(id_contenido ORDER BY id_contenido) AS ids
FROM contenido WHERE estado = 'pendiente';
-- Antes: 6 → 7,13,14,15,16,17
```

Cada video tiene además sus tres consultas de prueba en la sección "Respaldo".

---

## 7. Archivos del tronco común

Tenerlos a mano. Son los mismos en los tres videos.

| Archivo | Líneas | Qué se ve |
|---|---|---|
| `docker-compose.yml` | `14-25` | servicio app, puerto `5000`, cadena MySQL |
| `docker-compose.yml` | `27-44` | MySQL 8.4, puerto `3307`, volumen, DDL inicial, healthcheck |
| `app/__init__.py` | `114-126` | errores HTTP con sobre uniforme |
| `app/__init__.py` | `128-157` | errores de validación → `422` con `details` |
| `app/__init__.py` | `159-177` | error interno genérico, sin traza |
| `app/__init__.py` | `208-238` | `include_router`: prefijos `/api/museo/...` |
| `app/utils/response.py` | `14-59` | sobre `{success, message, data}` |
| `app/utils/roles.py` | `47-94` | token y comprobación de sesión |
| `app/utils/security.py` | `23-85` | huella de la clave y comparación segura |
| `app/static/js/api.js` | `19-92` | token, petición HTTP y lectura de la respuesta |
| `db/DDL.sql` | `94-118` | tabla `contenido` y sus índices |
| `db/DDL.sql` | `375-389` | tabla `validacion_log` |
| `db/DDL.sql` | `394-408` | tabla `historial_puntos` |
| `db/DDL.sql` | `433-464` | las dos vistas |
| `tests/test_app.py` | `20-39` | documentación OpenAPI |

---

## 8. Las siete capas y los 6 criterios

**Siete capas:** entrada, orden del trabajo, reglas, acceso a datos, modelos,
formatos y utilidades.

**6 criterios que se nombran al cerrar:**

1. Siete capas separadas.
2. MySQL con 25 tablas y 2 vistas.
3. API REST con Swagger y 30 rutas / 37 operaciones.
4. Reglas, validaciones, sesión y roles.
5. Evidencia en Swagger, Docker y 19 pruebas.
6. Coherencia entre los tres cortes.

---

## 9. Checklist antes de grabar

- [ ] Docker arriba y `/docs` responde.
- [ ] `printenv DATABASE_URL` apunta a MySQL, no a SQLite.
- [ ] DBeaver en `127.0.0.1:3307` y el conteo da 6 pendientes.
- [ ] Login real desde `/login` con `l.jimenez@unilibre.edu.co`.
- [ ] `SIMULApi.getToken()` devuelve un token en la consola.
- [ ] La página correspondiente carga sin errores en consola.
- [ ] Editor abierto con los archivos del tronco común y los de tu video.
- [ ] Acuerdo previo memorizado, con tu ancla.
- [ ] `pytest -q` da 19 passed.
