# SIMUL — Documentación Técnica

> **Parte 2: Los datos del museo** (`app/data/simul_data.py`)
> Continúa a [`ARQUITECTURA.md`](./ARQUITECTURA.md) (Parte 1: arquitectura y backend).

---

## Índice

1. [Qué es este archivo](#1-qué-es-este-archivo)
2. [Inventario completo](#2-inventario-completo)
3. [Modelo de datos deducido](#3-modelo-de-datos-deducido)
4. [Sección por sección](#4-sección-por-sección)
5. [Diccionario de datos de `CONTENT_ITEMS`](#5-diccionario-de-datos-de-content_items)
6. [Convenciones y vocabularios](#6-convenciones-y-vocabularios)
7. [Reglas de negocio embebidas](#7-reglas-de-negocio-embebidas)
8. [Cómo se consume](#8-cómo-se-consume)
9. [Inconsistencias detectadas](#9-inconsistencias-detectadas)
10. [Esquema MySQL definitivo](#10-esquema-mysql-definitivo)

---

## 1. Qué es este archivo

`app/data/simul_data.py` es la **única fuente de verdad** del museo mientras no
haya base de datos. Lo declara `app/data/__init__.py:9`:

> *"`simul_data.py` es la única fuente de verdad: las vistas lo importan para pintar
> el HTML y lo entregan al navegador con el filtro `tojson`... Al conectar MySQL este
> paquete desaparece y sus datos pasan a leerse desde `app/repositories`."*

| Métrica | Valor |
|---|---|
| Líneas | **1.186** |
| Constantes de nivel de módulo | **37** |
| Secciones (`# ===`) | **14** |
| Entidades "de tabla" | **10** (`CONTENIDO`, `USUARIO`, `NIVEL`, `INSIGNIA`, `COMENTARIO`, `REACCION`, `FAVORITO`, `HISTORIA`, `PROPUESTA`, …) |
| Registros totales | **~220** |
| Código ejecutable | **0** — solo literales (dicts, listas) |

Lo último es clave: el archivo **no tiene funciones, clases ni imports**. Es pura
declaración de datos. Por eso su migración a MySQL es "mecánica": no hay lógica que
reescribir, solo transporte.

**Característica de estilo:** casi todos los textos evitan tildes (`Linea`, `Anos`,
`Investigacion`). Se hizo para evitar problemas de codificación; el HTML sí las tiene.
Es una deuda estética, no funcional.

---

## 2. Inventario completo

| # | Sección | Constante | Tipo | Registros | Líneas |
|---|---|---|---:|---:|---:|
| 1 | Usuarios de demostración | `ROLE_DATA` | dict | 3 | 8-57 |
| 1 | ↳ | `DEMO_PASSWORD` | str | — | 61 |
| 2 | Docentes asesores | `TEACHERS` | list | 4 | 68-109 |
| 3 | Gamificación | `LEVEL_NAMES` | dict | 11 | 118-130 |
| 3 | ↳ | `LEVEL_TABLE` | list | 10 | 133-144 |
| 3 | ↳ | `RANKING_DATA` | list | 9 | 146-219 |
| 3 | ↳ | `BADGES_CATALOG` | list | 8 | 222-231 |
| 4 | Línea del tiempo | `TIMELINE_EVENTS` | list | 11 | 238-339 |
| 5 | Contenido del museo | `CONTENT_ITEMS` | list | **11** | 346-594 |
| 6 | Hall de la Fama | `HALL_OF_FAME` | list | 3 | 601-656 |
| 7 | Exploración | `EXPLORE_CATEGORIES` | list | 7 | 663-720 |
| 7 | ↳ | `CATEGORY_SLUG_MAP` | dict | 6 | 724-731 |
| 7 | ↳ | `SEARCH_CATEGORIES` | list | 7 | 734-742 |
| 7 | ↳ | `SEARCH_YEARS` | list | 8 | 744-753 |
| 8 | Portada | `HOME_STATS` | list | 4 | 760-765 |
| 8 | ↳ | `HOME_QUICK_ACCESS` | list | 6 | 767-810 |
| 8 | ↳ | `HOME_HERO_IMAGE` | str | — | 813-816 |
| 9 | Aportes del estudiante | `MY_ITEMS` | list | 3 | 823-854 |
| 9 | ↳ | `STUDENT_ACTIVITY` | list | 4 | 857-878 |
| 9 | ↳ | `STUDENT_MAX_POINTS` | int | — | 881 |
| 10 | Validación admin | `VALIDATION_QUEUE` | list | 5 | 888-971 |
| 10 | ↳ | `PUBLISH_CHECKLIST` | list | 6 | 974-981 |
| 11 | Indicadores admin | `KPI_DATA` | list | 6 | 988-995 |
| 11 | ↳ | `MONTHLY_CONTENT` | list | 12 | 997-999 |
| 11 | ↳ | `MONTHS_LABELS` | list | 12 | 1001-1004 |
| 11 | ↳ | `IMPACT_METRICS` | list | 4 | 1006-1011 |
| 12 | Gestión de usuarios | `SYSTEM_USERS` | list | 7 | 1018-1026 |
| 12 | ↳ | `USER_ROLES` | list | 4 | 1028 |
| 12 | ↳ | `ROLE_COLORS` | dict | 4 | 1030-1035 |
| 12 | ↳ | `ROLE_LABELS` | dict | 3 | 1037-1041 |
| 13 | Formularios | `PROPOSAL_CATEGORIES` | list | 4 | 1048-1053 |
| 13 | ↳ | `PROPOSAL_TECHNOLOGIES` | list | 10 | 1055-1066 |
| 13 | ↳ | `TEACHER_CONTENT_TYPES` | list | 6 | 1069-1106 |
| 13 | ↳ | `TEACHER_FORMS` | dict | 4 | 1110-1140 |
| 14 | Comentarios/reacciones | `SEED_COMMENTS` | list | 2 | 1147-1164 |
| 14 | ↳ | `SEED_REACTIONS` | dict | 4 | 1167-1172 |
| 14 | ↳ | `FILE_ICONS` | dict | 10 | 1175-1186 |

---

## 3. Modelo de datos deducido

Los comentarios del archivo indican a qué tabla del futuro esquema pertenece cada
constante. El grafo de entidades es:

```
                    ┌─────────────────────────────────────┐
                    │  USUARIO          (4 vistas distintas)│
                    │  ─ ROLE_DATA      3 sesiones demo     │
                    │  ─ TEACHERS       4 docentes          │
                    │  ─ SYSTEM_USERS   7 cuentas admin     │
                    │  ─ RANKING_DATA   9 (proyección)      │
                    └──────────────┬──────────────────────┘
                                   │ author / autor
                                   ▼
   ┌─────────────┐        ┌──────────────────────┐        ┌──────────────┐
   │ CATEGORIA   │◀──────▶│  CONTENIDO           │───────▶│  COMENTARIO  │
   │ EXPLORE_    │  slug  │  CONTENT_ITEMS (11)  │ 1   N  │ SEED_COMMENTS│
   │ CATEGORIES  │  map   │  id: "1".."11"       │        │ parentId → ↺ │
   └─────────────┘        │                      │        └──────────────┘
                          │  status: publicado / │
                          │          pendiente / │        ┌──────────────┐
                          │          rechazado   │───────▶│  REACCION    │
                          └──────────┬───────────┘ 1   1  │ SEED_    (4) │
                                     │                    │ REACTIONS    │
       ┌─────────────────────────────┼──────────────┐     └──────────────┘
       │                             │              │
       ▼                             ▼              ▼
  ┌──────────┐              ┌────────────┐   ┌────────────────┐
  │HALL_FAMA │              │MY_ITEMS(3) │   │VALIDATION_QUEUE│
  │HALL_OF_  │              │ id 7,8,old1│   │ id p1..p5      │
  │FAME (3)  │              └────────────┘   └────────────────┘
  └──────────┘           (proyecciones del mismo CONTENIDO con OTROS ids)

  ┌──────────────┐   ┌────────────────┐   ┌───────────────────┐
  │ NIVEL        │   │ INSIGNIA       │   │ HISTORIA          │
  │ LEVEL_NAMES  │   │ BADGES_CATALOG │   │ TIMELINE_EVENTS   │
  │ LEVEL_TABLE  │   │ (8)            │   │ (11)              │
  └──────────────┘   └────────────────┘   └───────────────────┘
```

**Observación estructural importante:** `CONTENT_ITEMS`, `MY_ITEMS`,
`VALIDATION_QUEUE` y `HALL_OF_FAME` **modelan lo mismo** (contenido del museo) pero
con **espacios de IDs diferentes** y esquemas distintos. `HALL_OF_FAME` es casi un
duplicado textual de los ítems 9-11 de `CONTENT_ITEMS`. Es el punto más débil del
modelo → ver §9.

---

## 4. Sección por sección

### §1 — Usuarios de demostración (`ROLE_DATA`, líneas 8-61)

Tres perfiles fijos, uno por rol. Se usan para el login simulado.

| Clave | Nombre | Correo | points | level | badges |
|---|---|---|---:|---:|---|
| `student` | Valentina Moreno | `v.moreno@unilibre.edu.co` | 1240 | 4 | Explorador, Primer Aporte, Top 10 |
| `teacher` | Dr. Carlos Patiño | `c.patino@unilibre.edu.co` | 3800 | 8 | Docente Activo, Investigador, Mentor |
| `admin` | Ing. Laura Jiménez | `l.jimenez@unilibre.edu.co` | 9999 | 10 | Administrador, Fundador, Leyenda |

Campos por perfil: `name`, `email`, `role`, `avatar` (URL de Unsplash), `points`,
`level`, `badges[]`, `description`.

```python
61  DEMO_PASSWORD = "1234"   # ← misma para los 3 roles (coincide con el prototipo)
```

> ⚠ El comentario de las líneas 5-7 advierte: *"en producción NUNCA se manda una
> contraseña al navegador"*. La contraseña viaja al cliente porque `web_routes.py:170`
> la inyecta como `demo_password`.

**Precisión:** los valores de `points`/`level` son **coherentes con** `LEVEL_TABLE`
(1240 ∈ [900,1500] → nivel 4 ✓; 3800 ∈ [3600,4400] → nivel 8 ✓; 9999 → nivel 10 ✓).

---

### §2 — Docentes asesores (`TEACHERS`, líneas 68-109)

4 docentes disponibles para el formulario de propuesta (`/proponer-contenido`).

| id | Nombre | Correo | department |
|---|---|---|---|
| `t1` | Dr. Carlos Patiño | c.patino@unilibre.edu.co | Ingeniería de Sistemas |
| `t2` | Mg. Sandra Ruiz | s.ruiz@unilibre.edu.co | Ingeniería de Sistemas |
| `t3` | Ing. Mariana Torres | m.torres@unilibre.edu.co | Ingeniería de Sistemas |
| `t4` | Dr. Ricardo Montoya | r.montoya@unilibre.edu.co | Ingeniería de Sistemas |

Campos: `id`, `name`, `email`, `department`, `avatar`.

> **Solapamiento:** `t1` (Carlos Patiño) es **el mismo** que `ROLE_DATA["teacher"]` y
> que `SYSTEM_USERS[2]`. Son tres representaciones del mismo usuario con ids
> `"t1"` (aquí), sin id (en `ROLE_DATA`) y `"3"` (en `SYSTEM_USERS`).

---

### §3 — Gamificación (RF-GAM-01 / RF-GAM-03)

#### `LEVEL_NAMES` (dict nivel→nombre, líneas 118-130)
```python
118  LEVEL_NAMES = {0:"", 1:"Curioso", 2:"Explorador", ..., 10:"Leyenda"}
```
Índice 0 vacío a propósito (no existe nivel 0). Se usa para pintar "Nivel 4 — Contribuidor".

#### `LEVEL_TABLE` (líneas 133-144) — la tabla `NIVEL` de la BD
| Nº | Nombre | puntos_min | puntos_max |
|---:|---|---:|---:|
| 1 | Curioso | 0 | 200 |
| 2 | Explorador | 200 | 500 |
| 3 | Colaborador | 500 | 900 |
| 4 | Contribuidor | 900 | 1500 |
| 5 | Innovador | 1500 | 2200 |
| 6 | Investigador | 2200 | 3000 |
| 7 | Referente | 3000 | 3600 |
| 8 | Experto | 3600 | 4400 |
| 9 | Maestro | 4400 | 6000 |
| 10 | Leyenda | 6000 | 9999 |

Campos: `numero`, `nombre`, `puntos_min`, `puntos_max`. Los rangos son **contiguos**
(`max` de uno = `min` del siguiente) → en el límite exacto enviaría ambigüedad si se
implementara con `>=min and <=max`; debería usarse `>= min and < max`.

#### `RANKING_DATA` (líneas 146-219)
9 usuarios con `rank`, `name`, `avatar`, `points`, `level`, `badges[]` (emojis).
Campos `rank` y `level` **se ignoran**: `web_routes.py:289` reordena por `points`
y recalcula el `rank`. Solo Valentina (1240) coincide con un perfil demo.

#### `BADGES_CATALOG` (líneas 222-231) — tabla `INSIGNIA`
8 insignias con `icon`, `name`, `puntos_requeridos`.
Nótese el idioma mezclado en los nombres: `"First Aporte"` (inglés), `"Top 10"`,
`"En racha"`. Se muestran tal cual al usuario → deuda de traducción.

---

### §4 — Línea del tiempo (`TIMELINE_EVENTS`, líneas 238-339) — tabla `HISTORIA`

11 hitos del programa, campos `year`, `title`, `description`, `icon`:

| Año | Hito | Año | Hito |
|---:|---|---:|---|
| 1989 | Fundación del Programa | 2015 | Laboratorio de Ciberseguridad |
| 1993 | Primera Promoción | 2018 | Acreditación de Alta Calidad |
| 1998 | Primera Acreditación | 2020 | Virtualización Urgente |
| 2004 | Semillero SISTEC | 2022 | Hackathon Unilibre |
| 2008 | Expansión Curricular | 2024 | 35 Años de Historia |
| 2012 | Primer Programa de Maestría | | |

Se consume en `/contenido/3` (el ítem "Linea del Tiempo"), como marca
`web_routes.py:145`: `es_linea_tiempo=(contenido_id == "3")`.

> El año **2008** menciona IA y Seguridad Informática; el **2024** dice "más de 2000
> egresados", mientras `HOME_STATS` dice "4.800+ Egresados" (§9).

---

### §5 — Contenido del museo (`CONTENT_ITEMS`, líneas 346-594) — tabla `CONTENIDO`

**La entidad central del sistema.** 11 ítems. Ver el diccionario completo en §5.

Resumen:

| id | Título (abreviado) | Año | Categoría | Status | Autor |
|---|---|---|---:|---|---|
| 1 | Monitoreo Ambiental IoT | 2023 | Proyecto | ✅ publicado | Valentina Moreno +2 |
| 2 | Premio Nacional Innovación | 2022 | Premio | ✅ publicado | Semillero SISTEC |
| 3 | Línea del Tiempo 35 años | 2024 | Historia | ✅ publicado | Coordinación Académica |
| 4 | Hackathon Unilibre 2024 | 2024 | Evento | ✅ publicado | Centro de Innovación |
| 5 | Gestión Académica con IA | 2023 | Investigacion | ✅ publicado | Dr. Patiño, Mg. Ruiz |
| 6 | App Residuos — Premio Verde | 2021 | Premio | ✅ publicado | Grupo EcoSistemas |
| 7 | Blockchain para Títulos | 2024 | Proyecto | ⏳ pendiente | Juan Perez |
| 8 | Chatbot de Orientación | 2024 | Proyecto | ❌ rechazado | Andrea Lopez |
| 9 | Mg. Patricia Salcedo | 1989 | Hall de la Fama | ✅ publicado | Mg. Patricia Salcedo |
| 10 | Dr. Ricardo Montoya | 2015 | Hall de la Fama | ✅ publicado | Dr. Ricardo Montoya |
| 11 | Ing. Camila Vargas | 2020 | Hall de la Fama | ✅ publicado | Ing. Camila Vargas |

**Composición de estados:** 9 publicados · 1 pendiente (`7`) · 1 rechazado (`8`).
Esto es intencional: da contenido para *todas* las pantallas sin tener que crear nada.

El ítem `8` es el único con `observations` no vacío (líneas 526-530) — el motivo de
rechazo que alimenta "Mis aportes" (RNF-SEG-04).

---

### §6 — Hall de la Fama (`HALL_OF_FAME`, líneas 601-656) — subtipo `HALL_FAMA`

3 personas con `id` (`h1`-`h3`), `name`, `role`, `year`, `category`, `description`,
`image`, `achievements[]`.

| id | Nombre | role | Categoría | achievements |
|---|---|---|---|---|
| h1 | Mg. Patricia Salcedo | Fundadora del Programa | Docente | 3 logros |
| h2 | Dr. Ricardo Montoya | Investigador Distinguido | Investigador | 3 logros |
| h3 | Ing. Camila Vargas | Egresada Emprendedora | Egresado | 3 logros |

> ⚠ **Duplicación:** son las mismas 3 personas que los ítems 9-11 de `CONTENT_ITEMS`,
> con textos idénticos pero **esquema distinto** (aquí hay `achievements[]`, allí hay
> `tags`/`documents`/`participants`) y **otro espacio de ids** (`h1` vs `"9"`).

---

### §7 — Categorías de exploración (RF-EXP-01 / RF-EXP-02)

#### `EXPLORE_CATEGORIES` (líneas 663-720)
7 categorías con `id` (slug), `label`, `icon`, `desc`, `count`, `color`:

| id | label | count | color |
|---|---|---:|---|
| `historia` | Historia | 18 | #7C3AED |
| `premios` | Premios | 47 | #D97706 |
| `proyectos` | Proyectos | 134 | #2563EB |
| `investigacion` | Investigacion | 62 | #DC2626 |
| `eventos` | Eventos | 89 | #059669 |
| `hall` | Hall de la Fama | 24 | #C9A84C |
| `galeria` | Galeria Historica | 203 | #DB2777 |

Los `count` (suma = 577) **no** coinciden con los 11 ítems reales: son cifras
aspiracionales para la portada, y sí coinciden con `KPI_DATA` (§11).

#### `CATEGORY_SLUG_MAP` (líneas 724-731)
Traduce slug de URL → valor de `CONTENT_ITEMS.category` (singular, en español):
```python
"historia"→"Historia" · "premios"→"Premio" · "proyectos"→"Proyecto"
"investigacion"→"Investigacion" · "eventos"→"Evento" · "hall"→"Hall de la Fama"
```
> ⚠ **Falta `galeria`** → la categoría "Galería Histórica" no filtra nada (§9).

#### `SEARCH_CATEGORIES` / `SEARCH_YEARS` (líneas 734-753)
Opciones del filtro lateral. Categorías en singular + "Todos". Años: `Todos, 2024,
2023, 2022, 2021, 2020, 2019, "Antes de 2019"`.
> El filtro de años es un **desplegable de textos**, no un rango: "Antes de 2019"
> requiere lógica especial en `buscar.js`.

---

### §8 — Portada (líneas 760-816)

| Constante | Contenido |
|---|---|
| `HOME_STATS` | 4 tarjetas: `35+` años, `4.800+` egresados, `120+` premios, `340+` proyectos |
| `HOME_QUICK_ACCESS` | 6 accesos rápidos con `title`, `desc`, `icon`, `cat` (slug), `image` |
| `HOME_HERO_IMAGE` | URL del banner (1440×600) |

Los `cat` de `HOME_QUICK_ACCESS` son: `historia, premios, proyectos, investigacion,
eventos, hall` — **los 6 slugs del mapa** (de nuevo, sin `galeria`).

---

### §9 — Aportes del estudiante (RF-DSH-02 / RF-DSH-01)

#### `MY_ITEMS` (líneas 823-854) — 3 aportes
| id | Título | date | status | observations |
|---|---|---|---|---|
| `7` | Sistema Blockchain… | 2024-11-15 | pendiente | — |
| `8` | Chatbot de Orientación… | 2024-09-03 | rechazado | *(motivo largo)* |
| `old1` | App para gestión de notas | 2023-05-20 | publicado | — |

Los ids `7`/`8` **coinciden con `CONTENT_ITEMS`**, pero `old1` no existe allí
(id inventado). Campos: `id`, `title`, `type`, `date`, `status`, `observations`.

#### `STUDENT_ACTIVITY` (líneas 857-878)
4 notificaciones: `text`, `time`, `icon` (⏳ 🏅 💬 🎯).

#### `STUDENT_MAX_POINTS = 2000` (línea 881)
Máximo de la barra de progreso del nivel actual.
> ⚠ El estudiante está en **nivel 4** = [900, 1500]; `2000` es el techo del **nivel 5**.
> Semántica ambigua (§9).

---

### §10 — Bandeja de validación del admin (RF-VAL-01)

#### `VALIDATION_QUEUE` (líneas 888-971) — 5 items
| id | Título | type | author | date |
|---|---|---|---|---|
| `p1` | Blockchain para Verificación de Títulos | Proyecto | Juan Perez | 2024-11-15 |
| `p2` | Semillero NLP Lab | Investigacion | Dra. Ana Ramirez | 2024-11-12 |
| `p3` | Hackathon FinTech 2024 | Premio | Equipo CodeBankers | 2024-11-08 |
| `p4` | Congreso SISTEC 2024 | Evento | Comite SISTEC | 2024-11-05 |
| `p5` | Dr. Alejandro Ospina — Hall | Hall de la Fama | Coordinacion Academica | 2024-11-01 |

Campos: `id`, `title`, `type`, `author`, `date`, `image`, `description`, `tags[]`,
`documents[]`. Nota: **no** tiene `status` (toda la bandeja se asume pendiente).

> ⚠ **`p1` es el mismo contenido que `CONTENT_ITEMS[7]` y que `MY_ITEMS[7]`** (misma
> propuesta de blockchain de Juan Perez) pero con **id `p1`**. Tres ids para un solo
> hecho de negocio → §9.

#### `PUBLISH_CHECKLIST` (líneas 974-981)
6 acciones que se "ejecutan" al publicar (RF-VAL-04), todas con `done: True`.
Es una **simulación visual**: el código no ejecuta ninguna de ellas.

---

### §11 — Indicadores del dashboard admin (RF-DSH-03)

| Constante | Contenido |
|---|---|
| `KPI_DATA` | 6 KPIs: `label`, `value`, `icon`, `color`, `change` |
| `MONTHLY_CONTENT` | 12 enteros (Ene…Dic) para el gráfico |
| `MONTHS_LABELS` | 12 etiquetas de mes |
| `IMPACT_METRICS` | 4 métricas de impacto con `label`, `value`, `sub` |

`KPI_DATA` y `EXPLORE_CATEGORIES` comparten los mismos `count`/`value`
(47 premios, 134 proyectos, 89 eventos, 62 publicaciones, 24 en Hall) → **están
duplicados**, deben mantenerse en sincronía a mano.

---

### §12 — Gestión de usuarios (RF-USR-05)

#### `SYSTEM_USERS` (líneas 1018-1026) — 7 cuentas
Campos: `id`, `name`, `email`, `role`, `active`, `joined`, `avatar`.

| id | Nombre | Rol | active |
|---:|---|---|---|
| 1 | Valentina Moreno | Estudiante | ✅ |
| 2 | Juan Perez | Estudiante | ✅ |
| 3 | Dr. Carlos Patino | Docente | ✅ |
| 4 | Dra. Ana Ramirez | Docente | ✅ |
| 5 | Ing. Laura Jimenez | Administrador | ✅ |
| 6 | Andres Felipe Rios | Egresado | ✅ |
| 7 | Andrea Lopez | Estudiante | ❌ |

#### `USER_ROLES`, `ROLE_COLORS`, `ROLE_LABELS` (líneas 1028-1041)
```python
USER_ROLES  = ["Estudiante", "Egresado", "Docente", "Administrador"]   # 4 roles en español
ROLE_COLORS = {"Estudiante":"tag-blue", "Egresado":"tag-purple",
               "Docente":"tag-orange", "Administrador":"tag-red"}
ROLE_LABELS = {"student":"Estudiante", "teacher":"Docente", "admin":"Administrador"}
```
> ⚠ **Dos vocabularios de rol coexisten** (§9): `ROLE_LABELS` traduce de los 3 roles
> internos (`student/teacher/admin`) a etiquetas, pero `USER_ROLES`/`SYSTEM_USERS`
> usan **4** roles ya en español (incluye `Egresado`, que no tiene equivalente interno).

---

### §13 — Catálogos de formularios

| Constante | Contenido |
|---|---|
| `PROPOSAL_CATEGORIES` | 4 tipos: Proyecto de Grado, Semillero, Extracurricular, Tesis de Maestría |
| `PROPOSAL_TECHNOLOGIES` | 10 tecnologías: React, Node.js, Python, Flutter, Java, TensorFlow, Arduino, Firebase, PostgreSQL, MongoDB |
| `TEACHER_CONTENT_TYPES` | 6 tipos (`id`, `label`, `icon`, `desc`): historia, premio, proyecto, evento, investigacion, hall |
| `TEACHER_FORMS` | 4 formularios dinámicos |

#### `TEACHER_FORMS` (líneas 1110-1140)
Define los campos que el JS pinta según el tipo elegido. Claves: `premio`, `hall`,
`proyecto` y `default`. Cada campo es `{label, placeholder, type?}`.

```python
1111  "premio": [ {label:"Nombre del premio *", ...}, ... ]   # 6 campos
1119  "hall":   [ ... ]                                       # 6 campos
1127  "proyecto":[ ... ]                                      # 5 campos
1134  "default":[ ... ]                                       # 4 campos
```

> **Faltan** las claves `historia`, `evento` e `investigacion` aunque existen en
> `TEACHER_CONTENT_TYPES` → esos 3 tipos caen al formulario `default`.
> El `*` al final de la etiqueta marca los campos obligatorios (se parsea en el JS).

---

### §14 — Comentarios, reacciones e íconos

#### `SEED_COMMENTS` (líneas 1147-1164) — 2 comentarios
Campos: `id` (**int**, no string), `contentId`, `author`, `text`, `time`, `parentId`.
Ambos son sobre `contentId:"1"` y con `parentId: None`.
> `Store.addComment` soporta hilos (`parentId`), pero **la semilla no trae ninguno**.

#### `SEED_REACTIONS` (líneas 1167-1172)
Dict `contentId → {emoji, count, reacted}` para los ítems 1-4. `reacted: False`
siempre (es el estado "sin reaccionar" del visitante).

#### `FILE_ICONS` (líneas 1175-1186)
10 extensiones → emoji. Usado por el gestor de evidencias (`adjuntar_evidencias`).

---

## 5. Diccionario de datos de `CONTENT_ITEMS`

El esquema más importante del proyecto. **15 campos**, todos obligatorios en la
práctica (el mock siempre los trae):

| Campo | Tipo | Ejemplo | Descripción | Notas |
|---|---|---|---|---|
| `id` | str | `"1"` | Identificador | **String** aunque parezca número |
| `title` | str | "Sistema de Monitoreo…" | Título | |
| `year` | int | `2023` | Año | |
| `category` | str | `"Proyecto"` | Categoría (singular) | Valores de `CATEGORY_SLUG_MAP` |
| `categoryTag` | str | `"tag-blue"` | Clase CSS del badge | `tag-blue/orange/green/red/purple/gold` |
| `description` | str | "Plataforma integral…" | Resumen | 1-3 frases |
| `image` | str | URL Unsplash | Imagen de tarjeta | 800×500 |
| `author` | str | "Valentina Moreno, +2" | Autor(es) | **Texto libre, no FK** ⚠ |
| `tags` | list[str] | `["IoT","Node.js"]` | Etiquetas | 2-4 |
| `status` | str | `"publicado"` | Estado | `publicado`/`pendiente`/`rechazado` |
| `participants` | list[str] | `["Valentina Moreno", …]` | Integrantes | |
| `technologies` | list[str] | `["Arduino","LoRaWAN"]` | Stack | Puede ir vacío |
| `documents` | list[obj] | `[{name,size}]` | Evidencias | `size` es **texto** ("3.2 MB") |
| `observations` | str | `""` | Motivo de rechazo | Solo si `status=="rechazado"` |

**Convención mixta:** `categoryTag` está en camelCase (porque lo consume el JS)
mientras el resto de constantes como `puntos_requeridos` usan snake_case. Es una
inconsistencia del archivo, no un error → §9.

---

## 6. Convenciones y vocabularios

### Estados del contenido (ciclo de vida)
```
  [estudiante propone]
          │
          ▼
     ┌──────────┐   admin aprueba    ┌───────────┐
     │pendiente │ ─────────────────▶ │ publicado │
     └──────────┘                     └───────────┘
          │   admin rechaza (observations OBLIGATORIO)
          ▼
     ┌───────────┐   el autor corrige
     │ rechazado │ ─────────────────────▶ vuelve a "pendiente"
     └───────────┘
```
Valores exactos: `"publicado"`, `"pendiente"`, `"rechazado"` (minúsculas, sin tilde).

### Formatos de ID por colección
| Colección | Formato | Ejemplo |
|---|---|---|
| `CONTENT_ITEMS` | numérico-string | `"1"`, `"11"` |
| `MY_ITEMS` | mezcla | `"7"`, `"8"`, `"old1"` |
| `VALIDATION_QUEUE` | `p` + número | `"p1"`…`"p5"` |
| `HALL_OF_FAME` | `h` + número | `"h1"`…`"h3"` |
| `TEACHERS` | `t` + número | `"t1"`…`"t4"` |
| `SYSTEM_USERS` | numérico-string | `"1"`…`"7"` |
| `SEED_COMMENTS` | **int** | `1`, `2` |
| `Store` (runtime) | timestamp | `'c'+Date.now()` |

> Seis formatos distintos para "id". En MySQL todos serían `INT` o `VARCHAR` con
> estrategia única (o autoincremental, o prefijo por tipo).

### Clases CSS de categoría (`categoryTag`)
| Clase | Uso |
|---|---|
| `tag-blue` | Proyecto |
| `tag-orange` | Premio |
| `tag-green` | Evento |
| `tag-red` | Investigacion |
| `tag-purple` | Historia |
| `tag-gold` | Hall de la Fama |

### Slugs de categoría ↔ valores de `category`
| Slug (URL) | `CONTENT_ITEMS.category` | `EXPLORE_CATEGORIES.label` |
|---|---|---|
| `historia` | `Historia` | Historia |
| `premios` | `Premio` | Premios |
| `proyectos` | `Proyecto` | Proyectos |
| `investigacion` | `Investigacion` | Investigacion |
| `eventos` | `Evento` | Eventos |
| `hall` | `Hall de la Fama` | Hall de la Fama |
| `galeria` | ❌ **sin mapeo** | Galeria Historica |

> Singular vs plural: el filtro lateral usa **singular** (`Premio`), la portada
> **plural** (`Premios`). El mapa resuelve la diferencia… salvo `galeria`.

---

## 7. Reglas de negocio embebidas

Aunque no hay funciones, los datos **codifican** reglas:

| Regla | Dónde | Cómo |
|---|---|---|
| **Nivel por puntos** | `LEVEL_TABLE` | `nivel = f(points)` con rangos contiguos |
| **Insignia por puntos** | `BADGES_CATALOG` | `puntos_requeridos` por insignia |
| **Ciclo de contenido** | `CONTENT_ITEMS.status` | 3 estados + `observations` obligatorio al rechazar |
| **Navegación categoría→filtro** | `CATEGORY_SLUG_MAP` | slug → valor de `category` |
| **Formulario por tipo** | `TEACHER_FORMS[type]` | con fallback a `default` |
| **Campos obligatorios** | sufijo `*` en `label` | parseado por el JS |
| **Ícono por extensión** | `FILE_ICONS` | `ext → emoji` |
| **Checklist de publicación** | `PUBLISH_CHECKLIST` | 6 pasos, todos `done` |

**Ejemplo verificable — cálculo de nivel:**
```
points = 1240 → está en [900, 1500) → nivel 4 → LEVEL_NAMES[4] = "Contribuidor"
```
`ROLE_DATA["student"]` dice exactamente `level: 4` ✓.

---

## 8. Cómo se consume

```
simul_data.py  ──import──▶  web_routes.py  ──render_template──▶  page.html
   (Python)                  (30 variables)      (contexto Jinja)     │
                                                                       │ {{ var | tojson }}
                                                                       ▼
                                                            window.SIMUL_XXX = [...]
                                                                       │
                                                     app.js boot() ────┤ Store.initX()
                                                                       ▼
                                                                 localStorage
```

**Tabla de inyección** (qué constante llega a qué `window.*`):

| Constante Python | Variable `window` | Vistas que la reciben |
|---|---|---|
| `CONTENT_ITEMS` | `SIMUL_CONTENT` | buscar, contenido, favoritos, dashboards, admin |
| `SEED_REACTIONS` | `SIMUL_REACTIONS` | contenido, favoritos, dashboards, admin_contenido |
| `SEED_COMMENTS` | `SIMUL_COMMENTS` | contenido |
| `VALIDATION_QUEUE` | `SIMUL_QUEUE` | admin_validacion |
| `SYSTEM_USERS` | `SIMUL_USERS` | admin_usuarios |
| `ROLE_DATA` | `SIMUL_ROLE_EMAILS` / `SIMUL_ROLE_USERS` | login |
| `LEVEL_NAMES` | `SIMUL_LEVEL_NAMES` | dashboard_estudiante |
| `ROLE_LABELS` | `SIMUL_ROLE_LABELS` | varias (vía `_common_context`) |
| `EXPLORE_CATEGORIES` | `categories` (contexto Jinja) | explorar |
| `CATEGORY_SLUG_MAP` | `SIMUL_CATEGORY_SLUG` | buscar |
| `FILE_ICONS` | `SIMUL_FILE_ICONS` | adjuntar_evidencias |
| `TEACHER_FORMS` | contexto Jinja `forms` | registrar_contenido |

Todo el archivo se importa **una sola vez al arrancar** el proceso
(`web_routes.py:32`), así que es estático en memoria.

---

## 9. Inconsistencias detectadas

### 🔴 9.1 Tres IDs para el mismo contenido (blockchain)

| Representación | id | Archivo |
|---|---|---|
| `CONTENT_ITEMS[7]` | `"7"` | simul_data.py:491 |
| `MY_ITEMS[0]` | `"7"` | simul_data.py:825 |
| `VALIDATION_QUEUE[0]` | **`"p1"`** | simul_data.py:890 |

La propuesta de blockchain de Juan Perez aparece **3 veces con 2 ids distintos**.
Si el admin la aprueba desde `VALIDATION_QUEUE`, `Store.dropFromQueue("p1")` solo
borra de la bandeja — **no actualiza** `CONTENT_ITEMS["7"]` ni `MY_ITEMS["7"]`,
porque sus ids no coinciden. El estado queda inconsistente.

> **Arreglo:** usar **un** id canónico (el de `CONTENT_ITEMS`) en las tres.

### 🔴 9.2 Dos vocabularios de rol

* Interno: `student` / `teacher` / `admin` (3) — usado por `Store`, `ROLE_DATA`, `guardPage`.
* Admin: `Estudiante` / `Egresado` / `Docente` / `Administrador` (4) — usado por `SYSTEM_USERS`.

**`Egresado` no existe en el vocabulario interno** → un egresado que inicie sesión
no tendría dashboard (`dashboardPath()` devuelve `/`) y `guardPage` lo rechazaría.

### 🔴 9.3 Categoría "Galería Histórica" sin filtro

`EXPLORE_CATEGORIES` incluye `galeria` (línea 713) y `HOME_QUICK_ACCESS`… no.
`CATEGORY_SLUG_MAP` **no** tiene `galeria`, y `SEARCH_CATEGORIES` tampoco.
Si un usuario entra a `/explorar` y pulsa "Galería Histórica", el mapa devuelve
`None` → la búsqueda no filtra nada. **Falta** `"galeria": "Galeria"` (o similar) y
al menos un `CONTENT_ITEMS` con esa categoría.

### 🟠 9.4 Nivel equivocado en el ranking

`RANKING_DATA` dice que **Lorena Castro** (2870 pts) es **nivel 7**, pero según
`LEVEL_TABLE` 2870 ∈ [2200, 3000) → **nivel 6**. Los demás son correctos.

### 🟠 9.5 `STUDENT_MAX_POINTS = 2000` mal alineado

El estudiante está en nivel 4 = [900, 1500). `2000` es el techo del nivel 5.
La barra de progreso no puede calcular bien el % del nivel actual con ese valor.

### 🟠 9.6 Datos duplicados y desincronizados

| Duplicado | Riesgo |
|---|---|
| `KPI_DATA` vs `EXPLORE_CATEGORIES.count` | Mismos conteos en 2 sitios; se desincronizan a mano |
| `HALL_OF_FAME` vs `CONTENT_ITEMS[9-11]` | Mismas personas, 2 esquemas |
| `ROLE_DATA["teacher"]` = `TEACHERS["t1"]` = `SYSTEM_USERS["3"]` | 3 copias de Carlos Patiño |
| `MY_ITEMS["8"].observations` == `CONTENT_ITEMS["8"].observations` | Texto idéntico, 2 lugares |

### 🟠 9.7 Contradicción en número de egresados

* `HOME_STATS`: **"4.800+ Egresados"** (línea 762)
* `TIMELINE_EVENTS[2024]`: **"más de 2.000 egresados activos"** (línea 335)

No es necesariamente un error (total vs. activos) pero no está declarado.

### 🟡 9.8 Autor como texto libre

`CONTENT_ITEMS.author` (línea 362) es `"Valentina Moreno, Felipe Castro, Andrea
López"` — varios autores concatenados en un string. **No hay forma de consultar
"contenido de Felipe Castro"** salvo con `LIKE`. En MySQL debe ser una tabla
puente `contenido_autor` o, mínimo, un `author_id` + `participants`.

Esto ya causa bugs: `web_routes.py:198` filtra los aportes del estudiante con
`"Valentina" in c["author"]` — coincidencia de subcadena frágil.

### 🟡 9.9 `id: int` en comentarios

`SEED_COMMENTS[].id` es `int` (línea 1149) mientras todos los demás ids son `str`.
`Store.addComment` genera `'c'+Date.now()` (string) → **tipos mezclados** en la misma lista.

### 🟡 9.10 Rangos de nivel solapados en los bordes

`LEVEL_TABLE` usa `[min, max]` inclusivo, y `max` de un nivel == `min` del siguiente
(200, 500…). Un usuario con exactamente 200 puntos encajaría en dos niveles si el
cálculo no define la frontera (`>= min and < max`).

### 🟡 9.11 Nombres de insignia en inglés

`BADGES_CATALOG` mezcla `"First Aporte"` (spanglish), `"Top 10"`, `"En racha"`.
Se muestran literales al usuario.

---

## 10. Esquema MySQL definitivo

Refina el propuesto en `ARQUITECTURA.md §12` con los datos reales observados:

```sql
-- ============ USUARIO (unifica ROLE_DATA + TEACHERS + SYSTEM_USERS) ============
CREATE TABLE usuario (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(120)  NOT NULL,
  email         VARCHAR(180)  NOT NULL UNIQUE,
  password_hash VARCHAR(255)  NOT NULL,
  role          ENUM('student','teacher','admin','egresado') NOT NULL,
  active        BOOLEAN       NOT NULL DEFAULT TRUE,
  points        INT           NOT NULL DEFAULT 0,
  level         TINYINT       NOT NULL DEFAULT 1,
  description   TEXT          NULL,
  avatar        VARCHAR(255)  NULL,
  department    VARCHAR(120)  NULL,          -- solo docentes (TEACHERS.department)
  joined        DATE          NULL,
  created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============ NIVEL (LEVEL_TABLE) ============
CREATE TABLE nivel (
  numero     TINYINT     PRIMARY KEY,
  nombre     VARCHAR(40) NOT NULL,
  puntos_min INT         NOT NULL,
  puntos_max INT         NOT NULL
);

-- ============ INSIGNIA (BADGES_CATALOG) ============
CREATE TABLE insignia (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  icon              VARCHAR(8)   NOT NULL,
  name              VARCHAR(60)  NOT NULL,
  puntos_requeridos INT          NOT NULL
);

CREATE TABLE usuario_insignia (          -- N:M
  usuario_id INT NOT NULL,
  insignia_id INT NOT NULL,
  PRIMARY KEY (usuario_id, insignia_id),
  FOREIGN KEY (usuario_id)  REFERENCES usuario(id)  ON DELETE CASCADE,
  FOREIGN KEY (insignia_id) REFERENCES insignia(id) ON DELETE CASCADE
);

-- ============ CATEGORIA (EXPLORE_CATEGORIES + CATEGORY_SLUG_MAP) ============
CREATE TABLE categoria (
  id    VARCHAR(40)  PRIMARY KEY,          -- slug: 'proyectos', 'hall'...
  label VARCHAR(80)  NOT NULL,             -- 'Proyectos'
  value VARCHAR(40)  NOT NULL UNIQUE,      -- 'Proyecto' (lo que va en contenido)
  icon  VARCHAR(8)   NULL,
  descr VARCHAR(255) NULL,
  color CHAR(7)      NULL,                 -- '#2563EB'
  tag_class VARCHAR(20) NULL               -- 'tag-blue'
);

-- ============ CONTENIDO (CONTENT_ITEMS) ============
CREATE TABLE contenido (
  id               VARCHAR(32) PRIMARY KEY,   -- '1'..'11' (o INT si se unifica)
  title            VARCHAR(200) NOT NULL,
  year             SMALLINT     NOT NULL,
  category_id      VARCHAR(40)  NOT NULL,
  description      TEXT         NOT NULL,
  image            VARCHAR(500) NULL,
  status           ENUM('pendiente','publicado','rechazado') NOT NULL DEFAULT 'pendiente',
  observations     TEXT         NULL,          -- motivo de rechazo (RNF-SEG-04)
  alt_text         VARCHAR(255) NULL,          -- RNF-ACC-01
  created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categoria(id)
);

-- Autor(es): tabla puente (author/participants son listas de texto libre)
CREATE TABLE contenido_autor (
  contenido_id VARCHAR(32) NOT NULL,
  usuario_id   INT         NULL,               -- NULL si es externo (texto libre)
  nombre       VARCHAR(120) NOT NULL,          -- texto original siempre presente
  rol          ENUM('autor','participante') NOT NULL DEFAULT 'participante',
  PRIMARY KEY (contenido_id, nombre),
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id)   REFERENCES usuario(id)
);

CREATE TABLE contenido_tag (
  contenido_id VARCHAR(32) NOT NULL,
  tag          VARCHAR(60) NOT NULL,
  PRIMARY KEY (contenido_id, tag),
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

CREATE TABLE contenido_tecnologia (
  contenido_id VARCHAR(32) NOT NULL,
  tecnologia   VARCHAR(60) NOT NULL,
  PRIMARY KEY (contenido_id, tecnologia),
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

-- ============ DOCUMENTO / EVIDENCIA (CONTENT_ITEMS.documents) ============
CREATE TABLE documento (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  contenido_id VARCHAR(32)  NOT NULL,
  name         VARCHAR(200) NOT NULL,
  size         VARCHAR(20)  NOT NULL,        -- '3.2 MB' (texto, como en el mock)
  url          VARCHAR(500) NULL,
  alt_text     VARCHAR(255) NULL,            -- RNF-ACC-01 (obligatorio al adjuntar)
  extension    VARCHAR(10)  NULL,            -- para FILE_ICONS
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

-- ============ COMENTARIO (SEED_COMMENTS, árbol con parentId) ============
CREATE TABLE comentario (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  contenido_id VARCHAR(32)  NOT NULL,
  autor_id     INT          NOT NULL,
  parent_id    INT          NULL,
  text         TEXT         NOT NULL,
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contenido_id) REFERENCES contenido(id)  ON DELETE CASCADE,
  FOREIGN KEY (autor_id)     REFERENCES usuario(id),
  FOREIGN KEY (parent_id)    REFERENCES comentario(id) ON DELETE CASCADE
);

-- ============ REACCION (SEED_REACTIONS) ============
CREATE TABLE reaccion (
  contenido_id VARCHAR(32) PRIMARY KEY,
  emoji        VARCHAR(8)  NOT NULL DEFAULT '👏',
  count        INT         NOT NULL DEFAULT 0,
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

-- ============ FAVORITO (solo en store.js, no en simul_data) ============
CREATE TABLE favorito (
  usuario_id   INT NOT NULL,
  contenido_id VARCHAR(32) NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, contenido_id),
  FOREIGN KEY (usuario_id)   REFERENCES usuario(id)   ON DELETE CASCADE,
  FOREIGN KEY (contenido_id) REFERENCES contenido(id) ON DELETE CASCADE
);

-- ============ HISTORIA (TIMELINE_EVENTS) ============
CREATE TABLE historia (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  year        SMALLINT     NOT NULL,
  title       VARCHAR(150) NOT NULL,
  description TEXT         NOT NULL,
  icon        VARCHAR(8)   NULL
);

-- ============ BANDEJA / PROPUESTA ============
-- VALIDATION_QUEUE  → es una VISTA de contenido WHERE status='pendiente'
-- MY_ITEMS          → es una VISTA de contenido/autoria WHERE usuario = :yo
-- Por eso NO se crean tablas: se resuelven con consultas.
CREATE VIEW v_bandeja_validacion AS
  SELECT c.id, c.title, cat.value AS type, c.created_at AS date,
         c.description, c.image
  FROM contenido c JOIN categoria cat ON cat.id = c.category_id
  WHERE c.status = 'pendiente';

-- PROPUESTAS de estudiante (store.js: simul.proposals) — sí es entidad propia
CREATE TABLE propuesta (
  id         VARCHAR(40) PRIMARY KEY,
  autor_id   INT NOT NULL,
  teacher_id INT NOT NULL,
  category   VARCHAR(80),
  year       SMALLINT,
  status     ENUM('pendiente','aprobada','rechazada') NOT NULL DEFAULT 'pendiente',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (autor_id)   REFERENCES usuario(id),
  FOREIGN KEY (teacher_id) REFERENCES usuario(id)
);
```

### Migración de constantes → tablas

| Constante | Destino | Acción |
|---|---|---|
| `ROLE_DATA` | `usuario` | seed (3 filas) |
| `TEACHERS` | `usuario` (role='teacher') | seed (4 filas, deduplicar con ROLE_DATA) |
| `SYSTEM_USERS` | `usuario` | seed (7 filas, deduplicar) |
| `LEVEL_NAMES` + `LEVEL_TABLE` | `nivel` | seed (10 filas) |
| `BADGES_CATALOG` | `insignia` | seed (8 filas) |
| `RANKING_DATA` | **vista** sobre `usuario` | `ORDER BY points DESC` |
| `TIMELINE_EVENTS` | `historia` | seed (11 filas) |
| `CONTENT_ITEMS` | `contenido` + 5 tablas satélite | seed (11 filas) |
| `HALL_OF_FAME` | `contenido` (categoría 'hall') | **deduplicar** con ítems 9-11 |
| `EXPLORE_CATEGORIES` | `categoria` | seed (7 filas) |
| `CATEGORY_SLUG_MAP` | `categoria.value` | **columna**, no constante |
| `SEARCH_CATEGORIES` | `categoria` | derivado (`SELECT label`) |
| `SEARCH_YEARS` | `contenido` | derivado (`SELECT DISTINCT year`) |
| `MY_ITEMS` | **vista** sobre `contenido` | por autor |
| `VALIDATION_QUEUE` | **vista** | `WHERE status='pendiente'` |
| `STUDENT_ACTIVITY` | `notificacion` | seed |
| `KPI_DATA`, `MONTHLY_CONTENT`, `IMPACT_METRICS` | agregados | `SELECT COUNT(*)` / `GROUP BY` |
| `PUBLISH_CHECKLIST` | — | lógica de aplicación |
| `PROPOSAL_CATEGORIES` / `_TECHNOLOGIES` | catálogos | seed o constantes |
| `TEACHER_CONTENT_TYPES` | `categoria` | seed |
| `TEACHER_FORMS` | — | configuración del front (no BD) |
| `SEED_COMMENTS` / `SEED_REACTIONS` | `comentario` / `reaccion` | seed |
| `FILE_ICONS` | — | constante de presentación (no BD) |

> **Regla de oro de la migración:** lo que en el mock es una **vista** (ranking,
> bandeja, mis aportes, años, categorías) **no se guarda**: se calcula con SQL.
> Guardarlo crearía los mismos problemas de desincronización de §9.6.

---

*Documento generado a partir del análisis de `app/data/simul_data.py` (1.186 líneas).*
*Parte 2 de 5. Sigue: Parte 3 — Frontend núcleo (`app.js`, `store.js`, `api.js`, `_navbar.html`).*
