# Guiones de video — Tercer corte SIMUL

**Entregable:** un video por integrante. Cada uno explica **un botón** y lo sigue
desde la parte visual hasta MySQL y de vuelta, demostrando conocimiento de arriba
a abajo. Duración sugerida: **4–6 min por integrante**.

> Cada integrante debe decir **exactamente lo mismo** en el punto 0 ("Acuerdo
> previo"). Eso evita que el docente piense que uno cableó el botón y otro no.

---

## 0. Acuerdo previo (lo dicen los tres, 20 segundos)

> "Antes de empezar, una aclaración importante para que se entienda lo que van a
> ver. En este repositorio conviven **dos capas con propósitos distintos**:
>
> - La **interfaz HTML** que ves en pantalla es la entrega del **corte 2**: un
>   prototipo autocontenido que persiste en `localStorage` para poder demostrarlo
>   sin servidor.
> - El **backend del corte 3** expone **esa misma operación** como API REST, y es
>   lo que vamos a ejecutar en **Swagger / Postman contra MySQL**.
>
> El botón visual no dispara directamente la API: lo dejamos así para **no romper
> el entregable anterior**, y para que se vea la trazabilidad entre los tres
> cortes. Cada uno lo va a decir antes de bajar al código. Lo que sí demostramos
> es que la operación está implementada de verdad, capa por capa, y persiste en
> la base de datos."

**Frase sobre Flask vs FastAPI** (si el docente pregunta, o para decirla al cierre):

> "El enunciado menciona Flask porque era el framework con el que arrancamos en
> el corte 2. En este corte **migramos a FastAPI**, que es el que aparece en el
> resumen de criterios de la rúbrica. La decisión está justificada: FastAPI nos
> da OpenAPI/Swagger automático, validación con Pydantic y soporte async sin
> código extra. Las vistas Jinja se conservan y ahora las sirve FastAPI."

---

## Checklist antes de grabar (común para los tres)

```bash
# 1. Contenedores arriba (ya están levantados, pero esto lo reproduce cualquiera)
docker compose up --build

# 2. Si la BD está vacía, sembrar:
docker compose exec app python db/seed.py

# 3. Verificar en el navegador:
#    Swagger  -> http://localhost:5000/docs
#    Museo    -> http://localhost:5000/
#    DBeaver  -> 127.0.0.1:3307 / simul_db / simul_user / simul_password
```

**Credencial admin (la misma para los tres):** `l.jimenez@unilibre.edu.co` / `1234`
(contraseña de todos los usuarios de demostración).

**En pantalla, ten abierto:** el navegador con la página correspondiente y
`/docs` en otra pestaña; el editor con los archivos que se citan; DBeaver si vas
a mostrar la persistencia.

---

# INTEGRANTE 1 — Botón «Aprobar y publicar»

**Criterios que cubre:** 1 (arquitectura), 2 (BD/SQLAlchemy), 4 (reglas de negocio,
roles, seguridad), 6 (coherencia con cortes 1–2).
**Requerimientos:** RF-VAL-01, RF-VAL-02, RF-VAL-04, RF-GAM-01, RNF-SEG-02.

## Guion literal

**[Pantalla: `/admin/validacion`, sesión admin]**

> "Soy **[NOMBRE]**. Voy a explicar el botón **«Aprobar y publicar»** de la bandeja
> de validación del administrador, y lo voy a seguir desde lo que ve el usuario
> hasta la fila que queda escrita en MySQL.
>
> *(Acuerdo previo — léelo aquí también.)*
>
> Estoy en `/admin/validacion`. Esta página la sirve FastAPI con una plantilla
> Jinja: la ruta está en `app/routes/web_routes.py`, función `admin_validacion`.
> El contador dice **6 pendientes** y las tarjetas las pinta JavaScript, no las
> trae el servidor."

**[Señala el botón de una tarjeta]**

> "Fíjate en el botón: dice **«Aprobar y publicar»**. No tiene un `id` HTML; se
> identifica con el atributo `data-approve`. Se genera en
> `app/static/js/pages/admin_validacion.js`, alrededor de la línea 165, y el
> click se captura por delegación de eventos: `LISTA.addEventListener('click', …)`
> busca `event.target.closest('[data-approve]')` y llama a `aprobar(id)`.
>
> Esa función hace tres cosas en el navegador: `Store.upsertContent(...)` mete la
> pieza en el catálogo con `status: 'publicado'`, `Store.dropFromQueue(id)` la
> saca de la bandeja, y sale un *toast* «Contenido aprobado y publicado». A los
> 900 ms redirige a `/admin/publicacion`. Todo eso es `localStorage` —como
> acordamos, es la capa visual del corte 2—."

**[Cambia a `/docs`]**

> "La operación real del corte 3 está aquí: **`POST /api/museo/validacion/{id}/aprobar`**,
> en el tag **Validación**. El resumen dice *«Aprobar contenido (+100 puntos al
> autor)»* y la descripción, *«Transacción única: estado publicado, bitácora,
> notificación, puntos, nivel e insignias»*. Ese texto no es decorativo: FastAPI
> lo genera desde el `summary` y el `description` del decorador en
> `app/routes/validacion_routes.py`.
>
> El prefijo `/api/museo/validacion` se monta en `app/__init__.py` con
> `include_router`. Fíjate en que el router entero lleva
> `dependencies=[Depends(requiere_usuario)]`: sin token, la respuesta es **401**."

**[Pulsa Authorize, pega el token del login admin]**

> "Ya autorizado. Antes de ejecutar, sigo el recorrido por el código."

**[Editor: `validacion_routes.py` → `validacion_controller.py`]**

> "**Capa 1, la ruta.** La función `aprobar` recibe el `contenido_id` por la URL
> y un cuerpo `DecisionIn | None`. Al aprobar, las observaciones son **opcionales**
> — por eso `Body(default=None)` y `model_dump(exclude_unset=True)`.
>
> **Capa 2, el controlador.** `ValidacionController.aprobar` delega en
> `_decidir(contenido_id, payload, 'aprobar')`, que obtiene al usuario con
> `usuario_actual()` y llama a `service.aprobar`. Ojo con un detalle de diseño:
> el controlador **no** comprueba el rol aquí; la comprobación de administrador
> la hace el servicio, para que la regla no se pueda saltar desde otra ruta."

**[Editor: `validacion_service.py`, método `aprobar`]**

> "**Capa 3, el servicio — aquí está el corazón de la regla de negocio.**
>
> Primero `_cargar(contenido_id, admin)`. Esa función es la que decide:
> - si `admin.rol_nombre != 'admin'` → **403** *«Se requiere rol administrador»*;
>   `rol_nombre` es una propiedad del modelo `Usuario` que devuelve
>   `self.rol.nombre`;
> - si no existe el contenido → **404**;
> - si `estado != 'pendiente'` → **409** *«El contenido no está en la bandeja»*.
>   Esto evita aprobar dos veces.
>
> Luego, en una sola transacción:
> 1. `contenido.estado = 'publicado'`, `id_validador = admin.id_usuario`,
>    `fec_valid` y `observaciones`.
> 2. `add_log(ValidacionLog(accion='aprueba', …))` → la bitácora.
> 3. `_notificar(...)` crea una `Notificacion(tipo='aprobado')` para el autor.
> 4. `gamificacion.registrar_movimiento(..., puntos=PUNTOS_PUBLICAR)`,
>    donde `PUNTOS_PUBLICAR = 100`. Ese método suma `usuario.puntos_total += 100`
>    y escribe un `HistorialPuntos` con el motivo.
> 5. `_refrescar_gamificacion(autor)` recalcula el nivel por rangos
>    (`get_nivel_por_puntos`) y otorga insignias cuyo `puntos_requeridos` ya se
>    cumpla.
> 6. **Un único `db.session.commit()`** al final.
>
> Es decir: o se hacen las seis cosas, o no se hace ninguna. Eso es una
> transacción de verdad, no seis guardados sueltos."

**[Editor: repositorios y modelos]**

> "**Capa 4, el repositorio.** `ContenidoRepository.get_by_id` usa
> `db.session.get(Contenido, id)`, que aprovecha el mapa de identidad de
> SQLAlchemy. `ValidacionRepository.add_log` solo hace `db.session.add`: **no hace
> commit**, porque el commit lo decide el servicio.
>
> **Capa 5, el modelo y la BD.** En `app/models/contenido.py` el campo `estado`
> es un `ENUM('pendiente','publicado','rechazado')`, con índice, y `id_validador`
> es FK a usuario con `ON DELETE SET NULL`. En `validacion_log` el campo `accion`
> es `ENUM('aprueba','rechaza')`. Todo eso está espejado en `db/DDL.sql`: **25
> tablas y 2 vistas**, `v_bandeja_validacion` y `v_ranking`. El DDL se monta como
> *init script* de MySQL en `docker-compose.yml`, así que la primera vez que
> arranca el contenedor la base nace exactamente como el diagrama E-R del corte 2."

**[Vuelve a Swagger y ejecuta]**

> "Ejecuto con un id pendiente. **HTTP 200**, y el sobre de respuesta es siempre
> el mismo, de `app/utils/response.py`:
> `{ success: true, message: 'Contenido aprobado y publicado', data: {...} }`.
> En `data` aparece el contenido con `estado: 'publicado'`; fíjate en que el
> modelo de salida expone el validador como objeto, pero **no expone
> `password_hash`** en ningún lado."

**[DBeaver]**

> "Y va la prueba de persistencia. En DBeaver, sobre `simul_db`:
>
> ```sql
> SELECT c.id_contenido, c.titulo, c.estado, c.fec_valid, u.puntos_total
> FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
> WHERE c.id_contenido = <ID>;
>
> SELECT accion, observaciones, fecha_decision FROM validacion_log
> WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;
>
> SELECT puntos, motivo FROM historial_puntos
> WHERE id_contenido = <ID> ORDER BY fecha DESC;
> ```
>
> Ahí está: el estado cambió, aparece la fila `aprueba` en la bitácora, el
> movimiento de **+100** puntos y el total del autor actualizado. La petición
> pasó por un middleware en `app/__init__.py` que instala una sesión por
> petición, hace `commit` si el código es menor a 400 y `rollback` si no."

### Preguntas que te puede hacer el docente

| Pregunta | Respuesta corta |
|---|---|
| ¿Quién hace el `commit`? | El servicio, una sola vez; el middleware confirma la misma sesión si la respuesta es < 400 y hace `rollback` en error. |
| ¿Qué pasa si un docente aprueba? | 403. Se comprueba `admin.rol_nombre` en `_cargar`, dentro del servicio. |
| ¿Cómo sabes que son 100 puntos y no otro número? | Constante `PUNTOS_PUBLICAR = 100` y movimiento en `historial_puntos`; hay un test que compara `despues == antes + 100`. |
| ¿Dónde queda el motivo de la decisión? | En `contenido.observaciones` y en `validacion_log.observaciones`. |
| ¿Por qué el botón de la web no llama a esto? | Es el prototipo del corte 2 en `localStorage`; la API se demuestra en Swagger/Postman para conservar la coherencia entre cortes. |

---

# INTEGRANTE 2 — Botón «Rechazar» con motivo obligatorio

**Criterios que cubre:** 3 (códigos HTTP, CRUD, Swagger), 4 (validaciones,
errores, no exponer datos sensibles), 6 (coherencia).
**Requerimientos:** RF-VAL-03, RNF-SEG-04, RNF-SEG-02.

## Guion literal

**[Pantalla: `/admin/validacion`, sesión admin]**

> "Soy **[NOMBRE]**. Voy a explicar el botón **«Rechazar»**. Lo interesante de este
> botón no es cambiar el estado, sino que **exige un motivo** y que ese motivo
> queda registrado para que el autor pueda leerlo. Lo sigo desde el modal hasta
> la bitácora en MySQL.
>
> *(Acuerdo previo — léelo aquí también.)*
>
> En la tarjeta hay otro botón, `data-reject`, que dice **«Rechazar»** — se genera
> en `admin_validacion.js`, junto al de aprobar. El click llama a `rechazar(id)`."

**[Haz clic en Rechazar]**

> "Se abre un modal con tres cosas: el título **«Rechazar contenido»**, un
> `<textarea id="reject-reason">` con la etiqueta **«Observaciones \*»**, y un
> botón **«Confirmar rechazo»** (`#reject-confirm`).
>
> Si dejo el campo vacío y pulso confirmar, aparece el mensaje rojo
> *«Escribe el motivo del rechazo: es obligatorio (RNF-SEG-04)»*. Ese código
> RNF-SEG-04 viene del corte 1. Fíjate en el detalle: el JavaScript solo valida
> que no esté vacío después de `trim()`. **No valida longitud mínima**; eso lo
> hace el backend, y ahora lo muestro."

**[Cambia a `/docs`]**

> "En Swagger está `POST /api/museo/validacion/{id}/rechazar`. Fíjate en el
> *Request body*: el esquema `RechazoIn` marca `observaciones` como **required**,
> con `minLength: 5` y `maxLength: 1000`. Eso sale de
> `app/schemas/contenido_schema.py`:
>
> ```python
> class RechazoIn(ModeloSalida):
>     observaciones: str = Field(
>         min_length=5, max_length=1000,
>         description="Motivo del rechazo (mínimo 5 caracteres)"
>     )
> ```
>
> Compáralo con `DecisionIn`, que es el de aprobar: ahí es `str | None = None`,
> opcional. La diferencia está pensada: aprobar no necesita explicación,
> rechazar sí."

**[Ejecuta con `{}`]**

> "Mando un cuerpo vacío. **HTTP 422**, y la respuesta es
> `{ success: false, message: 'Datos inválidos', details: { observaciones: [...] } }`.
> Ese 422 no lo escribe el endpoint: **FastAPI valida antes de entrar**, con
> Pydantic v2, y el manejador global `RequestValidationError` en
> `app/__init__.py` convierte cada error en una clave de `details`. Por eso el
> código HTTP es semántico: 422 es 'entendí la petición pero los datos no sirven',
> no un 400 genérico."

**[Editor: ruta → controlador → servicio]**

> "Si el cuerpo pasa, entramos en la ruta `rechazar`, que recibe `payload:
> RechazoIn` y lo reenvía con `payload.model_dump()`. El controlador `_decidir`
> comprueba que haya usuario (401 si no) y llama a `service.rechazar`.
>
> En el servicio, `_cargar` repite las mismas barreras que en aprobar: **403** si
> no es admin, **404** si no existe, **409** si ya no está pendiente. Después
> `_observaciones(data)` limpia el texto con `.strip()`. Y aquí hay una segunda
> línea de defensa que me gustaría destacar: si después de limpiar queda vacío,
> el servicio devuelve **422 propio** con
> `details: { observaciones: ['El motivo del rechazo es obligatorio'] }`.
> ¿Para qué, si Pydantic ya validó? Porque cinco espacios en blanco pasan
> `min_length=5`, pero `.strip()` los convierte en cadena vacía. Es una defensa
> en profundidad.
>
> Luego `contenido.estado = 'rechazado'`, `id_validador`, `fec_valid` y
> `observaciones = motivo`; `ValidacionLog(accion='rechaza')`;
> `_notificar(..., tipo='rechazado')` para el autor; un solo `commit`; y
> `success(..., 'Contenido rechazado')`.
>
> **Lo que NO hace: sumar puntos.** No hay ni una llamada a gamificación en todo
> el método `rechazar`. Es una regla de negocio deliberada: se premia publicar,
> no se premia rechazar. Eso lo contrasté con el integrante 1."

**[Ejecuta con un motivo válido y muestra el historial]**

> "Ahora mando `{'observaciones': 'Falta evidencia fotográfica'}`. **HTTP 200**,
> `estado: 'rechazado'`. Y si repito la misma llamada sobre el mismo id, obtengo
> **409**: no se puede decidir dos veces.
>
> Después llamo a `GET /api/museo/validacion/{id}/historial`. Aparece una entrada
> con `accion: 'rechaza'` y el mismo texto. Ese endpoint es **solo para admin**:
> aunque el router solo exige JWT, el controlador `historial` comprueba
> `rol_nombre == 'admin'` y devuelve 403 si no lo es. El motivo no se pierde."

**[Seguridad]**

> "Y un último punto de seguridad: las respuestas usan siempre el sobre de
> `app/utils/response.py`. Los errores globales del `create_app` dan **401** sin
> token, **422** por validación y **500** con un mensaje genérico — el *traceback*
> se registra en el log del servidor con `logger.exception`, **nunca se envía al
> cliente**. Los esquemas de salida tampoco filtran datos sensibles: `AutorOut`
> solo expone `id_usuario`, `nombre` y `foto`, y `UsuarioOut` lleva literalmente
> en su docstring *«Serialización de usuario SIN password_hash»*."

### Preguntas que te puede hacer el docente

| Pregunta | Respuesta corta |
|---|---|
| ¿422 o 400? | 422 porque es validación semántica de campos; el manejador global de `RequestValidationError` lo estandariza. |
| ¿No es redundante validar en JS, en Pydantic y en el servicio? | No: JS da respuesta inmediata, Pydantic es el contrato de la API y el servicio cubre el caso de espacios en blanco. Defensa en profundidad. |
| ¿Quién lee el motivo? | El autor en «Mis aportes» (RNF-SEG-04) y el admin en `/historial`. |
| ¿Por qué no suma puntos? | Regla de negocio: solo la publicación rewards. No hay llamada a gamificación en `rechazar`. |
| ¿Cómo demuestras el 422? | En Swagger con `{}` y en Postman con el request «Rechazar sin motivo (422)» de la carpeta Validación. |

---

# INTEGRANTE 3 — Botón «Buscar / filtrar» + mapa CRUD y Docker

**Criterios que cubre:** 2 (BD y ORM), 3 (API REST y CRUD), 5 (pruebas, Swagger,
Docker), 6 (coherencia).
**Requerimiento:** RF-EXP-02.

## Guion literal

**[Pantalla: `/buscar`]**

> "Soy **[NOMBRE]**. Voy a explicar el buscador del museo y, de paso, les muestro
> el mapa completo de la API REST y cómo se ejecuta en Docker.
>
> *(Acuerdo previo — léelo aquí también.)*
>
> Estoy en `/buscar`. No hay un botón «Buscar» con id: la búsqueda se dispara con
> el evento `input` del campo `#search-input`, con los filtros laterales
> `data-filter-category` y `data-filter-year`, y con `#search-clear` para limpiar.
> En `app/static/js/pages/buscar.js`, la función `publicados()` lee
> `Store.getContent()` y filtra por `status === 'publicado'`; `coincide()` compara
> texto en título y etiquetas, categoría exacta y año, con el caso especial
> «Antes de 2019».
>
> Otra vez: es `localStorage`. Los datos iniciales los inyecta Jinja desde
> `app/data/simul_data.py` en la ruta `web_routes.py`. No hay ni un `fetch` en
> este archivo."

**[Cambia a `/docs`]**

> "La misma búsqueda como API es **`GET /api/museo/contenido/`**, público, en el
> tag **Contenido**. Miren los parámetros que Swagger documenta automáticamente
> desde los `Query(...)` de `app/routes/contenido_routes.py`:
> `q`, `categoria`, `tipo`, `anio` —con mínimo 1900 y máximo 2100—, `page`
> (mínimo 1) y `per_page` (entre 1 y 100). Si mando `anio=1800`, obtengo **422**:
> la validación es declarativa, no un `if` dentro de la función."

**[Editor: controlador → servicio → repositorio]**

> "El controlador normaliza los `None` a `page=1` y `per_page=12`. El servicio
> llama a `ContenidoRepository.get_publicados`, y aquí conviene mirar con calma:
>
> ```python
> query = db.session.query(Contenido).filter(
>     Contenido.estado == "publicado"
> )
> query = self._aplicar_filtros(query, q, categoria, tipo, anio)
> total = query.count()
> items = (query.order_by(Contenido.fec_crea.desc())
>               .offset((page - 1) * per_page)
>               .limit(per_page).all())
> ```
>
> y el número de páginas se calcula con `pages = -(-total // per_page)`, que es
> el techo de la división. El resultado se guarda en un `@dataclass Pagina` con
> `items`, `page`, `per_page`, `total` y `pages`.
>
> En `_aplicar_filtros`, el texto usa `.ilike(f'%{q}%')` sobre `titulo` y
> `categoria`. El año es más interesante: como el año vive en las tablas de
> subtipo, no en `contenido`, se usa `id_contenido.in_(select(...))` contra cada
> subtipo, y para `Evento` y `Noticia` se aplica `extract('year', fecha)`.
> **¿Por qué `IN (SELECT ...)` y no un `JOIN`?** Porque un `JOIN` duplicaría la
> fila base de contenido si un proyecto tiene varios registros; con `IN`
> cada contenido aparece una sola vez."

**[Muestra el SQL generado]**

> "Esto es lo que SQLAlchemy manda a MySQL:
>
> ```sql
> SELECT ... FROM contenido
> WHERE contenido.estado = 'publicado'
>   AND (lower(contenido.titulo) LIKE lower('%museo%')
>        OR lower(contenido.categoria) LIKE lower('%museo%'))
>   AND contenido.id_contenido IN (
>         SELECT evento.id_contenido FROM evento
>         WHERE EXTRACT(year FROM evento.fecha_evento) = 2024)
> ORDER BY contenido.fec_crea DESC
> LIMIT 12, 12;
> ```
>
> Fíjate en la correspondencia con el diseño: `estado`, `tipo`, `categoria` y
> `fec_crea` tienen índice en el modelo (`index=True`) y en el DDL
> (`idx_contenido_estado`, `idx_contenido_tipo`, …). El tipo `YEAR` del diagrama
> se logra con un `TypeDecorator` propio, `app/models/types.py`: en MySQL crea
> `YEAR` y en el SQLite de desarrollo crea `SMALLINT`, para que la app arranque
> en cualquier entorno."

**[Ejecuta en Swagger]**

> "Ejecuto con `q=museo&anio=2024&page=1&per_page=12`. **HTTP 200** y el sobre
> `{ success: true, message: 'OK', data: { items: [...], page: 1, pages: N,
> total: M } }`. Cada item lo construye `_resumen()` con los campos que ya
> existían en el prototipo: `tipo`, `titulo`, `categoria`, `anio`, `imagen`,
> `descripcion` y `autor`. Ahí está la coherencia con el corte 2: **los mismos
> nombres de campo**, ahora leídos desde MySQL."

**[Mapa CRUD — 40 segundos]**

> "Para cerrar el mapa de la API: todo vive bajo `/api/museo` y Swagger muestra
> **30 rutas / 37 operaciones**. En contenido tenemos **GET** de listado y
> detalle, **POST** para crear (nace pendiente) y para evidencias, comentarios,
> reacciones y favoritos, **PUT** y **PATCH** para actualizar —solo el autor o un
> admin— y **DELETE** solo para admin. Los códigos son 200/201 para éxito, 401
> sin token, 403 sin permiso, 404 no encontrado y 422 validación. Además están
> los módulos de autenticación, validación, gamificación, administración y las
> vistas del museo. El archivo `docs/postman/SIMUL.postman_collection.json`
> reúne **6 carpetas y 23 peticiones** con sus pruebas, y ya está corregido con
> la credencial real del admin."

**[Terminal / Docker]**

> "Y la reproducibilidad: `docker compose up --build` levanta **`simul_app`** en
> el puerto 5000 y **`simul_db`** (MySQL 8.4) en el 3307. El app espera a que la
> base esté *healthy* antes de arrancar; el DDL se monta como init script, así
> que las 25 tablas y las 2 vistas se crean solas la primera vez. Cargo los datos
> con `docker compose exec app python db/seed.py`, corro `pytest -q` —**19
> pruebas**— y lo veo en DBeaver con `127.0.0.1:3307`, `simul_db`,
> `simul_user` / `simul_password`."

### Preguntas que te puede hacer el docente

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué `IN` y no `JOIN` para el año? | Evita duplicar filas de contenido; el año está en tablas de subtipo 1:1. |
| ¿Cómo calculas la paginación? | `count()` para el total, `offset((page-1)*per_page).limit(per_page)` y techo con `-(-total // per_page)`. |
| ¿Qué pasa con `anio=1800`? | 422, porque `Query(ge=1900, le=2100)` lo valida antes del endpoint. |
| ¿Dónde está Docker? | `docker-compose.yml`: dos servicios, healthcheck, init script del DDL y volumen persistente. |
| ¿Cómo demuestras que funciona? | Swagger, colección Postman con 23 requests, 19 tests y DBeaver contra MySQL. |

---

# Preguntas transversales (prepárenlas los tres)

**¿El proyecto usa Flask o FastAPI?**
> Arrancamos en Flask en el corte 2; en este corte migramos a FastAPI, que es lo
> que pide el resumen de la rúbrica. Se conservan las plantillas Jinja, ahora
> servidas por `Jinja2Templates`. No queda ni un `import flask` en el código.

**¿Por qué el botón de la interfaz no llama a la API?**
> Por decisión de coherencia: el corte 2 era un prototipo sin base de datos y lo
> conservamos tal cual. La operación está implementada y se demuestra en
> Swagger/Postman, que es lo que pide el criterio 5. Está documentado en
> `web_routes.py` y en `docs/`.

**¿Cómo saben que los modelos corresponden al diagrama E-R?**
> `db/DDL.sql` tiene 25 tablas y 2 vistas con ENUM, YEAR, claves foráneas e
> índices; los 25 modelos ORM replican tablas, columnas, relaciones e índices, y
> el DDL se monta como init script de MySQL.

**¿Dónde se maneja un error inesperado?**
> En el manejador global `Exception` de `create_app`: 500 con mensaje genérico,
> `logger.exception` en el servidor y sin traza expuesta al cliente.

**¿Qué cambiaría si conectáramos el botón a la API mañana?**
> En `admin_validacion.js` cambiaría `Store.upsertContent/dropFromQueue` por un
> `fetch` al endpoint con el JWT; ni el HTML ni las capas `routes → controllers →
> services → repositories → models` tendrían que tocarse. Eso es precisamente lo
> que demuestra que la arquitectura está bien separada.

---

## Errores que NO deben decir

- ❌ "El botón guarda en MySQL" → **no**: guarda en `localStorage`; MySQL se
  demuestra en Swagger/Postman.
- ❌ "El repo hace el commit" → **no**: el servicio hace el commit y el
  middleware lo confirma/hace rollback.
- ❌ "Es Flask" → **no**: es FastAPI; Flask fue el corte 2.
- ❌ "Rechazar también da puntos" → **no**: solo aprobar suma 100.
- ❌ "El 422 lo lanza Pydantic en el endpoint" → más preciso: FastAPI valida
  **antes** de entrar al endpoint y el handler global arma el sobre de error.
- ❌ Inventar un `require_admin`: en el código no existe; el rol se comprueba en
  el servicio (`rol_nombre`) y en algunos controladores.
