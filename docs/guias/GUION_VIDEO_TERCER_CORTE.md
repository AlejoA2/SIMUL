# Guiones de video — Tercer corte SIMUL (versión ≤ 10 min)

**Regla de oro:** cada video dura **máximo 10 minutos**. El texto marcado con `>`
es lo que se **dice en voz alta**; el resto es material de apoyo que **no se lee**
(sirve para responder preguntas o para tener a mano).

## Presupuesto de tiempo por video

| Bloque | Tiempo |
|---|---:|
| Acuerdo previo (lo leen los tres, idéntico) | 1:00 |
| Guion hablado del integrante | 4:00 – 4:30 |
| Pausas para clics, Swagger, DBeaver y lectura de código/SQL en pantalla | 2:30 – 3:30 |
| **Total** | **7:30 – 9:00** (tope 10:00) |

> Ritmo de referencia: **~100 palabras/minuto** hablando de código en español con
> pausas. Si te quedas corto, usa el material de respaldo; **nunca improvises
> diciendo que el botón guarda en MySQL**.

---

## 0. Acuerdo previo — lo dicen los TRES, idéntico (1:00)

> "Aclaración antes de empezar: la interfaz HTML es la entrega del **corte 2** y
> persiste en `localStorage`; el backend del **corte 3** expone esa misma
> operación como API REST y la demostramos en **Swagger y Postman contra MySQL**.
> El botón visual no llama a la API —lo dejamos así para conservar el entregable
> anterior—, pero la operación sí está implementada capa por capa y persiste.
> Arrancamos en Flask en el corte 2 y migramos a **FastAPI**, que da Swagger
> automático y validación con Pydantic. Los tres diremos lo mismo."

---

# INTEGRANTE 1 — Botón «Aprobar y publicar» (≈ 8:00, tope 9:30)

**Cubre:** criterios 1, 2, 4 y 6. **RF:** VAL-01/02/04, GAM-01, SEG-02.

> **[0:00] Presentación.** Soy **[NOMBRE]**. Explico el botón **«Aprobar y
> publicar»** de la bandeja de validación y lo sigo desde la pantalla hasta la
> fila que queda en MySQL. *(Acuerdo previo.)*
>
> **[1:00] Capa visual.** Estoy en `/admin/validacion`: la sirve FastAPI con una
> plantilla Jinja desde `web_routes.py`. El botón no tiene `id` HTML: se genera
> en `admin_validacion.js` con el atributo `data-approve`, y el click se captura
> por delegación — `closest('[data-approve]')` → `aprobar(id)`. Esa función hace
> `Store.upsertContent(status:'publicado')`, `Store.dropFromQueue` y un toast.
> Todo eso es `localStorage`: es la capa visual del corte 2.
>
> **[1:50] El puente.** La operación real es **`POST /api/museo/validacion/{id}/aprobar`**.
> El *summary* dice «+100 puntos al autor» y Swagger lo genera desde el
> decorador de `validacion_routes.py`. El router lleva
> `Depends(requiere_usuario)`: sin token, **401**. Autorizo con el admin.
>
> **[2:20] Ruta y controlador.** La ruta recibe `DecisionIn | None`: al aprobar
> las observaciones son opcionales, por eso `Body(default=None)`. El controlador
> `_decidir` obtiene al usuario con `usuario_actual()` y llama a
> `service.aprobar`. Detalle de diseño: el **rol no se comprueba aquí**, se
> comprueba en el servicio, para que la regla no se pueda saltar desde otra ruta.
>
> **[3:00] Servicio — el corazón.** `_cargar` devuelve **403** si
> `admin.rol_nombre != 'admin'` —propiedad que lee `self.rol.nombre`—, **404** si
> no existe el contenido y **409** si `estado != 'pendiente'`: así no se puede
> aprobar dos veces. Después, en **una sola transacción**: estado `publicado`,
> `id_validador` y `fec_valid`; `ValidacionLog(accion='aprueba')`; notificación
> al autor; `registrar_movimiento(puntos=100)`, que suma `puntos_total` y escribe
> un `HistorialPuntos`; `_refrescar_gamificacion`, que recalcula el nivel por
> rangos y otorga insignias; y **un único commit**. O se hacen las seis cosas, o
> no se hace ninguna.
>
> **[4:50] Repositorio y modelo.** `get_by_id` usa `db.session.get`, que
> aprovecha el mapa de identidad de SQLAlchemy. `add_log` solo hace `add`: no
> commitea. En `contenido.py`, `estado` es un ENUM con índice y `id_validador` es
> FK con `ON DELETE SET NULL`; en `validacion_log`, `accion` es ENUM
> `aprueba/rechaza`. Todo eso está espejado en `db/DDL.sql`: **25 tablas y 2
> vistas**, montado como *init script* de MySQL.
>
> **[5:50] Ejecuto → HTTP 200.** El sobre es `{success, message, data}`, de
> `response.py`. En `data` aparece `estado: 'publicado'` y el validador como
> objeto, pero **nunca `password_hash`**. El middleware instala una sesión por
> petición, hace `commit` si el código es < 400 y `rollback` si no.
>
> **[6:30] Persistencia.** En DBeaver muestro el contenido, la fila `aprueba` en
> `validacion_log`, el movimiento de **+100** y el total actualizado del autor.
> Cierro con la trazabilidad: **RF-VAL-02 y RF-VAL-04** del corte 1, el botón en
> el corte 2 y esta transacción en el corte 3.

### Respaldo de integrante 1 (no leer; útil si preguntan)

```sql
SELECT c.id_contenido, c.titulo, c.estado, c.fec_valid, u.puntos_total
FROM contenido c JOIN usuario u ON u.id_usuario = c.id_autor
WHERE c.id_contenido = <ID>;

SELECT accion, observaciones, fecha_decision FROM validacion_log
WHERE id_contenido = <ID> ORDER BY fecha_decision DESC;

SELECT puntos, motivo FROM historial_puntos
WHERE id_contenido = <ID> ORDER BY fecha DESC;
```

- `PUNTOS_PUBLICAR = 100` está en `validacion_service.py`; `_observaciones()` hace
  `.strip()` y al aprobar puede devolver cadena vacía.
- `get_nivel_por_puntos`: regla `>= mínimo y < máximo`; el último nivel incluye su
  máximo. Insignias: `puntos_requeridos <= puntos_total`.
- Los repositorios `add_log` y `otorgar_insignia` **no commitean**: el commit es
  del servicio. El middleware vuelve a confirmar la misma sesión si status < 400.
- Errores globales en `create_app`: `StarletteHTTPException`, `RequestValidationError`
  (422 con `details`) y `Exception` (500 genérico, `logger.exception` sin traza al cliente).

---

# INTEGRANTE 2 — Botón «Rechazar» con motivo obligatorio (≈ 7:30, tope 9:00)

**Cubre:** criterios 3 y 4. **RF:** VAL-03, SEG-04, SEG-02.

> **[0:00] Presentación.** Soy **[NOMBRE]**. Explico el botón **«Rechazar»**. Lo
> importante no es cambiar el estado, sino que **exige un motivo** y que ese
> motivo queda registrado para el autor. *(Acuerdo previo.)*
>
> **[1:00] Capa visual.** En la tarjeta está `data-reject` → `rechazar(id)`.
> Abre un modal con el título «Rechazar contenido», un `<textarea
> id="reject-reason">` con etiqueta **«Observaciones \*»** y el botón
> «Confirmar rechazo». Si lo dejo vacío aparece: *«Escribe el motivo del rechazo:
> es obligatorio (RNF-SEG-04)»*, código que viene del corte 1. Fíjate en el
> detalle: el JS solo valida **no vacío** con `.trim()`; la longitud mínima la
> valida el backend. Y otra vez: es `localStorage`.
>
> **[2:00] El contrato en Swagger.** En `POST /api/museo/validacion/{id}/rechazar`,
> el *Request body* muestra `RechazoIn` con `observaciones` **required**,
> `minLength: 5` y `maxLength: 1000`. Sale de `contenido_schema.py` con
> `Field(min_length=5, max_length=1000)`. Compáralo con `DecisionIn`, el de
> aprobar: ahí es `str | None = None`. Aprobar no necesita explicación; rechazar sí.
>
> **[2:50] La respuesta 422.** Mando `{}` → **HTTP 422** con
> `{success: false, message: 'Datos inválidos', details: {observaciones: [...]}}`.
> Ese 422 no lo escribe el endpoint: **FastAPI valida antes de entrar** con
> Pydantic v2, y el manejador global `RequestValidationError` arma el `details`
> por campo. Es un código semántico, no un 400 genérico.
>
> **[3:40] Servicio.** Si el cuerpo pasa, el controlador llama a
> `service.rechazar`. `_cargar` repite 403 / 404 / 409. Luego `_observaciones`
> limpia con `.strip()`, y hay una **segunda defensa**: si queda vacío, el
> servicio devuelve su propio 422 — porque cinco espacios pasan `min_length=5`,
> pero `.strip()` los vuelve cadena vacía. Después: estado `rechazado`,
> `id_validador`, `fec_valid`, `observaciones`, `ValidacionLog(accion='rechaza')`,
> notificación `tipo='rechazado'`, un commit y `success(..., 'Contenido rechazado')`.
>
> **[5:10] Lo que NO hace: sumar puntos.** No hay ni una llamada a gamificación
> en todo `rechazar`. Es una regla de negocio: se premia publicar, no rechazar.
>
> **[5:30] Evidencia.** Mando `{'observaciones': 'Falta evidencia fotográfica'}` →
> **200**. Repito el mismo id → **409**. Y `GET …/{id}/historial` muestra
> `accion: 'rechaza'` con el mismo texto: aunque el router solo pide JWT, el
> controlador `historial` exige `rol_nombre == 'admin'` y da 403 si no.
>
> **[6:40] Seguridad.** Errores: 401 sin token, 422 validación, 500 genérico con
> `logger.exception` en el servidor y **sin traza expuesta**. Los esquemas no
> filtran datos sensibles: `AutorOut` expone solo id, nombre y foto, y
> `UsuarioOut` dice literalmente *«Serialización de usuario SIN password_hash»*.

### Respaldo de integrante 2 (no leer)

- Doble validación: JS = respuesta inmediata; Pydantic = contrato de la API;
  servicio = defensa en profundidad para espacios en blanco.
- `validacion_log`: `accion ENUM('aprueba','rechaza')`, `observaciones TEXT`,
  FK a contenido con CASCADE y a admin con RESTRICT (`DDL.sql`).
- `v_bandeja_validacion` filtra `WHERE c.estado='pendiente'`: al rechazar, la fila
  desaparece de la vista.
- El autor lee el motivo en «Mis aportes» (RNF-SEG-04); el admin, en `/historial`.
- Postman: carpeta **Validación (admin)** → request **«Rechazar sin motivo (422)»**.
  Para el 200, duplica el request y cambia el body por un motivo ≥ 5 caracteres.

---

# INTEGRANTE 3 — Botón «Buscar / filtrar» + CRUD y Docker (≈ 8:00, tope 9:30)

**Cubre:** criterios 2, 3, 5 y 6. **RF:** EXP-02.

> **[0:00] Presentación.** Soy **[NOMBRE]**. Explico el buscador, el mapa completo
> de la API y cómo se ejecuta en Docker. *(Acuerdo previo.)*
>
> **[1:00] Capa visual.** En `/buscar` no hay un botón con id: la búsqueda salta
> con el evento `input` de `#search-input`, con `data-filter-category` y
> `data-filter-year`, y con `#search-clear`. En `buscar.js`, `publicados()` lee
> `Store.getContent()` y filtra `status === 'publicado'`; `coincide()` compara
> texto en título y etiquetas, categoría y año, con el caso «Antes de 2019».
> Jinja inyecta los datos desde `simul_data.py`. No hay ni un `fetch`.
>
> **[2:00] La API.** `GET /api/museo/contenido/`, público. Swagger documenta los
> `Query(...)`: `q`, `categoria`, `tipo`, `anio` —mínimo 1900, máximo 2100—,
> `page` (mínimo 1) y `per_page` (1 a 100). Si mando `anio=1800` → **422**: es
> validación declarativa, no un `if` dentro de la función.
>
> **[2:50] Servicio y repositorio.** El controlador normaliza `None` a `page=1`,
> `per_page=12`. `get_publicados` filtra `estado == 'publicado'`, aplica filtros,
> hace `count()` para el total, ordena por `fec_crea.desc()` y aplica
> `offset((page-1)*per_page).limit(per_page)`. El resultado es un `@dataclass
> Pagina`, con `pages = -(-total // per_page)` —el techo de la división.
>
> **[4:00] ORM → SQL.** El texto usa `.ilike('%q%')` sobre `titulo` y `categoria`,
> que en MySQL se traduce a `lower(...) LIKE lower(...)`. El año vive en las
> tablas de subtipo, así que se usa `id_contenido.in_(select(...))` y
> `extract('year', fecha)`. **¿Por qué `IN` y no `JOIN`?** Porque un `JOIN`
> duplicaría la fila de contenido. `estado`, `tipo`, `categoria` y `fec_crea`
> tienen índice en el modelo y en el DDL; el tipo `YEAR` del diagrama se logra
> con `YearType`: `YEAR` en MySQL, `SMALLINT` en el SQLite de desarrollo.
>
> **[5:20] Respuesta y CRUD.** Ejecuto con `q=museo&anio=2024` → **200** con
> `{success, message, data: {items, page, pages, total}}`. Cada item usa los
> mismos campos del prototipo: `tipo`, `titulo`, `categoria`, `anio`, `imagen`,
> `autor`: ahí está la coherencia con el corte 2. Swagger muestra **30 rutas / 37
> operaciones**: GET, POST, **PUT y PATCH** (solo autor o admin) y **DELETE**
> (solo admin), con 200/201, 401, 403, 404 y 422.
>
> **[6:50] Docker y evidencia.** `docker compose up --build` levanta `simul_app`
> en 5000 y `simul_db` (MySQL 8.4) en 3307; el app espera a que la base esté
> *healthy* y el DDL se monta como init script. Cargo con `docker compose exec
> app python db/seed.py`, corro `pytest -q` —**19 pruebas**— y lo veo en DBeaver
> en `127.0.0.1:3307`, `simul_db`, `simul_user`/`simul_password`.

### Respaldo de integrante 3 (no leer)

SQL que genera SQLAlchemy (para mostrar si preguntan):

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

- `Pagina` está en `contenido_repository.py`; `_aplicar_filtros` usa `IN` sobre
  cuatro subtipos con columna `anio` y `extract` para `Evento` y `Noticia`.
- `db/DDL.sql`: 25 tablas + vistas `v_bandeja_validacion` y `v_ranking`; el DDL se
  monta en `/docker-entrypoint-initdb.d/01_schema.sql`.
- Postman: colección **«SIMUL · Museo Digital — API»**, 6 carpetas / 23 requests,
  bearer con `{{token}}`. Credencial admin real: `l.jimenez@unilibre.edu.co` / `1234`.
- El detalle de contenido usa `usuario_opcional`: funciona sin token y solo añade
  `es_favorito` si viene uno.

---

# Preguntas frecuentes (tener a mano; responder 1 o 2 si sobra tiempo)

| Pregunta | Respuesta corta |
|---|---|
| ¿Flask o FastAPI? | Arrancamos en Flask; migramos a FastAPI (lo pide el resumen de criterios): OpenAPI automático, Pydantic y async. Quedan las plantillas Jinja. |
| ¿Por qué el botón no llama a la API? | Coherencia con el corte 2: era un prototipo sin BD. Cambiar el `fetch` en el JS sería lo único necesario; las capas `routes → controllers → services → repositories → models` no se tocan. |
| ¿Quién hace el commit? | El servicio, una vez; el middleware confirma la sesión si status < 400 y hace rollback si no. |
| ¿Cómo saben que los modelos corresponden al E-R? | `db/DDL.sql` (25 tablas, 2 vistas, ENUM, YEAR, FK, índices) se monta como init script; los 25 modelos ORM replican tablas, columnas, relaciones e índices. |
| ¿Dónde se maneja un error inesperado? | Handler global `Exception`: 500 genérico, `logger.exception` en servidor, sin traza al cliente. |
| ¿Qué pasa si un docente aprueba o rechaza? | 403: `rol_nombre` se comprueba en `_cargar`, dentro del servicio. |
| ¿Por qué rechazar no da puntos? | Regla de negocio: solo publicar premia; `rechazar` no llama a gamificación. |

## Errores que NO deben decir

- ❌ "El botón guarda en MySQL" → guarda en `localStorage`; MySQL se demuestra en Swagger/Postman.
- ❌ "El repo hace el commit" → lo hace el servicio; el middleware confirma/hace rollback.
- ❌ "Es Flask" → es FastAPI; Flask fue el corte 2.
- ❌ "Rechazar también da puntos" → solo aprobar suma 100.
- ❌ "El 422 lo lanza Pydantic dentro del endpoint" → FastAPI valida **antes** de entrar y el handler global arma el sobre.
- ❌ Inventar un `require_admin` → no existe; el rol se comprueba con `rol_nombre`.
