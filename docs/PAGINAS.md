# SIMUL — Documentación Técnica

> **Parte 4: Las páginas** (21 HTML + 15 JS)
> Continúa a [`ARQUITECTURA.md`](./ARQUITECTURA.md) (1), [`DATOS.md`](./DATOS.md) (2) y [`FRONTEND.md`](./FRONTEND.md) (3).

---

## Índice

1. [Qué cubre esta parte](#1-qué-cubre-esta-parte)
2. [El patrón de página canónico](#2-el-patrón-de-página-canónico)
3. [Ejemplo comentado: `favoritos`](#3-ejemplo-comentado-favoritos)
4. [Mapa de las 21 páginas](#4-mapa-de-las-21-páginas)
5. [Recorrido por rol](#5-recorrido-por-rol)
6. [Los scripts inline (páginas sin JS)](#6-los-scripts-inline-páginas-sin-js)
7. [El bus de eventos](#7-el-bus-de-eventos)
8. [Auditoría de `innerHTML` / escaping](#8-auditoría-de-innerhtml--escaping)
9. [Hallazgos](#9-hallazgos)
10. [Deuda y repetición de código](#10-deuda-y-repetición-de-código)

---

## 1. Qué cubre esta parte

Las **21 plantillas HTML** (`app/templates/pages/`) y los **15 scripts de página**
(`app/static/js/pages/`). Todas siguen **el mismo patrón**; por eso no se documentan
una por una, sino:

* el **patrón canónico** (§2) destilado de las 15,
* un **ejemplo completo comentado** (§3),
* la **tabla** de las 21 (§4) y su **agrupación por rol** (§5),
* los **casos especiales** sin JS (§6).

| Métrica | Valor |
|---|---|
| Plantillas HTML | 21 (20 con ruta + `contenido_no_encontrado` de 404) |
| Scripts JS | 15 (6 páginas no tienen JS) |
| Líneas HTML | 5.227 |
| Líneas JS de página | 3.353 |
| Páginas totalmente estáticas | 2 (`index`, `explorar`) |
| Páginas con guarda de rol | 11 |
| ⚠ Páginas privadas **sin** guarda | 2 (`dashboard_admin`, `admin_publicacion`) |

---

## 2. El patrón de página canónico

Los 15 scripts comparten **exactamente** esta estructura. Es un patrón tan
consistente que se puede escribir como plantilla:

```javascript
/* ==========================================================
   <NOMBRE DE LA PÁGINA>  (RF-XXX-0N)

   <una o dos frases explicando qué hace y de dónde saca los datos>
   ========================================================== */

(function () {                                  // ① IIFE: ámbito privado
  'use strict';                                 // ② errores estrictos

  const $  = SIMUL.$;                           // ③ helpers del núcleo
  const $$ = SIMUL.$$;

  const DATOS = window.SIMUL_XXX || [];         // ④ datos que inyectó Jinja

  const EL = $('#algún-id');                    // ⑤ caché de nodos del DOM

  function pintar() {                           // ⑥ lógica de render
    if (!EL) return;                            //    guarda si no existe el nodo
    EL.innerHTML = DATOS.map(/* … */).join(''); //    (siempre escapando)
  }

  document.addEventListener('simul:ready', function () {   // ⑦ punto de entrada
    const user = SIMUL.guardPage('rol');        // ⑧ guarda de sesión/rol
    if (!user) return;                          //    (redirige si no corresponde)

    pintar();                                   // ⑨ primer render

    document.addEventListener('simul:favorites-changed', pintar);  // ⑩ reacción a eventos

    EL.addEventListener('click', function (event) { /* … */ });    // ⑪ handlers
  });

})();
```

### Piezas clave y por qué existen

| # | Pieza | Por qué |
|---|---|---|
| ① | **IIFE** | Evita variables globales. Cada página es un módulo aislado. |
| ④ | `window.SIMUL_XXX` | El **puente** con Python: `web_routes` inyecta JSON con `| tojson` (Parte 2 §8). |
| ⑤ | Caché de nodos al inicio | Buscar en el DOM es caro; se hace una vez. |
| ⑦ | `'simul:ready'` | **Todos** los scripts esperan este evento (emitido por `boot()` en `app.js`). Garantiza que el `Store` ya está sembrado. |
| ⑧ | `guardPage(rol)` | Si no corresponde, ya redirigió; `if (!user) return` **corta** la ejecución. |
| ⑩ | Eventos `simul:*` | Desacople entre `app.js` y las páginas (ver §7). |

> ⚠ **El patrón depende del orden de carga** (Parte 3 §2): los scripts de página se
> ejecutan en el parseo (registran el listener de `simul:ready`) y `boot()` corre
> después, en `DOMContentLoaded`. Si `app.js` se cargara con `defer` o `async`,
> `boot()` podría disparar `simul:ready` **antes** de que las páginas escuchen y
> **ninguna** correría. Es un acoplamiento frágil por orden (§9.8).

### Las 3 variantes del patrón

**A. Pública sin guarda** (buscar, contenido): sin `guardPage`, render directo.
**B. Privada con rol** (dashboards): `guardPage('student'|'teacher'|'admin')`.
**C. Privada sin rol** (perfil, favoritos, mis_aportes): `guardPage()` → basta con
estar logueado.

---

## 3. Ejemplo comentado: `favoritos`

Es la página más corta (73 líneas) y muestra **todas** las piezas del patrón. La
documentamos línea por línea como referencia:

```javascript
 1  /* ==========================================================
 2     FAVORITOS  (RF-EXP-04)
 3
 4     Lista el contenido guardado por el usuario. Los ids viven en
 5     localStorage; el texto sale del catálogo que entrega la ruta.
 6     ========================================================== */
```

**Líneas 4-5 resumen el modelo de datos del frontend:** los **ids** (qué guardaste)
viven en `localStorage`; el **texto** (título, imagen…) se busca en el catálogo
`simul.content`. Es una "relación" manual entre dos claves.

```javascript
 8  (function () {
 9    'use strict';
11    const $ = SIMUL.$;                                // del núcleo
13    const GRID  = $('#favorites-grid');               // contenedor de tarjetas
14    const VACIO = $('#favorites-empty');              // estado vacío
```

```javascript
20    function pintar() {
21      if (!GRID) return;                              // nodo inexistente → salir
23      /* La primera vez se siembra la lista con cuatro piezas… */
25      Store.initFavorites(window.SIMUL_SEED_FAVORITES || []);
```

> ⚠ **Línea 25 es la única siembra de favoritos de todo el proyecto** (Parte 3 §9.4).
> Si el usuario nunca visitó `/favoritos`, la lista semilla no existe.

```javascript
27      const catalogo = Store.getContent();           // el catálogo (texto)
28      const ids = Store.getFavorites() || [];        // la selección (ids)
30      /* Se conserva el orden en que el usuario guardó. */
31      const items = ids
32        .map(function (id) {
33          return catalogo.find(function (c) {
34            return String(c.id) === String(id);      // comparación por string
35          });
36        })
37        .filter(Boolean);                            // ← quita los ids huérfanos
```

**Líneas 31-37** son el "JOIN" manual: por cada id guardado, busca su objeto. El
`.filter(Boolean)` (37) es la defensa clave: si un favorito apunta a un contenido que
ya no existe (o que el usuario no visita por primera vez), el `find` devuelve
`undefined` y se descarta. **Sin eso, `contentCardHtml(undefined)` reventaría.**

```javascript
39      GRID.classList.toggle('hidden', items.length === 0);     // si vacío → oculto
40      GRID.classList.toggle('grid', items.length > 0);         // si hay → rejilla
42      VACIO.classList.toggle('hidden', items.length !== 0);    // estado vacío
43      VACIO.classList.toggle('flex', items.length === 0);
45      GRID.innerHTML = items.map(SIMUL.contentCardHtml).join('');
```

**Línea 45:** el render delega en `SIMUL.contentCardHtml` (Parte 3 §3.10), que **ya
escapa todos los campos**. Por eso aquí **no** se llama a `escapeHtml` directamente
(ver §8).

```javascript
48      ids.forEach(function (id) {
49        SIMUL.$$('[data-favorite="' + id + '"]').forEach(function (btn) {
50          btn.textContent = '★';                     // rellena la estrella
51          btn.style.color = '#C9A84C';
52        });
53      });
54    }
```

```javascript
60    document.addEventListener('simul:ready', function () {
61      const user = SIMUL.guardPage();                // variante C: cualquier sesión
62      if (!user) return;                             // ya redirigió
64      pintar();
68      document.addEventListener('simul:favorites-changed', function (event) {
69        if (!event.detail.active) pintar();          // se quitó uno → repintar
70      });
71    });
73  })();
```

**Líneas 68-70:** al quitar un favorito desde esta pantalla, `app.js` emite
`simul:favorites-changed`; aquí se repinta **solo cuando se quitó** (`!active`),
porque añadir no cambia esta vista.

---

## 4. Mapa de las 21 páginas

| # | Ruta | Plantilla | JS | Guarda | Datos inyectados |
|---|---|---|---|---|---|
| 1 | `GET /` | `index.html` | — | público | `HOME_STATS`, `HOME_QUICK_ACCESS`, `HALL_OF_FAME`, `HOME_HERO_IMAGE` |
| 2 | `GET /explorar` | `explorar.html` | — | público | `EXPLORE_CATEGORIES` |
| 3 | `GET /buscar` | `buscar.html` | `buscar.js` | público | `SIMUL_CONTENT`, `SIMUL_CATEGORY_SLUG`, `SIMUL_CATEGORIES`, `SIMUL_YEARS`, `SIMUL_INITIAL_QUERY`, `SIMUL_INITIAL_CAT` |
| 4 | `GET /contenido/<id>` | `contenido.html` | `contenido.js` | público | `SIMUL_CONTENT`, `SIMUL_COMMENTS`, `SIMUL_REACTIONS`, `SIMUL_ROLE_LABELS`, `SIMUL_ITEM_ID`, `SIMUL_HAS_TIMELINE`, `SIMUL_TIMELINE` |
| 5 | `GET /login` | `login.html` | `login.js` | público | `SIMUL_ROLE_USERS`, `SIMUL_ROLE_EMAILS`, `SIMUL_DEMO_PASSWORD` |
| 6 | `GET /registro` | `registro.html` | `registro.js` | público | `SIMUL_ROLE_EMAILS` |
| 7 | `GET /dashboard/estudiante` | `dashboard_estudiante.html` | `dashboard_estudiante.js` | `student` | `SIMUL_CONTENT`, `SIMUL_REACTIONS`, `SIMUL_ROLE_LABELS`, `SIMUL_LEVEL_NAMES` |
| 8 | `GET /proponer-contenido` | `proponer_contenido.html` | `proponer_contenido.js` | `student` | (docentes, categorías, tecnologías, años) |
| 9 | `GET /mis-aportes` | `mis_aportes.html` | `mis_aportes.js` | cualquiera | `MY_ITEMS` (render servidor) |
| 10 | `GET /favoritos` | `favoritos.html` | `favoritos.js` | cualquiera | `SIMUL_CONTENT`, `SIMUL_REACTIONS`, `SIMUL_SEED_FAVORITES` |
| 11 | `GET /ranking` | `ranking.html` | — (inline) | público | ranking recalculado, `SIMUL_ROLE_LABELS` |
| 12 | `GET /mi-perfil` | `perfil.html` | `perfil.js` | cualquiera | `SIMUL_ROLE_LABELS`, `SIMUL_BADGES_CATALOG` |
| 13 | `GET /dashboard/docente` | `dashboard_docente.html` | `dashboard_docente.js` | `teacher` | `SIMUL_CONTENT`, `SIMUL_REACTIONS`, `SIMUL_ROLE_LABELS` |
| 14 | `GET /registrar-contenido` | `registrar_contenido.html` | `registrar_contenido.js` | `teacher` | `SIMUL_TEACHER_FORMS` |
| 15 | `GET /adjuntar-evidencias` | `adjuntar_evidencias.html` | `adjuntar_evidencias.js` | `teacher` | `SIMUL_FILE_ICONS` |
| 16 | `GET /dashboard/admin` | `dashboard_admin.html` | — (inline) | ⚠ **ninguna** | `SIMUL_ROLE_LABELS` |
| 17 | `GET /admin/contenido` | `admin_contenido.html` | `admin_contenido.js` | `admin` | `SIMUL_CONTENT`, `SIMUL_REACTIONS` |
| 18 | `GET /admin/validacion` | `admin_validacion.html` | `admin_validacion.js` | `admin` | `SIMUL_QUEUE` |
| 19 | `GET /admin/publicacion` | `admin_publicacion.html` | — | ⚠ **ninguna** | `PUBLISH_CHECKLIST` (render servidor) |
| 20 | `GET /admin/usuarios` | `admin_usuarios.html` | `admin_usuarios.js` | `admin` | `SIMUL_USERS`, `SIMUL_USER_ROLES`, `SIMUL_ROLE_COLORS` |
| 21 | (404) | `contenido_no_encontrado.html` | — | público | — |

### Métodos de `Store` que usa cada página

| Página | Lee | Escribe |
|---|---|---|
| `buscar` | `getContent` | — |
| `contenido` | `getReactions`, `isFavorite`, `getComments`, `getUser` | `addComment`, `toggleReaction`, `toggleFavorite` |
| `favoritos` | `getContent`, `getFavorites` | `initFavorites` |
| `dashboard_estudiante` | `getContent`, `getFavorites` | — |
| `dashboard_docente` | `getUser`, `getProposals` | — |
| `mis_aportes` | `getProposals` | — |
| `perfil` | `getUser` | `updateUser` |
| `proponer_contenido` | `getUser` | `addProposal` |
| `registrar_contenido` | `getUser` | `upsertContent` |
| `admin_contenido` | `getContent`, `findContent` | `setContentStatus`, `deleteContent` |
| `admin_validacion` | `getQueue` | `upsertContent`, `dropFromQueue`, `initQueue` |
| `admin_usuarios` | `getUsers`, `getUser` | `setUserRole`, `updateUser`, `toggleUserActive`, `initUsers` |
| `login` | `getUser` | `login` |
| `registro` | — | `register` |
| `adjuntar_evidencias` | — | — (solo UI) |

---

## 5. Recorrido por rol

### 🟢 Visitante (sin sesión)

| Página | Qué muestra |
|---|---|
| `index` | Portada: hero, estadísticas (`HOME_STATS`), accesos rápidos, Hall de la Fama. **100% estática** (Jinja). |
| `explorar` | Rejilla de 7 categorías con enlaces a `/buscar?cat=<slug>`. **Estática.** |
| `buscar` | Buscador con filtros de texto/categoría/año. **Filtrado en el navegador** sobre `Store.getContent()`, mostrando **solo `status==='publicado'`** (`buscar.js:43-47`). Enlace profundo `?cat=` vía `CATEGORY_SLUG_MAP`. |
| `contenido/<id>` | Detalle: cuerpo, relacionados, comentarios (leer), reacciones. Comentar exige sesión (el formulario tiene `data-requires-auth`). El 404 usa `contenido_no_encontrado.html`. |
| `ranking` | Tabla de la comunidad (RF-GAM-04). **Público por diseño.** Render 100% Jinja. |
| `login` / `registro` | Formularios simbióticos (ver abajo). |

**Login/registro (RF-USR-01/02)** son especiales: `hide_nav` oculta la navbar
(`base.html:106`). El login valida contra correos demo y `DEMO_PASSWORD` en
`login.js`; al elegir rol, `Store.login(role)` copia el perfil y
`dashboardPath(role)` redirige (Parte 3 §4.2). El registro solo **guarda** en
`simul.pendingUsers` (no inicia sesión).

### 🔵 Estudiante

| Página | Rol funcional |
|---|---|
| `dashboard_estudiante` | Aportes del usuario + barra de progreso de nivel + contador de favoritos (RF-DSH-01). |
| `proponer_contenido` | Formulario de propuesta con docente asesor, categoría, tecnología y adjuntos (RF-PRY-01) → `Store.addProposal()`. |
| `mis_aportes` | Historial con estados; modal de **observaciones de rechazo** (RF-DSH-02 + RNF-SEG-04). |
| `favoritos` | Rejilla de lo guardado (RF-EXP-04). |
| `perfil` | Edición de nombre/descripción → `Store.updateUser()` (RF-USR-03). |

### 🟠 Docente

| Página | Rol funcional |
|---|---|
| `dashboard_docente` | Contenido propio agrupado por estado + propuestas que asesora (RF-COM-01, RF-PRY-02). |
| `registrar_contenido` | Formulario **dinámico**: los campos cambian según el tipo (`TEACHER_FORMS`); publica con `Store.upsertContent()` (RF-COM-02). |
| `adjuntar_evidencias` | Gestor de archivos con barra de progreso simulada e íconos por extensión (`FILE_ICONS`); exige `alt_text` (RNF-ACC-01). |

### 🔴 Administrador

| Página | Rol funcional |
|---|---|
| `dashboard_admin` | KPIs, gráfico mensual, métricas de impacto (RF-DSH-03). ⚠ **Sin guarda.** |
| `admin_contenido` | Tabla de todo el contenido con cambio de estado y borrado (RF-ADM). |
| `admin_validacion` | Bandeja de pendientes: aprobar/rechazar con **observación obligatoria** (RF-VAL-01/03/04). |
| `admin_publicacion` | Checklist de publicación (RF-VAL-04). ⚠ **Sin guarda ni JS.** |
| `admin_usuarios` | Gestión de roles y activación (RF-USR-05). |

---

## 6. Los scripts inline (páginas sin JS)

Seis plantillas **no** tienen archivo JS. Dos de ellas sí tienen un `<script>`
inline mínimo:

### `dashboard_admin.html` y `ranking.html`

```django
{# las dos, líneas 7-9 idénticas #}
<script>
    window.SIMUL_ROLE_LABELS = {{ role_labels | tojson }};
</script>
```

Solo inyectan `SIMUL_ROLE_LABELS` (para que `paintUser` traduzca el rol). El resto
del HTML lo renderiza Jinja por completo.

### Las otras cuatro

| Página | Motivo |
|---|---|
| `index.html` | Todo es estático (Jinja). |
| `explorar.html` | Rejilla de enlaces estática. |
| `admin_publicacion.html` | Checklist estático (`PUBLISH_CHECKLIST`). |
| `contenido_no_encontrado.html` | Plantilla de error 404. |

> ⚠ **`dashboard_admin.html` y `admin_publicacion.html` son privadas pero no
> tienen guarda**: no hay JS que llame a `guardPage('admin')` (§9.1, §9.2).

---

## 7. El bus de eventos

`app.js` y las páginas se comunican con **eventos de `document`**. Es el mecanismo
de desacople del proyecto:

| Evento | Emite | Escuchan | Payload |
|---|---|---|---|
| `simul:ready` | `app.js` `boot()` (línea 342) | **Los 15** scripts de página | `{ user }` |
| `simul:favorites-changed` | `app.js` `initFavorites` (313) | `contenido.js`, `dashboard_estudiante.js`, `favoritos.js` | `{ id, active }` |
| `storage` | (navegador) | `dashboard_docente.js` | evento nativo |

```
         app.js boot()
              │
              ├── dispatch 'simul:ready' ────────┐
              │                                  ▼
              │            ┌───────────────────────────────────┐
              │            │ buscar.js    → leerParametros()    │
              │            │ favoritos.js → guardPage + pintar  │
              │            │ perfil.js    → guardPage + render  │
              │            │ … (los 15)                         │
              │            └───────────────────────────────────┘
              │
   clic en ★ ─┤── dispatch 'simul:favorites-changed'
              │            └──▶ las páginas repintan lo suyo
```

**El evento `storage` (nativo del navegador)** lo usa `dashboard_docente.js`: se
dispara cuando **otra pestaña** cambia `localStorage`. Es la única concesión a
"multipestaña" del proyecto.

---

## 8. Auditoría de `innerHTML` / escaping

14 usos de `innerHTML` en los scripts de página. Se auditaron todos:

| Página | ¿Escapa? | Cómo |
|---|---|---|
| `favoritos.js:45` | ✅ | Delega en `SIMUL.contentCardHtml` (que escapa) |
| `buscar.js:82` | ✅ | Delega en `SIMUL.contentCardHtml` |
| `contenido.js:149,156` | ✅ | `escapeHtml` explícito (6 usos) |
| `adjuntar_evidencias.js:43` | ✅ | `escapeHtml(archivo.nombre)` |
| `admin_contenido.js:117` | ✅ | 12 usos de `escapeHtml` |
| `admin_usuarios.js:111` | ✅ | 9 usos |
| `admin_validacion.js:148` | ✅ | 14 usos |
| `proponer_contenido.js:118` | ✅ | `escapeHtml` |
| `registrar_contenido.js:105` | ✅ | `escapeHtml` en labels/placeholders |
| `dashboard_docente.js:79,90` | ✅ | 3 usos |
| `dashboard_estudiante.js:47,61` | ⚠️ **1 hueco** | Ver §9.4 |

**Conclusión:** la disciplina de escapado es **sólida y consistente**. El proyecto
construye HTML por concatenación (riesgo alto de XSS), pero aplica `escapeHtml` en
casi todos los puntos. Es el aspecto mejor cuidado del frontend.

---

## 9. Hallazgos

### 🔴 9.1 `/dashboard/admin` no tiene guarda

`dashboard_admin.html` **no tiene archivo JS** y su único `<script>` inline solo
inyecta `SIMUL_ROLE_LABELS`. **Nadie llama a `guardPage('admin')`.**
Consecuencia: cualquier visitante que escriba `localhost:5000/dashboard/admin`
recibe la pantalla completa de administración (datos mock, pero es una
incoherencia con el RBAC del resto de `/admin/*`).

> Los KPIs son datos de demostración, así que no hay fuga real **hoy** — pero al
> conectar MySQL **sí** lo sería.

### 🟠 9.2 `/admin/publicacion` tampoco tiene guarda

Igual que la anterior: sin JS → sin `guardPage`. Es la pantalla menos sensible
(solo un checklist), pero rompe el patrón "todo `/admin/*` exige admin".

### 🟠 9.3 Las observaciones de rechazo viajan en el HTML

`mis_aportes.html` renderiza los motivos de rechazo **en el servidor** y los pone en
un atributo `data-observations` de cada botón; `mis_aportes.js:58` los lee del DOM.
La única protección (RNF-SEG-04: "la sesión es necesaria para ver los motivos") es el
`SIMUL.guardPage()` de la línea 54. **El texto está en la página aunque no haya
sesión** — basta con ver el código fuente o deshabilitar JS.

### 🟠 9.4 `capitalize(item.status)` sin escapar

`dashboard_estudiante.js:75`:

```javascript
'<span class="tag tag-' + SIMUL.escapeHtml(item.status) + '">' +
  SIMUL.capitalize(item.status) +      // ← NO escapado
'</span>' +
```

El atributo `class` sí se escapa, pero el **texto** interior usa `capitalize()`, que
**no** escapa. Hoy es inofensivo (`status` es un enum controlado:
`publicado`/`pendiente`/`rechazado`), pero es el **único hueco** de la auditoría §8 y
un precedente peligroso: si `status` viniera de entrada de usuario, sería XSS.

### 🟠 9.5 La "autoría" se resuelve por coincidencia de subcadena

`dashboard_estudiante.js:33-37`:

```javascript
const miNombre = String(user.name).split(' ').slice(-1)[0];   // último apellido
return contenido.filter(item =>
  String(item.author).indexOf(user.name) !== -1 ||
  String(item.author).indexOf(miNombre) !== -1);              // ← frágil
```

* Un estudiante llamado "Moreno" vería el contenido de **cualquier** "Moreno".
* Si el `author` fuera `"Ana Moreno, Luis Moreno"`, coincidiría con ambos.
* Es el mismo anti-patrón que ya señaló `web_routes.py:198` (Parte 1 §6.12).

### 🟠 9.6 `mis_aportes.js` usa un selector frágil

```javascript
const LISTADO = $('.simul-card.overflow-hidden');   // ← el primer card de la página
```

Selecciona el **primer** elemento con esa combinación de clases. Si se añadiera otra
tarjeta antes (un banner, un aviso), el JS ocultaría el elemento equivocado. Debería
ser un `id` dedicado.

### 🟡 9.7 `NIVEL_MAXIMO_PUNTOS = 2000` duplicado y erróneo

`dashboard_estudiante.js:14` replica el `STUDENT_MAX_POINTS = 2000` del mock
(Parte 2 §9.5), con el mismo problema: el estudiante está en el nivel 4
([900,1500)), así que "2000" no es su techo. Además el valor está **hardcodeado** en
el JS en vez de venir del servidor.

### 🟡 9.8 El patrón depende del orden de carga

Como se explicó en §2: si `app.js` se cargara con `defer`/`async` (o se moviera
antes de los `page_scripts`), `boot()` dispararía `simul:ready` antes de que las
páginas registren sus listeners y **ninguna** funcionaría. Es un acoplamiento
invisible documentado solo por el orden de dos etiquetas `<script>`.

### 🟡 9.9 `onclick` inline y enlaces muertos

Hay 3 `onclick` inline en las plantillas, pero **no son lógica**: los tres son
`onclick="return false;"` sobre un `<a href="#">`, es decir **enlaces muertos** que
solo evitan el salto de página:

| Archivo | Línea | Contenido |
|---|---|---|
| `registro.html` | 269, 273 | `<a href="#" onclick="return false;">` (términos y condiciones) |
| `contenido.html` | 321 | `<a … onclick="return false;">` |

El **único** `onclick` con lógica real está en `mis_aportes.js:44`
(`onclick="SIMUL.closeModal()"` dentro del HTML del modal), que rompe la convención
de delegación (`[data-modal-close]`) usada en el resto del proyecto.

> Los enlaces `href="#"` con `onclick="return false;"` son **deuda de UX**: parecen
> clicables pero no llevan a ninguna parte (términos, condiciones, etc.). Deberían
> apuntar a una página real o estar deshabilitados.

### 🟡 9.10 La normalización de tildes es parcial

`buscar.js:167`:

```javascript
const normalizado = estado.categoria.toLowerCase().replace('í', 'i');
```

Solo reemplaza **`í`** (por "Investigacion"/"Investigación"). Otras tildes
(`Evento`, `Premio`, `Historia`) no las tienen, así que funciona **por suerte**. Si
mañana una categoría tuviera `ó`, `é` o `á`, el enlace profundo fallaría.

### 🟡 9.11 `contenido_no_encontrado.html` duplica la navbar

La plantilla de 404 extiende `base.html`, así que muestra la navbar completa. Es
correcto, pero el usuario llega a una página de error **con navegación**, lo que
puede confundir (debería ofrecer un enlace de vuelta explícito).

---

## 10. Deuda y repetición de código

### 10.1 La tarjeta de contenido está implementada 4 veces

| Implementación | Archivo |
|---|---|
| Partial Jinja | `partials/_content_card.html` |
| JS del núcleo | `app.js:contentCardHtml` |
| JS inline | `dashboard_estudiante.js:61-99` (variante horizontal) |
| JS inline | `admin_validacion.js` y `admin_contenido.js` (variantes de tabla/tarjeta) |

Cada una repite las clases de Tailwind. Un cambio de diseño hay que hacerlo en
varios sitios.

### 10.2 Patrón de "modal con formulario" repetido

Tanto `admin_validacion.js` (motivo de rechazo) como `mis_aportes.js`
(observaciones) y `admin_contenido.js` construyen HTML de modal a mano. El modal en
sí está centralizado (`openModal`), pero su **contenido** se duplica.

### 10.3 El filtrado en el cliente no escala

`buscar.js` filtra **todo el catálogo** en el navegador. Con 11 items del mock es
instantáneo; con miles (una BD real) habría que enviar todo el catálogo al cliente en
cada carga. **La migración a la API** (`GET /api/contenido?q=&cat=&year=`) es
obligatoria, no opcional. El propio `buscar.js:8-9` lo advierte:

> *"En la siguiente fase, este archivo se sustituye por las llamadas a
> `GET /api/contenido` con query params."*

### 10.4 Repetición de `guardPage` + `if (!user) return`

Aparece 11 veces (una por página privada). Se podría extraer a un wrapper, pero es
una repetición **aceptable** (explícita y legible).

### 10.5 Resumen de la deuda

| Prioridad | Deuda |
|---|---|
| 🔴 Alta | Guardas faltantes en `/dashboard/admin` y `/admin/publicacion` |
| 🔴 Alta | Todo el RBAC es solo cliente (heredado de Parte 1 §11.2) |
| 🟠 Media | Autoría por subcadena (§9.5) |
| 🟠 Media | Filtrado en el navegador (§10.3) |
| 🟡 Baja | Hueco de escapado (§9.4), selector frágil (§9.6), tildes (§9.10) |
| 🟡 Baja | Repetición de componentes (§10.1, §10.2) |

---

*Documento generado a partir del análisis de las 21 plantillas de `app/templates/pages/`
y los 15 scripts de `app/static/js/pages/`.*
*Parte 4 de 5. Sigue: Parte 5 — Estilos (`app.css` y utilidades `simul-*`).*
