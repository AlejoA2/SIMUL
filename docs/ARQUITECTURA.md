# SIMUL — Documentación Técnica

**Museo Digital Interactivo** · Facultad de Ingeniería de Sistemas · Universidad Libre

> **Parte 1 de la documentación: Arquitectura general y Backend completo.**
> Contenido analizado leyendo el código fuente real (no hay documentos de diseño previos).

---

## Índice

1. [Visión general: los dos sistemas](#1-visión-general-los-dos-sistemas)
2. [Mapa de requerimientos](#2-mapa-de-requerimientos)
3. [Stack tecnológico](#3-stack-tecnológico)
4. [Arquitectura por capas](#4-arquitectura-por-capas)
5. [Ciclo de vida de la aplicación](#5-ciclo-de-vida-de-la-aplicación)
6. [Backend: código línea por línea](#6-backend-código-línea-por-línea)
7. [Flujos de peticiones](#7-flujos-de-peticiones)
8. [Contrato de la API](#8-contrato-de-la-api)
9. [Infraestructura y despliegue](#9-infraestructura-y-despliegue)
10. [Tests](#10-tests)
11. [Hallazgos y deuda técnica](#11-hallazgos-y-deuda-técnica)
12. [Plan de migración a MySQL](#12-plan-de-migración-a-mysql)
13. [Pendiente de documentar](#13-pendiente-de-documentar)

---

## 1. Visión general: los dos sistemas

El repositorio contiene **dos subsistemas que comparten proceso pero no se hablan**:

```
┌──────────────────────────────────────────────────────────────────┐
│  SISTEMA A — "API del profesor"   (ejercicio del curso)          │
│  auth_bp + product_bp · JWT · MySQL · arquitectura por capas     │
│  7 endpoints REST que funcionan correctamente.                   │
│  ⚠ NINGUNA página del museo los usa.                             │
├──────────────────────────────────────────────────────────────────┤
│  SISTEMA B — "Museo SIMUL"        (el producto real)             │
│  web_bp · 20 rutas HTML · datos mock · localStorage              │
│  21 páginas, 3 roles, gamificación, validación de contenido.     │
│  ⚠ NO tiene base de datos.                                       │
└──────────────────────────────────────────────────────────────────┘
                        ▲
                        └── El puente está PREPARADO pero NO cableado:
                            existe app/static/js/api.js (cliente JWT),
                            pero ningún template lo incluye y no se
                            carga axios en el HTML.
```

Lo confirman los propios docstrings:

```python
# app/routes/web_routes.py:11
# "Este corte es frontend: todavía no hay base de datos conectada, así
#  que cada vista lee de `app/data/simul_data.py`... Cuando se conecte
#  MySQL se sustituye el `import` por llamadas a `app/repositories`"

# app/static/js/pages/login.js:8
# "Cuando exista el backend, este archivo hace:
#      const res = await fetch('/api/auth/login', {...})"
```

**Implicación práctica:** el `Product`/`User` existente es el CRUD de *inventario*
del profesor (`name, price, stock`). **No modela el dominio del museo**, que necesita
`contenido`, `comentario`, `favorito`, `reaccion`, `categoria`, `propuesta`, etc.

### Tamaño del proyecto

| Área | Archivos | Líneas |
|---|---:|---:|
| Backend Python (`app/**/*.py` + `run.py`) | 19 | 2.837 |
| ↳ de los cuales `app/data/simul_data.py` (mock) | 1 | 1.186 |
| Plantillas Jinja (`app/templates/**/*.html`) | 29 | 6.255 |
| JavaScript del núcleo (`app/static/js/*.js`) | 3 | 967 |
| JavaScript por página (`app/static/js/pages/*.js`) | 15 | 3.353 |
| CSS (`app/static/css/*.css`) | 1 | 247 |
| Configuración e infraestructura | 8 | 151 |
| Pruebas (`tests/`) | 1 | 15 |
| **Total (excl. `flask-inventory/`, `docs/` y binarios)** | **76** | **13.825** |

> **Nota de alcance.** El total excluye `flask-inventory/` (andamiaje abandonado),
> `docs/` (esta documentación), las imágenes (`logo-unilibre.png`) y la base SQLite
> de ejemplo (`instance/inventory.db`). **5 plantillas están huérfanas** (no las
> renderiza ninguna ruta): `templates/index.html`, `partials/_auth.html`,
> `partials/_product_form.html`, `partials/_product_table.html` y
> `partials/_alerts.html` (0 bytes) — restos del template de inventario. Las 21
> rutas del museo solo renderizan `pages/*.html`.

---

## 2. Mapa de requerimientos

Están **anotados dentro del código** mediante códigos `RF-` (requisitos funcionales)
y `RNF-` (no funcionales). 65 menciones en 30 archivos.

### Requisitos funcionales

| Código | Requisito | Implementado en |
|---|---|---|
| RF-USR-01 | Registro e inicio de sesión | `pages/login`, `pages/registro` |
| RF-USR-02 | Selección de rol → dashboard por rol | `login.html:167`, `Store.dashboardPath()` (`store.js:116`) |
| RF-USR-03 | Perfil con descripción editable | `pages/perfil` |
| RF-USR-05 | Gestión de usuarios y roles (admin) | `pages/admin_usuarios` |
| RF-EXP-01 | Catálogo de categorías de exploración | `pages/explorar:42`, `simul_data.py:660` |
| RF-EXP-02 | Buscador con filtros (texto/categoría/año) | `pages/buscar`, `buscar.js:6` |
| RF-EXP-04 | Contenido guardado (favoritos) | `pages/favoritos`, `favoritos.js:2` |
| RF-DSH-01 | Dashboard del estudiante | `pages/dashboard_estudiante`, `simul_data.py:856` |
| RF-DSH-02 | Historial de "Mis aportes" + motivos de rechazo | `pages/mis_aportes` |
| RF-DSH-03 | Indicadores / KPIs | `dashboard_admin.html:73`, `index.html:86` |
| RF-DSH-04 | Panel del docente | `dashboard_docente.js:2` |
| RF-COM-01 | Contenido registrado por el docente | `web_routes.py:328` |
| RF-COM-02 | Registro de contenido (formulario según tipo) | `pages/registrar_contenido` |
| RF-PRY-01 | Propuesta de proyecto por el estudiante | `pages/proponer_contenido` |
| RF-PRY-02 | Proyectos que asesora el docente | `dashboard_docente.js:2` |
| RF-VAL-01 | Bandeja de validación del admin | `pages/admin_validacion`, `simul_data.py:885` |
| RF-VAL-03 | Observaciones obligatorias al rechazar | `admin_validacion.js:2` |
| RF-VAL-04 | Acciones automáticas al publicar | `admin_validacion.js:160`, `simul_data.py:973` |
| RF-GAM-01 | Barra de gamificación | `dashboard_estudiante.html:69` |
| RF-GAM-02 | Cómo se ganan puntos | `ranking.html:249` |
| RF-GAM-03 | Sistema de niveles | `simul_data.py:113` |
| RF-GAM-04 | Ranking de la comunidad | `web_routes.py:284` |
| RF-HIS-01 | Línea del tiempo | `simul_data.py:238`, contenido `id="3"` |

### Requisitos no funcionales

| Código | Requisito | Implementado en |
|---|---|---|
| RNF-ACC-01 | Accesibilidad: `alt_text` obligatorio en documentos | `registrar_contenido.html:151`, `adjuntar_evidencias.js:2` |
| RNF-SEG-02 | Control de acceso por rol | `app.js:231 guardPage()`, `_navbar.html:9` |
| RNF-SEG-04 | Sesión obligatoria para ver motivos de rechazo | `app.js:228`, `mis_aportes.html:111` |

---

## 3. Stack tecnológico

### Backend

| Tecnología | Versión | Rol |
|---|---|---|
| Python | 3.12 | Lenguaje |
| Flask | 3.1.1 | Framework web (microframework) |
| Flask-SQLAlchemy | 3.1.1 | ORM — mapea clases Python → tablas |
| Flask-JWT-Extended | 4.7.1 | Autenticación stateless con tokens |
| marshmallow | 4.0.1 | Validación y serialización de JSON |
| PyMySQL | 1.1.1 | Driver puro Python para MySQL |
| cryptography | 45.0.1 | Requerido por MySQL 8 (`caching_sha2_password`) |
| gunicorn | 23.0.0 | Servidor WSGI productivo (3 workers) |
| Werkzeug | 3.1.3 | Hashing de contraseñas |

### Frontend

| Tecnología | Nota |
|---|---|
| Jinja2 | Templates server-side (incluido con Flask) |
| Tailwind CSS | **Vía CDN en runtime** → `base.html:53` advierte que en producción debe compilarse |
| JavaScript plano | `app.js:12`: *"Sin dependencias: JavaScript plano, sin frameworks"* |
| Axios | Preparado en `api.js`, **nunca cargado** → código huérfano |
| Google Fonts | Montserrat (títulos) + Inter (texto), idénticas al prototipo Figma |

### Infraestructura

| Componente | Detalle |
|---|---|
| Dockerfile | `python:3.12-slim` + `gcc`, expone 5000, arranca con Gunicorn |
| docker-compose | `app` + `db` (`mysql:8.4`), healthcheck, volumen `mysql_data`, puerto 3307→3306 |
| BD real (Sistema A) | MySQL `inventory_db` → tablas `users`, `products` |
| BD del museo (Sistema B) | **No existe** → `app/data/simul_data.py` |
| Fallback | SQLite `instance/inventory.db` si no hay `DATABASE_URL` |
| Tests | 1 smoke test con `unittest` |

### Paleta institucional (declarada en `base.html:62-86`)

```
simul-red #C8102E · red-dark #A00D24 · red-light #E8153A
simul-gold #C9A84C · gold-light #E2C06A · gold-dark #A88535
simul-black #1A1A1A · simul-gray #6B7280 · gray-light #F4F4F5 · border #E5E7EB
```

---

## 4. Arquitectura por capas

```
HTTP
 │
 ▼
① RUTA (routes/)          decoradores @bp.get/post, extrae payload, despacha
 │
 ▼
② CONTROLADOR (controllers/)   valida con marshmallow, lee el JWT,
 │                            decide status code, serializa la respuesta
 ▼
③ SERVICIO (services/)     reglas de negocio (hoy: passthrough documentado)
 │
 ▼
④ REPOSITORIO (repositories/)  ÚNICA capa que toca SQLAlchemy
 │
 ▼
⑤ MODELO (models/)         mapeo clase ↔ tabla
 │
 ▼
MySQL (vía extensions.db)

   ✂️  Cada capa solo conoce a la de inmediatamente abajo.
   ✂️  Las respuestas se estandarizan con utils/response.py.
   ✂️  La validación vive en schemas/ (marshmallow).
```

### Por qué `extensions.py` (patrón oficial de Flask)

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()      # ← instanciado AQUÍ, sin aplicación
```

Se crea la instancia **sin** app y se inyecta después con `db.init_app(app)`.
Esto rompe el ciclo de importaciones: los modelos importan `db` desde `app.extensions`,
no desde `app/__init__.py`.

### El contrato de respuestas (`utils/response.py`)

Todo endpoint responde con una de estas dos formas:

```json
{ "success": true,  "message": "Producto creado", "data": { ... } }
{ "success": false, "message": "Datos inválidos", "details": { ... } }
```

---

## 5. Ciclo de vida de la aplicación

```
docker compose up
      │
      ▼
db (mysql:8.4) se inicializa → healthcheck mysqladmin ping (5s)
      │  condition: service_healthy
      ▼
app arranca → gunicorn run:app  (3 workers sync)
      │
      ├── cada worker importa run.py
      │         └── create_app()  (factory)
      │               ├─ Flask(static_folder, template_folder)
      │               ├─ app.config.from_object(Config)
      │               ├─ db.init_app(app)        ← conecta ORM
      │               ├─ JWTManager(app)
      │               ├─ register_blueprint(web_bp)      # raíz
      │               ├─ register_blueprint(auth_bp,  url_prefix="/api/auth")
      │               ├─ register_blueprint(product_bp, url_prefix="/api/products")
      │               └─ db.create_all()         ⚠ RACE CONDITION (ver §11.1)
      ▼
escucha en 0.0.0.0:5000
```

---

## 6. Backend: código línea por línea

### 6.1 `run.py` — punto de entrada (12 líneas)

```python
 1  from app import create_app
 4  app = create_app()
 6  if __name__ == "__main__":
 7      app.run(host="0.0.0.0", port=5000, debug=True)
```

| Línea | Qué hace | Por qué |
|---|---|---|
| 1 | Importa la **factory** `create_app` | Separa la creación de la app del archivo que la expone. |
| 4 | Crea la instancia al importar el módulo | **Esto es lo que busca Gunicorn**: `run:app` = módulo `run`, atributo `app`. |
| 7 | Arranca con Flask en desarrollo | Solo se ejecuta con `python run.py`. En Docker **no se usa**: el `CMD` es Gunicorn. |

> Nota: `debug=True` **nunca llega a Docker** (el CMD usa Gunicorn). Es seguro localmente,
> pero si se ejecutara `python run.py` en producción sería un riesgo (debugger remoto).

---

### 6.2 `app/config.py` — configuración (25 líneas)

```python
 1  import os
 4  class Config:
 6      SQLALCHEMY_DATABASE_URI = os.getenv(
 7          "DATABASE_URL",
 8          "sqlite:///inventory.db"
 9      )
11      SQLALCHEMY_TRACK_MODIFICATIONS = False
13      SECRET_KEY = os.getenv("SECRET_KEY", "development-secret")
18      JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-secret")
23      JWT_ACCESS_TOKEN_EXPIRES = int(
24          os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")
25      )
```

| Líneas | Explicación |
|---|---|
| 6-9 | **URI de conexión** desde la variable de entorno. Si no existe, usa SQLite (`inventory.db` dentro de `instance/`). Por eso el test `test_app.py` pasa sin Docker. |
| 11 | Desactiva el rastreo de eventos de SQLAlchemy (ahorra CPU; no afecta al esquema). |
| 13 | `SECRET_KEY` de Flask (sesiones, tokens CSRF). **Fallback inseguro** — en producción debe exigirse que exista. |
| 18 | Clave con la que se **firma** el JWT. El compose la define como `super-secret-key`. ⚠ Ver §11.3. |
| 23-25 | Expiración del token: 3600 s (1 hora) por defecto. Debe ser **int**; un valor no numérico crashearía al importar. |

---

### 6.3 `app/extensions.py` — instancias globales (4 líneas)

```python
1  from flask_sqlalchemy import SQLAlchemy
4  db = SQLAlchemy()
```

Punto de encuentro de **todas** las capas. Ver §4.

---

### 6.4 `app/__init__.py` — factory (45 líneas)

```python
 1  from flask import Flask
 2  from flask_jwt_extended import JWTManager
 4  from app.config import Config
 5  from app.extensions import db
 7  from app.routes.auth_routes import auth_bp
 8  from app.routes.product_routes import product_bp
 9  from app.routes.web_routes import web_bp
12  def create_app():
14      app = Flask(
15          __name__,
16          static_folder="static",
17          template_folder="templates"
18      )
20      app.config.from_object(Config)
22      db.init_app(app)
24      JWTManager(app)
26      app.register_blueprint(web_bp)
28      app.register_blueprint(auth_bp, url_prefix="/api/auth")
34      app.register_blueprint(product_bp, url_prefix="/api/products")
38      with app.app_context():
40          from app.models.user import User
41          from app.models.product import Product
43          db.create_all()
45      return app
```

| Línea(s) | Explicación |
|---|---|
| 7-9 | Se importan los **blueprints** (módulos de rutas) *antes* de registrarlos. |
| 14-18 | `static_folder` y `template_folder` son los valores por defecto; declararlos explícitamente documenta dónde viven. |
| 20 | `from_object` carga los atributos de `Config` como config de Flask. |
| 22 | **Inyección** del ORM → es el momento en que `db` queda ligado a esta app. |
| 24 | Activa `@jwt_required()`, `create_access_token`, etc. |
| 26-36 | Registro de los 3 blueprints → 20 rutas web + 7 rutas API. |
| 38-43 | **Contexto de aplicación**: fuera de él no hay acceso a `db`. Importa los modelos (para que `db.create_all()` los vea registrados) y crea las tablas. |
| 43 | ⚠ **Origen del race condition** — ver §11.1. |

---

### 6.5 Modelos (`app/models/`)

#### `models/__init__.py` (8 líneas)

```python
1  from app.models.user import User
2  from app.models.product import Product
5  __all__ = ["User", "Product"]
```
Reexporta los modelos → `from app.models import User` funciona y se asegura
de que estén registrados en MetaData antes de `create_all()`.

#### `models/user.py` (59 líneas)

```python
 1  from werkzeug.security import generate_password_hash, check_password_hash
 6  from app.extensions import db
 9  class User(db.Model):
11      __tablename__ = "users"
13      id        = db.Column(db.Integer, primary_key=True)
18      name      = db.Column(db.String(120), nullable=False)
23      email     = db.Column(db.String(180), unique=True, nullable=False, index=True)
30      password_hash = db.Column(db.String(255), nullable=False)
35      products  = db.relationship("Product", back_populates="owner")
40      def set_password(self, password):
42          self.password_hash = generate_password_hash(password)
46      def check_password(self, password):
48          return check_password_hash(self.password_hash, password)
53      def to_dict(self):
55          return {"id": self.id, "name": self.name, "email": self.email}
```

| Línea | Detalle |
|---|---|
| 1-4 | `Werkzeug` (no `werkzeug.security` directo) aporta hash **con salt y verificación**. Nunca se almacena texto plano. |
| 11 | Nombre explícito de tabla (plural, snake_case). |
| 23-27 | `unique=True` + `index=True`: unicidad garantizada **y** búsqueda rápida por correo. El índice nace gracias al unique. |
| 30 | `String(255)` porque `generate_password_hash` con scrypt/pbkdf2 supera con holgura 128 caracteres. |
| 35-38 | Relación 1‑N inversa. Accesible como `user.products`. |
| 40-51 | **Encapsulación**: el resto de la app nunca manipula `password_hash` directamente. |
| 53-59 | Serialización explícita → **omite** `password_hash` por seguridad. Hoy no se usa (se usa `UserSchema`), pero es el escape seguro. |

#### `models/product.py` (59 líneas)

```python
 1  from datetime import datetime
 6  class Product(db.Model):
 8      __tablename__ = "products"
10      id          = db.Column(db.Integer, primary_key=True)
15      name        = db.Column(db.String(150), nullable=False, index=True)
21      description = db.Column(db.Text, nullable=True)
26      price       = db.Column(db.Numeric(12, 2), nullable=False)
31      stock       = db.Column(db.Integer, nullable=False, default=0)
37      created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
43      updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                               onupdate=datetime.utcnow, nullable=False)
50      owner_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
56      owner       = db.relationship("User", back_populates="products")
```

| Línea | Detalle |
|---|---|
| 26 | `Numeric(12,2)` = DECIMAL con 2 decimales → **dinero nunca en float** (error de redondeo). |
| 31 | `default=0` es un valor **de columna** (SQL), no de Python: se aplica al INSERT. |
| 39 | `default=datetime.utcnow` → callable: se ejecuta por fila, no una vez. |
| 46 | `onupdate=datetime.utcnow` → lo actualiza SQLAlchemy al modificar el objeto. **Se aplica solo en UPDATE**. |
| 50-54 | FK a `users.id`, obligatoria → todo producto tiene dueño. |
| 56-59 | `back_populates` enlaza ambos lados: `product.owner` ↔ `user.products`. Si faltara en un lado, SQLAlchemy lanza error. |

---

### 6.6 Schemas — validación y serialización (`app/schemas/`)

marshmallow trabaja en dos direcciones:
* **`load`** → JSON → diccionario validado (entrada)
* **`dump`** → objeto → JSON seguro (salida)

#### `auth_schema.py` (49 líneas)

```python
 8  class RegisterSchema(Schema):
10      name     = fields.Str(required=True, validate=validate.Length(min=2, max=120))
18      email    = fields.Email(required=True)
22      password = fields.Str(required=True, load_only=True,
                             validate=validate.Length(min=8))
31  class LoginSchema(Schema):
33      email    = fields.Email(required=True)
37      password = fields.Str(required=True, load_only=True)
43  class UserSchema(Schema):
45      id = fields.Int();  name = fields.Str();  email = fields.Email()
```

| Línea | Detalle clave |
|---|---|
| 24 | **`load_only=True`** → el campo se acepta al *recibir*, pero **nunca se emite** al responder. Imposible que la contraseña se filtre por un `dump` olvidado. |
| 18 | `fields.Email` valida formato con una regex interna. |
| 43-49 | `UserSchema` es el **DTO de salida**: expone id/name/email y nada más. |

#### `product_schema.py` (86 líneas)

| Línea | Detalle |
|---|---|
| 8-36 | `ProductCreateSchema`: `name` 2-150, `price` ≥ 0, `stock` ≥ 0. **Todo `required=True`**. |
| 23-29 | `price = fields.Decimal(as_string=True)` → el JSON viaja como `"19.99"` (string) para no perder precisión en el cliente, y se convierte a `Decimal` al validar. |
| 20 | `load_default=""` → si llega `null`, lo normaliza a cadena vacía (evita `None` en el modelo). |
| 39-63 | `ProductUpdateSchema`: **mismos campos pero NINGUNO `required`** → permite el PATCH-estilo "envía solo lo que cambias". |
| 66-86 | `ProductResponseSchema`: agrega `owner_id`, `created_at`, `updated_at` — campos que jamás se aceptan como entrada. |

---

### 6.7 Repositorio — única capa que toca SQL (`product_repository.py`, 59 líneas)

```python
 1  from app.extensions import db
 2  from app.models.product import Product
 5  class ProductRepository:
 7      def get_all(self):
 9          return Product.query.order_by(Product.id.desc()).all()
13      def get_by_id(self, product_id):
15          return db.session.get(Product, product_id)
20      def create(self, data, owner_id):
26          product = Product(**data, owner_id=owner_id)
31          db.session.add(product)
33          db.session.commit()
35          return product
37      def update(self, product, data):
43          for key, value in data.items():
45              setattr(product, key, value)
51          db.session.commit()
53          return product
55      def delete(self, product):
57          db.session.delete(product)
59          db.session.commit()
```

| Línea | Explicación |
|---|---|
| 7-11 | `Product.query` es la API legacy de Flask-SQLAlchemy; `.all()` devuelve **lista de objetos**, no dicts. Orden descendente → los más nuevos primero. |
| 13-18 | `db.session.get(Model, id)` es la **API recomendada desde SQLAlchemy 2.0** (usa la caché de identidad; no recomprueba si ya está cargado). Devuelve `None` si no existe. |
| 27 | **`Product(**data, owner_id=owner_id)`** → desempaqueta el dict validado como argumentos nombrados. Aquí saltaría `TypeError` si un schema filtrara mal, no `IntegrityError`. |
| 43-49 | `setattr(obj, key, value)` en bucle = actualización genérica. **Sólo recibe campos ya validados** por `ProductUpdateSchema`, así que no hay riesgo de inyección de columnas. |
| 31-59 | **`commit()` en cada operación** → cada método es transaccionalmente independiente. Consecuencia: no hay rollback explícito; si `commit` lanza, la excepción sube al controlador (que no la atrapa → 500). |

> Los docstrings de esta capa no traen negocio. **Regla:** si una regla como
> *"stock no puede ser negativo"* o *"solo el dueño puede editar"* debe aplicarse
> siempre (aunque llame otro código), va en el **servicio**.

---

### 6.8 Servicio — reglas de negocio (`product_service.py`, 81 líneas)

```python
 6  class ProductService:
 8      def __init__(self):
13          self.repository = ProductRepository()
16      def get_products(self):
22          return self.repository.get_all()
36      def create_product(self, data, owner_id):
45          # Aquí podríamos agregar reglas de negocio.
48          return self.repository.create(data, owner_id)
70      def delete_product(self, product):
79          self.repository.delete(product)
```

**Análisis honesto:** hoy es un **passthrough**. Los docstrings (`product_service.py:45`)
lo reconocen: *«Aquí podríamos agregar reglas de negocio»*.

No es código inútil: es el **lugar correcto** donde entraría, por ejemplo:

```python
def create_product(self, data, owner_id):
    if data["stock"] == 0 and data["price"] > 0:
        raise BusinessError("No se puede publicar sin stock")
    return self.repository.create(data, owner_id)
```

Mantiene desacoplado al controlador del repositorio: si mañana los datos vienen de
otro origen (otra API, otro motor), **cambia el servicio y nada más**.

---

### 6.9 Controladores

#### `auth_controller.py` (186 líneas)

Módulo nivel de módulo (líneas 23-28) — las instancias se crean **una sola vez**
al importar, no por petición:

```python
24  register_schema = RegisterSchema()
26  login_schema    = LoginSchema()
28  user_schema     = UserSchema()
```

**`register()` — líneas 33-106:**

| Líneas | Paso | Fallo posible → respuesta |
|---|---|---|
| 43-55 | `register_schema.load(payload)` | `ValidationError` → **422** con `exc.messages` en `details` |
| 62-72 | Busca usuario por email | Ya existe → **409** *«El correo ya está registrado»* |
| 79-90 | `User(...)` + `user.set_password()` | Nunca guarda contraseña en claro |
| 93-95 | `add()` + `commit()` | |
| 102-106 | `success(user_schema.dump(user), ..., 201)` | |

> **Detalle de seguridad (líneas 143-148 y 155-162):** en `login`, usuario inexistente y
> contraseña incorrecta devuelven **el mismo** `401 «Credenciales inválidas»`.
> Si fueran distintos, un atacante podría enumerar correos registrados (*user enumeration*).

**`login()` — líneas 109-186:**

| Líneas | Paso |
|---|---|
| 119-131 | Valida email/contraseña → **422** |
| 138-148 | Busca el usuario → **401** si no existe |
| 155-162 | `check_password()` → **401** si no coincide |
| 169-171 | `create_access_token(identity=str(user.id))` |
| 178-186 | Devuelve `{access_token, user}` |

> **Línea 170: `identity=str(user.id)`.** Obligatorio: en Flask-JWT-Extended ≥4 el
> identidad debe ser *string* (los claims de id son JWT estándar y deben ser strings).
> Al recibirlo se revierte con `int()` (`product_controller.py:128`).

#### `product_controller.py` (262 líneas)

Módulo (líneas 23-32): `response_schema = ProductResponseSchema(many=True)`
→ `many=True` hace que `dump()` reciba una **lista**.

| Método | Líneas | Firma | Lógica |
|---|---|---|---|
| `get_all` | 47-62 | — | Servicio → `dump(many)` → `success()` |
| `get_by_id` | 65-91 | `product_id` | `None` → **404** |
| `create` | 94-153 | `payload` | load(**422**) → `get_jwt_identity()` → servicio → **201** |
| `update` | 156-225 | `id`, `payload` | 404 → load(**422**) → `if not data` → **400** → servicio |
| `delete` | 228-262 | `id` | 404 → servicio → `success(None, ...)` |

**Secuencia de `create` (líneas 109-153):**

```python
109      try:
111          data = create_schema.load(payload)      # ← validación
115      except ValidationError as exc:
117          return error("Datos inválidos", 422, exc.messages)

128      owner_id = int(get_jwt_identity())          # ← quién pidió (el token)
137      product  = self.service.create_product(data, owner_id)
147      return success(single_schema.dump(product), "Producto creado", 201)
```

**Guarda contra `PUT` vacío (líneas 202-207):**

```python
202      if not data:
204          return error("No hay datos para actualizar", 400)
```
`update_schema.load({})` **no lanza** (ningún campo es `required`) y devuelve `{}`.
Por eso esta comprobación es necesaria: sin ella un `PUT {}` llegaría al servicio y
haría un `commit()` sin cambios. ✅ Correcto — parece código muerto, pero no lo es.

> ⚠ **Deuda de seguridad:** `update` y `delete` **no verifican que el producto
> pertenezca a quien hace la petición**. Cualquier usuario autenticado con JWT puede
> editar o borrar productos de otros. Hoy el museo no usa esta API, pero es un fallo
> real del Sistema A → ver §11.4.

---

### 6.10 `utils/response.py` (42 líneas)

```python
 1  def success(data=None, message="OK", status=200):
11      return {"success": True, "message": message, "data": data}, status
18  def error(message, status=400, details=None):
28      response = {"success": False, "message": message}
37      if details:
39          response["details"] = details
42      return response, status
```

Devuelve **tuplas** `(dict, código)` — el formato que Flask entiende directamente.

| Detalle | Explicación |
|---|---|
| `data=None` | Permite respuestas sin cuerpo (ej. DELETE → `success(None, "Producto eliminado")`). |
| `if details:` (línea 37) | En vez de `is not None` → un `{}` vacío también se omite. Evita `"details": {}` en errores sin información. |
| `details` | Solo lo usan los `ValidationError` de marshmallow → contiene el dict de campo→mensaje. |

---

### 6.11 Rutas

#### `auth_routes.py` (68 líneas)

```python
15  auth_bp = Blueprint("auth", __name__)
22  controller = AuthController()          # ← instancia única, a nivel módulo
29  @auth_bp.post("/register")
30  def register():
38      payload = request.get_json(silent=True) or {}
45      return controller.register(payload)
54  @auth_bp.post("/login")
55  def login():
61      payload = request.get_json(silent=True) or {}
66      return controller.login(payload)
```

| Línea | Detalle |
|---|---|
| 22 | El controlador es **stateless**, así que compartirlo entre peticiones es seguro y ahorra memoria. |
| 38-40 | `get_json(silent=True)` devuelve `None` en vez de abortar 400 si el body no es JSON → combinado con `or {}` **nunca** lanza. El 422 lo decide el schema, con un mensaje mejor. |

#### `product_routes.py` (122 líneas)

```python
19  product_bp = Blueprint("products", __name__)
26  controller = ProductController()

33  @product_bp.get("/")                  @jwt_required()
34  @product_bp.get("/<int:product_id>")   @jwt_required()
50  @product_bp.post("/")                 @jwt_required()
67  @product_bp.put("/<int:product_id>")   @jwt_required()
89  @product_bp.delete("/<int:product_id>")@jwt_required()
112
```

| Línea | Detalle |
|---|---|
| 34, 51, 68, 90, 113 | `@jwt_required()` es el **decorador externo**: valida el token **antes** de ejecutar la función. Sin token o inválido → 401 sin tocar el controlador. |
| 50 | `<int:product_id>` → convertidor de tipo. `/api/products/abc` **404** (no llega a la ruta), distinto de un 422 de validación. |
| 33 | Ruta `"/"` con `url_prefix="/api/products"` → **`/api/products/`** (con barra final; Flask redirige la versión sin barra). |

---

### 6.12 `routes/web_routes.py` — el Sistema B (467 líneas)

Su docstring (líneas 1-24) es la mejor documentación del proyecto. Resume:

* Solo vistas HTML; la API del profesor *«sigue intacta y convive con este blueprint»*.
* No hay BD conectada → todo lee de `app.data.simul_data`.
* Las páginas privadas **no se protegen en servidor** (la sesión vive en `localStorage`);
  la guarda es `guardPage()` en `app.js`.

**Helper común (líneas 45-55):**

```python
45  def _common_context():
53      return {"role_labels": data.ROLE_LABELS}
```
`role_labels` viaja a **todas** las páginas para que la navbar pinte
"Estudiante/Docente/Administrador" sin otra petición.

**Las 20 rutas:**

| # | Método/URL | Función | Línea | Datos que inyecta |
|---|---|---|---:|---|
| 1 | `GET /` | `index` | 62 | `HOME_STATS`, `HOME_QUICK_ACCESS`, `HALL_OF_FAME`, `HOME_HERO_IMAGE` |
| 2 | `GET /explorar` | `explorar` | 78 | `EXPLORE_CATEGORIES` + `cat` de querystring |
| 3 | `GET /buscar` | `buscar` | 91 | categorías, años, `CONTENT_ITEMS`, `CATEGORY_SLUG_MAP` |
| 4 | `GET /contenido/<id>` | `detalle_contenido` | 111 | `item`, `relacionados[3]`, `TIMELINE_EVENTS`, comentarios, reacciones |
| 5 | `GET /login` | `login` | 160 | `ROLE_DATA`, `DEMO_PASSWORD` |
| 6 | `GET /registro` | `registro` | 175 | `ROLE_DATA` |
| 7 | `GET /dashboard/estudiante` | `dashboard_estudiante` | 191 | aportes, ranking ordenado, posición, niveles |
| 8 | `GET /proponer-contenido` | `proponer_contenido` | 234 | docentes, categorías, tecnologías, años |
| 9 | `GET /mis-aportes` | `mis_aportes` | 250 | `MY_ITEMS` |
| 10 | `GET /favoritos` | `favoritos` | 263 | `seed_favorites` (4 ids publicados) |
| 11 | `GET /ranking` | `ranking` | 284 | ranking recalculado + `rank` |
| 12 | `GET /mi-perfil` | `perfil` | 311 | `BADGES_CATALOG` |
| 13 | `GET /dashboard/docente` | `dashboard_docente` | 328 | contenido por autor + agrupado por estado |
| 14 | `GET /registrar-contenido` | `registrar_contenido` | 359 | `TEACHER_CONTENT_TYPES`, `TEACHER_FORMS` |
| 15 | `GET /adjuntar-evidencias` | `adjuntar_evidencias` | 374 | `FILE_ICONS` |
| 16 | `GET /dashboard/admin` | `dashboard_admin` | 391 | `KPI_DATA`, `MONTHLY_CONTENT`, `IMPACT_METRICS` |
| 17 | `GET /admin/contenido` | `admin_contenido` | 408 | `CONTENT_ITEMS`, `SEED_REACTIONS` |
| 18 | `GET /admin/validacion` | `admin_validacion` | 423 | `VALIDATION_QUEUE`, `CONTENT_ITEMS` |
| 19 | `GET /admin/publicacion` | `admin_publicacion` | 439 | `PUBLISH_CHECKLIST` |
| 20 | `GET /admin/usuarios` | `admin_usuarios` | 453 | `SYSTEM_USERS`, `USER_ROLES`, `ROLE_COLORS` |

**Los tres fragmentos con lógica real (el resto es passthrough):**

```python
# 111-126 · Búsqueda del detalle O 404
item = next((c for c in data.CONTENT_ITEMS if c["id"] == contenido_id), None)
if item is None:
    return render_template("pages/contenido_no_encontrado.html", ...), 404
```
`next(iterador, None)` → busca el primero que cumpla o devuelve `None` **sin iterar todo** si hay coincidencia temprana.

```python
# 120-138 · Relacionados: publicados, distintos de él mismo, máximo 3
relacionados = [c for c in data.CONTENT_ITEMS
                if c["id"] != contenido_id and c["status"] == "publicado"][:3]
```

```python
# 196-215 · Posición en el ranking (SIN lógica en el template)
ordenados  = sorted(data.RANKING_DATA, key=lambda r: r["points"], reverse=True)
posicion   = next((i for i, fila in enumerate(ordenados, start=1)
                   if fila["name"] == data.ROLE_DATA["student"]["name"]), None)
```
Comentario del propio autor (línea 201): *«Se calcula en Python para no dejar
lógica de negocio dentro del template»* → **buena práctica**.

```python
# 340-343 · dashboard_docente: agrupar por estado en una sola comprensión
estados = {estado: [c for c in contenido if c["status"] == estado]
           for estado in ("publicado", "pendiente", "rechazado")}
```

⚠ **Nota de mantenimiento (línea 198):** los aportes del estudiante se filtran con
`"Valentina" in c["author"]` — **hardcodeado**. Lo mismo en `dashboard_docente`
(líneas 336-337: `"Patiño" in ... or "Patino" in ... or "Ruiz" in ...`).
Falla si cambian los datos de demostración.

---

## 7. Flujos de peticiones

### 7.1 Registro — `POST /api/auth/register`

```
Cliente (JSON)             Ruta                Controlador
────────────────  ──────────────────────  ──────────────────────────────
{"name":"Ana",         auth_routes:29         auth_controller:33
 "email":"a@b.co",     get_json(silent)   →   43  register_schema.load()
 "password":"12345678"} or {}                   │ ✓ ok
                                                 │ ✗ ValidationError → 422
                                                 62  User.query.filter_by(email)
                                                   │ existe → 409
                                                 79  User(name=..., email=...)
                                                 88  set_password()  → hash+salt
                                                 93  db.session.add/commit
                                                 102 success(user_schema.dump(user),
                                                            "Usuario creado", 201)
Cliente ◀── {"success":true,"data":{"id":1,...}} 201
```

### 7.2 Login — `POST /api/auth/login`

```
119  login_schema.load()            ✗ → 422
138  User.query.filter_by(email)    no existe → 401
155  user.check_password()          ✗ → 401 (mismo mensaje: anti enumeration)
169  create_access_token(identity=str(user.id))   ← firma con JWT_SECRET_KEY
178  {access_token, user} → 200
```

### 7.3 CRUD de productos — `POST /api/products/`

```
① product_routes:67-82   @jwt_required() valida Bearer → ✗ sin token = 401
                          get_json(silent=True) or {}
② product_controller:94  create_schema.load()         ✗ → 422
                         int(get_jwt_identity())      ← el id del token
                         ProductService() → create_product(data, owner_id)
③ product_service:36     return repository.create(data, owner_id)
④ product_repository:26  Product(**data, owner_id=owner_id)
                         db.session.add() + commit()  → INSERT en MySQL
⑤ product_controller:147 single_schema.dump(product) + 201
```

---

## 8. Contrato de la API

Base: **`/api`** · Auth: **`Authorization: Bearer <token>`** · Formato: JSON

| Método | Ruta | Auth | Éxito | Errores |
|---|---|---|---|---|
| POST | `/api/auth/register` | — | 201 | 422, 409 |
| POST | `/api/auth/login` | — | 200 `{access_token, user}` | 422, 401 |
| GET | `/api/products/` | ✅ | 200 `[...]` | 401 |
| GET | `/api/products/<id>` | ✅ | 200 `{...}` | 401, 404 |
| POST | `/api/products/` | ✅ | 201 | 401, 422 |
| PUT | `/api/products/<id>` | ✅ | 200 | 401, 404, 422, 400 |
| DELETE | `/api/products/<id>` | ✅ | 200 `data:null` | 401, 404 |

**Esquema de error:**
```json
{ "success": false, "message": "Datos inválidos", "details": {"email": ["Not a valid email address."] } }
```

---

## 9. Infraestructura y despliegue

### `Dockerfile` (23 líneas)

```dockerfile
 1  FROM python:3.12-slim
 4  ENV PYTHONDONTWRITEBYTECODE=1     # no genera .pyc (imagen limpia)
 6  ENV PYTHONBUFFERED=1              # logs sin buffer
 8  WORKDIR /app
10  RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*
15  COPY requirements.txt .
17  RUN pip install --no-cache-dir -r requirements.txt   # ← capa cacheada
19  COPY . .                           # ← copia solo si cambió lo anterior
21  EXPOSE 5000
23  CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","3","run:app"]
```

| Decisión | Comentario |
|---|---|
| **Orden `COPY requirements` → `pip install` → `COPY . .`** | Clave: cambiar el código **no** reinstala las dependencias. Solo se revalida la capa 19. |
| `gcc` | Compila paquetes con extensiones C (`cryptography` trae wheel, pero por si acaso). |
| `rm -rf /var/lib/apt/lists/*` | Reduce la imagen ~10 MB. |
| `--workers 3` | 3 procesos = 3x memoria de app, pero atiende concurrencia real (los `sync` workers son bloqueantes). **→ es la causa del race §11.1** |
| `CMD` array (JSON) | Forma *exec*: sin `sh` intermedio, Gunicorn recibe los señales (`docker stop`) correctamente. |

### `docker-compose.yml` (41 líneas)

| Sección | Línea | Detalle |
|---|---|---|
| `app.build: .` | 3 | Usa `Dockerfile` de la raíz |
| `app.ports: 5000:5000` | 6 | API y páginas |
| `app.environment` | 8-9 | `DATABASE_URL` apunta al host **`db`** (nombre del servicio = DNS interno de Compose) y `JWT_SECRET_KEY` |
| `depends_on: condition: service_healthy` | 11-12 | **Espera a que MySQL acepte conexiones** antes de arrancar la app |
| `db.image: mysql:8.4` | 15 | LTS de MySQL |
| `db.ports: 3307:3306` | 23 | 3307 evita chocar con un MySQL local del host |
| `db.volumes: mysql_data:/var/lib/mysql` | 25 | **Persistencia**: `docker compose down` no borra datos |
| `healthcheck` | 27-38 | `mysqladmin ping` cada 5s, timeout 2s, 20 reintentos (~100 s de tolerancia) |

**Uso:**
```bash
docker compose up -d --build   # arrancar
docker compose logs -f app     # ver logs
docker compose down            # detener (conserva datos)
docker compose down -v         # detener BORRANDO la BD
```

---

## 10. Tests

```python
 7  class AppConfigSmokeTest(unittest.TestCase):
 8      def test_app_creates_with_sqlite_default(self):
 9          os.environ.pop("DATABASE_URL", None)
10          app = create_app()
11          self.assertIn("sqlite", app.config["SQLALCHEMY_DATABASE_URI"])
```

* **Smoke test de configuración**: verifica que sin `DATABASE_URL` la app usa SQLite.
* Al llamar `create_app()` ejecuta `db.create_all()` → por eso existe
  `instance/inventory.db` en el repositorio.
* **Cobertura real: casi nula.** No hay tests de rutas, auth, JWT, ni validación.

**Cómo ejecutarlo:**
```bash
python -m unittest discover -s tests -v
```

---

## 11. Hallazgos y deuda técnica

### 11.1 🔴 Race condition al arrancar (reproducido)

**Síntoma** (primer arranque con BD vacía):
```
sqlalchemy.exc.OperationalError: (1050, "Table 'products' already exists)
[ERROR] Reason: Worker failed to boot.
```

**Causa:** `app/__init__.py:43` ejecuta `db.create_all()` dentro de `create_app()`.
Con `--workers 3`, Gunicorn importa la app en **3 procesos simultáneos** que compiten
por crear las tablas. `create_all()` primero *consulta* si la tabla existe y luego la
*crea* (*check-then-create*) — **no es atómico**, y el DDL de MySQL no se puede
revertir. Dos workers chocan → worker muere (`exit 3`) → Gunicorn reinicia el master
→ el 2º intento encuentra las tablas y arranca.

Solo afecta al **primer arranque con volumen vacío**, pero se repite en cada despliegue limpio.

**Correcciones posibles** (orden de preferencia):
1. Script de arranque que crea las tablas **una vez** antes de lanzar Gunicorn.
2. `gunicorn --preload` (la app se carga en el master antes del fork) + `db.engine.dispose()`.
3. `try/except OperationalError` alrededor de `create_all()` (tapa el síntoma).

### 11.2 🔴 Seguridad client-side en el museo

`web_routes.py:19`: *«Las páginas privadas no se protegen en el servidor»*.
`guardPage()` (`app.js:231`) es JS de navegador → **burlable** escribiendo la URL:
`localhost:5000/dashboard/admin` responde 200 a cualquiera.
**Migración:** decorador `@jwt_required()` o `@login_required` en esas rutas.

### 11.3 🟠 Secretos en texto plano

| Dónde | Valor | Riesgo |
|---|---|---|
| `docker-compose.yml:9` | `JWT_SECRET_KEY: super-secret-key` | Cualquiera que lo lea puede **firmar tokens válidos** |
| `docker-compose.yml:19-21` | `inventory_password`, `root_password` | Acceso total a la BD |
| `simul_data.py:61` | `DEMO_PASSWORD = "1234"` (al cliente) | Aceptable en demo |
| `config.py:14,19` | defaults `development-secret` | Se activan si falta la env var |

`/api/products` puede firmarse un token con `super-secret-key` → acceso total.
**Solución:** variables en `.env` (ya está en `.dockerignore`).

### 11.4 🟠 Falta de autorización por recurso (IDOR)

`product_controller.update()` / `delete()` **no comparan** `product.owner_id` con
`get_jwt_identity()`. Cualquier usuario autenticado puede editar/borrar productos
ajenos. Faltaría:
```python
if product.owner_id != int(get_jwt_identity()):
    return error("No autorizado", 403)
```

### 11.5 🟠 `Dockerfile` con `COPY . .` no excluye `instance/`

`.dockerignore` no lista `instance/` → `instance/inventory.db` (20 KB, SQLite) entra
en la imagen. Inofensivo (no se usa con MySQL) pero ensucia la imagen.
(Igualmente `.gitignore` debería impedir commitearlo.)

### 11.6 🟡 Otros

| Hallazgo | Detalle |
|---|---|
| **`api.js` huérfano** | No se incluye en ninguna plantilla y no se carga `axios` → el cliente JWT está **muerto**. |
| **`_alerts.html` vacío** (0 B) | Incluido en algún template pero sin contenido. |
| **Filtros por nombre hardcodeados** | `web_routes.py:198` (`"Valentina"`) y `336-337` (`"Patiño"/"Patino"/"Ruiz"`). |
| **`flask-inventory/`** | Restos del template original: 4 archivos **0 bytes** + copias de dockerfile/compose. Basura. |
| **`SIMUL/`** (raíz) | Carpeta **vacía**. |
| **Sin manejo de excepciones en BD** | Ningún `try/except` alrededor de `commit()` → un `IntegrityError` se convierte en **500** sin cuerpo útil. |
| **`db.create_all()` no migra** | Cambia la estructura de tablas solo si son nuevas. **No altera columnas existentes** → hará falta Alembic. |
| **Tailwind por CDN** | `base.html:59` — el propio código avisa que debe compilarse para producción. |
| **`SECRET_KEY` fallback** | `config.py:14` devuelve `development-secret` en silencio. |
| **Tests mínimos** | 1 test; 0 tests de API. |

---

## 12. Plan de migración a MySQL

### 12.1 Por qué `products` no sirve

| El Sistema A tiene | El museo necesita |
|---|---|
| `users` (id, name, email, password_hash) | `usuarios` con **rol**, estado activo, puntos, nivel, insignias, descripción, avatar |
| `products` (name, price, stock) | `contenido` con **estado** (pendiente/publicado/rechazado), categoría, autor, año, imágenes, tecnologías |

Los campos de `Product` son **incompatibles** con el dominio: no hay `price`/`stock`
en un museo, y sí hace falta `status`, `category_id`, `alt_text`…

### 12.2 Esquema propuesto (deducido de `store.js`)

Cada clave de `localStorage` documenta su tabla futura:

```sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(180) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,      -- Werkzeug
  role ENUM('student','teacher','admin','graduate') NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  points INT DEFAULT 0, level INT DEFAULT 1,
  description TEXT, avatar VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL, slug VARCHAR(80) NOT NULL UNIQUE,
  icon VARCHAR(40), color VARCHAR(20)
);

CREATE TABLE contenido (
  id VARCHAR(32) PRIMARY KEY,              -- ids tipo "1","2" del mock
  title VARCHAR(180) NOT NULL,
  description TEXT, body LONGTEXT,
  year SMALLINT, image VARCHAR(255),
  category_id INT NOT NULL, author_id INT NOT NULL,
  status ENUM('pendiente','publicado','rechazado') DEFAULT 'pendiente',
  rejection_reason TEXT NULL,               -- RNF-SEG-04
  alt_text VARCHAR(255) NULL,               -- RNF-ACC-01
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categorias(id),
  FOREIGN KEY (author_id)  REFERENCES usuarios(id)
);

CREATE TABLE favoritos (
  usuario_id INT, contenido_id VARCHAR(32),
  PRIMARY KEY (usuario_id, contenido_id),    -- tabla FAVORITO (store.js:124)
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

CREATE TABLE comentarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  contenido_id VARCHAR(32) NOT NULL,
  autor_id INT NOT NULL,
  parent_id INT NULL,                        -- FK autoreferenciada (store.js:231)
  body TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES comentarios(id) ON DELETE CASCADE
);

CREATE TABLE reacciones (
  contenido_id VARCHAR(32) PRIMARY KEY,
  emoji VARCHAR(8) DEFAULT '👏',
  count INT DEFAULT 0
);

CREATE TABLE propuestas (
  id VARCHAR(40) PRIMARY KEY,                -- 'prop-' + Date.now()
  autor_id INT NOT NULL, teacher_id INT NOT NULL,
  category_id INT, year SMALLINT,
  status ENUM('pendiente','aprobada','rechazada') DEFAULT 'pendiente',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (autor_id) REFERENCES usuarios(id)
);
```

*(Niveles, insignias, ranking, línea del tiempo, Hall de la Fama y KPIs →
pueden seguir siendo derivados o catálogos de solo lectura.)*

### 12.3 Secuencia de migración recomendada

1. **Arreglar el race** de `create_all()` (§11.1) — *requisito previo*.
2. **Crear los modelos reales** (`app/models/contenido.py`, `usuario.py`, …).
3. **Añadir Alembic** (`flask db migrate/upgrade`) — `create_all()` no migra.
4. **Añadir rol a `Usuario`** + `@roles_required("admin")` en rutas de `/admin/*`.
5. **Mover `simul_data.py` a un seed** (script que puebla la BD la primera vez).
6. **Reescribir `web_routes.py`**: cada `data.X` → `Repository.X()`. El resto del
   proyecto **no cambia** (es lo que promete `data/__init__.py:14`).
7. **Sustituir el login simulado** por `POST /api/auth/login` + guardar
   `access_token` → ya existe `login.js:8-17` con el código previsto.
8. **Cablear `api.js`** en `base.html` (y cargar axios) para que las llamadas
   existentes (`Store` → API) funcionen.
9. **Proteger en servidor** las rutas privadas (§11.2).
10. **Añadir tests**: 1 por endpoint + auth.

---

## 13. Pendiente de documentar

| Parte | Contenido | Archivos |
|---|---|---|
| **Parte 2 — Datos del museo** | `simul_data.py` (1.123 líneas, 14 secciones): entidades, campos y reglas | `app/data/` |
| **Parte 3 — Frontend** | `app.js`, `store.js`, `api.js`, patrón de página, `_navbar.html` | `app/static/js/`, `templates/partials/` |
| **Parte 4 — Páginas** | 21 HTML + 15 JS, recorrido por rol | `templates/pages/`, `js/pages/` |
| **Parte 5 — Estilos** | `app.css` (247 líneas) y clases `simul-*` | `app/static/css/` |

---

*Documento generado a partir del análisis del código fuente.*
*Backend: 19 archivos Python · 2.837 líneas · todo analizado.*
