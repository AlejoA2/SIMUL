# Evidencias del Backend — Tercer corte

Capturas reales obtenidas contra `http://localhost:5000` (contenedores Docker
`simul_app` + `simul_db`) el **2026-11-24**, con las mismas llamadas que se
muestran en Swagger (`/docs`) y en los videos. Todas se pueden repetir desde
Swagger con *Try it out* o con las mismas `curl`.

**Resumen:** 30 rutas / 37 operaciones OpenAPI · 19 pruebas `pytest` ·
25 tablas + 2 vistas MySQL · Docker reproducible.

| Método HTTP | Cantidad |
|---|---|
| GET | 22 |
| POST | 10 |
| PUT | 2 |
| PATCH | 2 |
| DELETE | 1 |
| **Total** | **37 operaciones en 30 rutas** |

---

## 1. Documentación (Swagger/OpenAPI)

- `GET /docs` → **200** (Swagger UI con todos los endpoints por módulo).
- `GET /openapi.json` → **200**, `paths: 30`, con `GET`, `POST`, `PUT`,
  `PATCH` y `DELETE` representados.

---

## 2. Autenticación y seguridad

### `POST /api/museo/auth/login` → **200**

```json
{"success":true,"message":"Autenticación exitosa","data":{
  "access_token":"eyJhbGciOiJIUzI1NiIs... (token JWT, 163 caracteres)",
  "user":{"id_usuario":5,"nombre":"Ing. Laura Jimenez",
    "correo":"l.jimenez@unilibre.edu.co","rol":"admin",
    "puntos_total":9999,
    "nivel":{"numero":10,"nombre":"Leyenda","puntos_min":6000,"puntos_max":9999}}}}
```

### `GET /api/museo/auth/me` (con `Authorization: Bearer …`) → **200**

```json
{"success":true,"message":"OK","data":{"id_usuario":5,
  "nombre":"Ing. Laura Jimenez","correo":"l.jimenez@unilibre.edu.co",
  "rol":"admin","puntos_total":9999,
  "nivel":{"numero":10,"nombre":"Leyenda", ...}}}
```

- Ninguna respuesta incluye la clave: verificado que los cuerpos no contienen
  `password` ni hash (por ejemplo `GET /api/museo/admin/usuarios`).
- El token viaja en la cabecera `Authorization: Bearer` y vence en 1 hora.

---

## 3. CRUD de contenido (operaciones exitosas con persistencia)

### `POST /api/museo/contenido/` → **201**

```json
{"success":true,"message":"Contenido creado en estado pendiente",
 "data":{"id_contenido":29,"titulo":"Evidencia tercer corte",
   "estado":"pendiente","autor":{"id_usuario":1,"nombre":"Valentina Moreno"}}}
```

### Persistencia en MySQL (misma base que muestra DBeaver)

```sql
SELECT id_contenido, titulo, estado FROM contenido WHERE id_contenido = 29;
-- id_contenido=29 | Evidencia tercer corte | pendiente
SELECT COUNT(*) FROM contenido; -- 29 (antes de crear era 28)
```

### `PUT /api/museo/contenido/29` (actualización completa) → **200**

```json
{"success":true,"message":"Contenido actualizado",
 "data":{"id_contenido":29,"titulo":"Evidencia tercer corte (PUT)",
   "categoria":"Investigacion","estado":"pendiente"}}
```

### `PATCH /api/museo/contenido/29` (actualización parcial) → **200**

```json
{"success":true,"message":"Contenido actualizado",
 "data":{"id_contenido":29,"titulo":"Evidencia tercer corte (PATCH)", ...}}
```

### `DELETE /api/museo/contenido/29` → **200**

```json
{"success":true,"message":"Contenido eliminado","data":null}
```

### `GET /api/museo/contenido/29` después del DELETE → **404**

```json
{"success":false,"message":"Contenido no encontrado"}
```

```sql
SELECT COUNT(*) FROM contenido; -- 28: la base vuelve a su estado inicial
```

### Lectura pública (`GET /api/museo/contenido/`) → **200**

Sobre uniforme con paginación:

```json
{"success":true,"message":"OK","data":{"items":[ ... 3 elementos ... ],
 "page":1,"pages":7,"total":21}}
```

### Con filtros: `GET /api/museo/contenido/?q=proyecto&anio=2023` → **200**

```json
{"success":true,"message":"OK","data":{"items":[
  {"id_contenido":1,"titulo":"Sistema de Monitoreo Ambiental con IoT ...",
   "categoria":"Proyecto","anio":2023,"autor":{"id_usuario":1,"nombre":"Valentina Moreno"}},
  {"id_contenido":12,"titulo":"App para gestion de notas academicas", ...}],
  "page":1,"pages":1,"total":2}}
```

---

## 4. Escenarios de error

| Escenario | Método y ruta | Código | Cuerpo |
|---|---|---|---|
| Sin token en ruta privada | `GET /validacion/bandeja` | **401** | `{"success":false,"message":"No autenticado"}` |
| Rol insuficiente (estudiante) | `GET /validacion/bandeja` | **403** | `{"success":false,"message":"Se requiere rol administrador"}` |
| Identificador inexistente | `GET /contenido/9999` | **404** | `{"success":false,"message":"Contenido no encontrado"}` |
| Correo ya registrado | `POST /auth/register` | **409** | `{"success":false,"message":"El correo ya está registrado"}` |
| Año fuera de rango | `GET /contenido/?anio=1800` | **422** | `{"success":false,"message":"Datos inválidos","details":{"query.anio":["Input should be greater than or equal to 1900"]}}` |
| Clave corta en registro | `POST /auth/register` | **422** | `{"success":false,"message":"Datos inválidos","details":{"password":["String should have at least 8 characters"]}}` |
| Registro válido | `POST /auth/register` | **201** | `{"success":true,"message":"Usuario creado","data":{...}}` |

El `422` siempre nombra el campo con `details` (se arma en
`app/__init__.py`, líneas 128 a 157).

---

## 5. Reglas de negocio

### `GET /api/museo/admin/kpis` (admin) → **200**

```json
{"success":true,"message":"OK","data":{
  "contenido":{"publicado":21,"pendiente":6,"rechazado":1,
    "por_tipo":{"proyecto":2,"premio":2,"acontecimiento":12,
      "evento":1,"avance_investigacion":1,"hall":3}},
  "usuarios_activos":26,"notificaciones_pendientes":3}}
```

Otras reglas demostradas en los videos y cubiertas por `pytest`:

- Aprobar publica el contenido, suma **100** puntos al autor, registra
  `validacion_log` y genera notificación (flujo del video 1).
- Rechazar exige motivo de **5** caracteres como mínimo y no suma puntos
  (flujo del video 2); repetir la decisión responde **409**.
- Nivel e insignias se recalculan con el total de puntos.

---

## 6. Docker y pruebas

```powershell
docker compose ps
# simul_app   simul-app   Up       0.0.0.0:5000->5000/tcp
# simul_db    mysql:8.4   (healthy) 0.0.0.0:3307->3306/tcp

docker compose exec app printenv DATABASE_URL
# mysql+pymysql://simul_user:simul_password@db:3306/simul_db
```

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
# 19 passed
```

`tests/test_app.py` cubre: documentación OpenAPI, páginas HTML,
registro/login/perfil, validaciones de campos, CRUD de contenido,
permisos (401/403), flujo de validación con motivo obligatorio,
gamificación (100 puntos al publicar), funciones sociales y
restricciones de rol.

---

## Cómo repetir estas evidencias

1. `docker compose up -d --build` y `docker compose exec app python db/seed.py`
   (si la base está vacía).
2. Abrir `http://localhost:5000/docs` y ejecutar cada llamada con *Try it out*
   (el login da el token para el botón **Authorize**).
3. Verificar la persistencia en DBeaver (`127.0.0.1:3307`, `simul_db`).
4. Correr `pytest -q`.
