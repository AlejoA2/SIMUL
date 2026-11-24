# Video 3 — Paso a paso: qué probar y dónde

Compañero de [VIDEO_3_BUSCAR.md](VIDEO_3_BUSCAR.md): ese archivo tiene la
narración, este tiene **las acciones**. Los tiempos `[mm:ss]` coinciden con la
narración. Todos los valores de abajo están verificados contra la base.

## Datos fijos (verificados)

| Qué | Valor |
|---|---|
| Catálogo al abrir `/buscar` | **21** publicados |
| Texto `proyecto` en la pantalla | **2** tarjetas (ids 1 y 12) |
| Texto `hackathon` en la pantalla | **2** tarjetas (ids 4 y 27) |
| Filtro de año `2024` en la pantalla | **3** tarjetas (ids 4, 3 y 28) |
| Filtro de categoría `Proyecto` | **2** tarjetas (ids 1 y 12) |
| Búsqueda en Swagger que da filas | `q=proyecto` + `anio=2023` → **2 filas** |
| Búsqueda sin rango | `anio=1800` → **422** (rango 1900-2100) |
| Detalle | `id=1` → **200** con la ficha completa |
| Total de la API | **30 rutas / 37 operaciones** |
| Pendientes en MySQL | **6**: 7, 13, 14, 15, 16, 17 |
| Pruebas | **19 passed** |
| Admin de prueba | `l.jimenez@unilibre.edu.co` / `1234` (id 5) |

---

## 0. Preparación — 10 minutos antes de encender la grabadora

**Terminal 1 (Docker):**

```powershell
docker compose ps                                 # simul_app y simul_db en "Up"
docker compose exec app printenv DATABASE_URL    # debe decir ...@db:3306/simul_db
```

**Terminal 2 (pruebas):**

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q                                         # debe dar: 19 passed
```

**DBeaver** — conexión `127.0.0.1:3307`, base `simul_db`, usuario `simul_user`,
clave `simul_password`:

```sql
SELECT COUNT(*) AS pendientes, GROUP_CONCAT(id_contenido ORDER BY id_contenido) AS ids
FROM contenido WHERE estado = 'pendiente';
-- debe dar: 6 → 7,13,14,15,16,17
```

> Si al abrir una tabla sale `Public key retrieval is not allowed`, aplicá el
> arreglo de la sección 6 de [00_ANTES_DE_GRABAR.md](00_ANTES_DE_GRABAR.md).

**Navegador en ventana incógnito**, siempre `http://localhost:5000` (nunca
`127.0.0.1`, si no el token no se comparte):

- [ ] `/login` con el admin → entra al panel.
- [ ] `/buscar` carga el catálogo (21 tarjetas) **sin errores en la consola (F12)**.
- [ ] En la consola: `SIMULApi.getToken()` → devuelve un token.

**Editor** abierto con los archivos de la tabla de VIDEO_3_BUSCAR.md
(«Antes de iniciar a grabar»), para no perder tiempo buscando.

---

## 1. [00:48–03:28] La página y el navegador — `http://localhost:5000/buscar`

- [ ] Al abrir: **21 tarjetas** y el contador en 21.
- [ ] Escribir `proyecto` → **2 tarjetas** (Sistema de Monitoreo Ambiental… y
      App para gestion de notas…), contador en 2.
- [ ] Escribir `hackathon` → **2 tarjetas**.
- [ ] Borrar el texto y elegir año `2024` en el filtro lateral → **3 tarjetas**.
- [ ] Elegir categoría `Proyecto` → **2 tarjetas**.
- [ ] Botón **Limpiar** → vuelve a 21.
- [ ] En el editor (un archivo por bloque, como dice el guion): `buscar.html`
      50-63, 93-132, 147, 190-193; `buscar.js` 92, 56-69, 71-86; `api.js` 16,
      50-92, 214-226.

## 2. [03:28–06:53] El recorrido de capas — solo señalar en el editor

| Archivo | Líneas | Qué se señala |
|---|---|---|
| `app/routes/contenido_routes.py` | 37-100 | capa 1: GET, validación (422), público |
| `app/controllers/contenido_controller.py` | 20-49 | capa 2: defaults y permiso 403 |
| `app/services/contenido_service.py` | 74-105, 590 | capa 3: reglas, sobre y resumen |
| `app/repositories/contenido_repository.py` | 75-115, 380-459 | capa 4: SQL, total, filtros |
| `app/models/contenido.py` | 6-88 | capa 5: espejo SQLAlchemy |
| `db/DDL.sql` | 94-118, 108-111 | tabla `contenido` e índices |
| `app/__init__.py` | 208-239 | routers con prefijo `/api/museo` |

- [ ] **[06:53] De vuelta en la pantalla** — escribir `proyecto` → contador en **2**
      y las 2 tarjetas; escribir algo sin coincidencias → «Sin resultados» con el
      botón **Limpiar** (vuelve a 21).

---

## 3. [07:28] Swagger — `http://localhost:5000/docs`

Los endpoints de este video son **públicos: no hace falta Authorize**.

**`GET /api/museo/contenido/`** → clic en la fila → **Try it out**:

- [ ] `q=proyecto`, `anio=2023` → **Execute** → `200` con `items` (2 filas,
      ids 1 y 12), `page`, `pages`, `total`.
- [ ] Cambiar a `anio=1800` → **Execute** → `422` con
      `details.query.anio` nombrando el campo («Input should be greater than
      or equal to 1900»).

**`GET /api/museo/contenido/{id}`** → **Try it out**:

- [ ] `id=1` → **Execute** → `200` con la ficha completa (tipo, título,
      categoría, año, imagen, descripción, autor).

**Conteo:**

- [ ] Pestaña nueva → `http://localhost:5000/openapi.json` → decir la cifra:
      **30 rutas, 37 operaciones**.

---

## 4. [08:18] DBeaver — `127.0.0.1:3307` / `simul_db`

**F5 antes de cada lectura** (si no, se ve el resultset anterior).

- [ ] La búsqueda no escribe — filas publicadas que coinciden con Swagger:

```sql
SELECT id_contenido, titulo, categoria, estado
FROM contenido
WHERE estado = 'publicado'
  AND (LOWER(titulo) LIKE '%proyecto%' OR LOWER(categoria) LIKE '%proyecto%');
-- 2 filas: ids 1 y 12 — las mismas que devolvió Swagger
```

- [ ] Índices que sostienen el filtro (también en `db/DDL.sql`, 108 a 111):

```sql
SHOW INDEX FROM contenido;
```

- [ ] Las dos vistas del final del DDL (consultas guardadas, no tablas nuevas):

```sql
SELECT * FROM v_bandeja_validacion;   -- 6 pendientes: 7,13,14,15,16,17
SELECT * FROM v_ranking LIMIT 5;      -- puntos y nivel (arriba: Laura Jimenez)
```

---

## 5. [09:43] Seguridad — un 401 en vivo

- [ ] En Swagger, **sin tocar Authorize**: `GET /api/museo/gamificacion/mi-historial`
      → **Execute** → `401` («No autenticado»).
- [ ] Conseguir el token: `POST /api/museo/auth/login` → **Try it out** → cuerpo:

```json
{"correo":"l.jimenez@unilibre.edu.co","password":"1234"}
```

      → **Execute** → `200` → copiar `access_token` (desde `eyJ…`, sin comillas).

- [ ] Botón 🔒 **Authorize** (arriba a la derecha) → pegar el token **sin la
      palabra `Bearer`** → **Authorize** → **Close**.
- [ ] Repetir `mi-historial` → `200`. Decir: «el catálogo es público; lo
      privado pide token».

---

## 6. [10:18] Pruebas — terminal

- [ ] Con el `.venv` activado: `pytest -q` → **19 passed**.
- [ ] Señalar `tests/test_app.py` línea 20 (documentación OpenAPI) y línea 511
      (ranking y catálogos).

---

## 7. [10:43] Cierre — nada que probar

Los 6 criterios, y te quedás en el buscador.

---

## Si algo falla

| Sintoma | Causa y arreglo |
|---|---|
| La búsqueda da 0 filas | Estás en `anio=2024` → usar **2023** (los publicados con categoría Proyecto son de 2023) |
| `Public key retrieval is not allowed` en DBeaver | Editar conexión → Propiedades del controlador → `allowPublicKeyRetrieval=true` → reconectar (sección 6 de `00_ANTES_DE_GRABAR.md`) |
| El resultset de DBeaver no cambia | F5; y comprobar `printenv DATABASE_URL` |
| `401` en Swagger con token | Venció (dura 1 hora) → repetir el login y el Authorize |
| La página se ve vieja o sin datos | Recargar en ventana incógnito; siempre `localhost`, no `127.0.0.1` |
| El conteo de pendientes no da 6 | Replicar el SQL de restauración de `00_ANTES_DE_GRABAR.md`, sección 2b |
| `pytest` no se encuentra | Activar el entorno primero: `.\.venv\Scripts\Activate.ps1` |
