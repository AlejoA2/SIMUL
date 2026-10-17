# SIMUL — Documentación Técnica

> **Parte 5: Estilos y sistema de diseño**
> Continúa a [`ARQUITECTURA.md`](./ARQUITECTURA.md) (1), [`DATOS.md`](./DATOS.md) (2),
> [`FRONTEND.md`](./FRONTEND.md) (3) y [`PAGINAS.md`](./PAGINAS.md) (4).

---

## Índice

1. [Qué cubre esta parte](#1-qué-cubre-esta-parte)
2. [Cómo se carga el CSS](#2-cómo-se-carga-el-css)
3. [La paleta institucional (Tailwind)](#3-la-paleta-institucional-tailwind)
4. [`app.css`: las 8 secciones](#4-appcss-las-8-secciones)
5. [Clases del sistema: definidas vs. usadas](#5-clases-del-sistema-definidas-vs-usadas)
6. [El hallazgo central: el sistema de diseño es opcional](#6-el-hallazgo-central-el-sistema-de-diseño-es-opcional)
7. [El navbar por dentro](#7-el-navbar-por-dentro)
8. [Accesibilidad](#8-accesibilidad)
9. [Responsive](#9-responsive)
10. [Hallazgos](#10-hallazgos)
11. [Cierre de la serie](#11-cierre-de-la-serie)

---

## 1. Qué cubre esta parte

Todo el *styling* del proyecto:

| Pieza | Archivo | Líneas |
|---|---|---:|
| Hoja de estilos propia | `app/static/css/app.css` | 247 |
| Framework CSS (CDN) | `https://cdn.tailwindcss.com` | — |
| Configuración del tema | `base.html:61-86` (inline) | 26 |
| Tipografías | Google Fonts (Montserrat + Inter) | — |
| Estilos inline en plantillas/JS | dispersos | 338 hex + 386 `font-family` |

**La arquitectura de estilos son tres capas:**

```
   ┌─────────────────────────────────────────────────────────┐
   │ 1. Tailwind Play CDN  ── utilidades (flex, p-4, md:grid…)│
   │    + tailwind.config  ── paleta `simul` y tipografías    │
   ├─────────────────────────────────────────────────────────┤
   │ 2. app.css  ── clases de COMPONENTE propias              │
   │    (.simul-card, .btn-primary, .tag…, animaciones)       │
   ├─────────────────────────────────────────────────────────┤
   │ 3. style="…" inline ── lo que no encaja en 1 ni 2        │
   │    (¡y mucho de lo que sí encajaba!)                     │
   └─────────────────────────────────────────────────────────┘
```

> **La tercera capa se comió a la primera.** Es el hilo conductor de esta parte:
> existe un sistema de diseño declarado (capa 1) que el código **casi no usa**,
> porque todo se resuelve con `style="…"` inline.

---

## 2. Cómo se carga el CSS

`base.html` (el layout, Parte 3 §2) monta el pipeline en este orden:

```django
{# 1. Tipografías #}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

{# 2. Tailwind por CDN + configuración del tema #}
<script src="https://cdn.tailwindcss.com"></script>
<script>
    tailwind.config = { theme: { extend: { colors: { simul: {…} }, fontFamily: {…} } } };
</script>

{# 3. CSS propio #}
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

### ⚠ `cdn.tailwindcss.com` es el **Play CDN**, no es para producción

El propio comentario de `base.html:53-54` lo admite:

> *"En producción se recomienda compilar Tailwind durante el proceso de construcción."*

El Play CDN **compila Tailwind en el navegador** en cada carga:

| Consecuencia | Detalle |
|---|---|
| Peso | El script de Tailwind (~100 KB+) + generación de estilos en runtime |
| FOUC | Los estilos propios tardan en aplicarse → parpadeo (se suma al FOUC de `data-requires-auth` de Parte 3 §9.3) |
| Sin purge | No hay árbol de estilos eliminados → se descarga el motor completo |
| Dependencia de red | Sin CDN accesible, **toda** la apariencia desaparece |

**Es el hallazgo de mayor impacto en rendimiento del proyecto** (§10.1).

### El orden importa (otra vez)

`app.css` se carga **después** del CDN. Por eso sus reglas de componente ganan
sobre las utilidades de Tailwind de igual especificidad (p. ej. `.simul-card` frente
a `border`). Esto explica por qué `.simul-card` funciona aun mezclándose con utilidades.

---

## 3. La paleta institucional (Tailwind)

`base.html:62-86` declara la identidad visual como tokens reutilizables:

```javascript
tailwind.config = {
  theme: { extend: {
    colors: {
      simul: {
        red:          '#C8102E',   // rojo institucional (Universidad Libre)
        'red-dark':   '#A00D24',
        'red-light':  '#E8153A',
        gold:         '#C9A84C',   // dorado (gamificación / Hall de la Fama)
        'gold-light': '#E2C06A',
        'gold-dark':  '#A88535',
        black:        '#1A1A1A',   // negro de marca (navbar, titulares)
        gray:         '#6B7280',
        'gray-light': '#F4F4F5',
        border:       '#E5E7EB'
      }
    },
    fontFamily: {
      display: ['Montserrat', 'sans-serif'],  // títulos
      body:    ['Inter', 'sans-serif']        // texto corrido
    }
  }}
};
```

**11 tokens de color + 2 familias tipográficas.** La intención es que se use
`bg-simul-red`, `text-simul-black`, `font-display`, etc.

### ⚠ Pero casi nunca se usan

| Token declarado | Veces usado como clase |
|---|---:|
| `text-simul-gold-light` (`_navbar.html:43`) | 1 |
| `hover:text-simul-red` (`_navbar.html:108`) | 1 |
| `text-simul-gold-light` (otro) | 1 |
| `bg-simul-*` / `border-simul-*` | 1 |
| **Total clases `*-simul-*`** | **4** |
| `font-display` | **0** |
| `font-body` | **0** |

Un sistema de diseño de 13 tokens que **el código ignora** en el 99,9 % de los casos.

En su lugar, los colores se escriben **a mano**:

| Color | Hex | Apariciones inline |
|---|---|---:|
| Rojo institucional | `#C8102E` | **134** |
| Negro de marca | `#1A1A1A` | **82** |
| Dorado | `#C9A84C` | **21** |
| (otros grises/fondos) | — | ~101 |
| **Total hex hardcodeados** | | **338** |

Es decir: `bg-[#1A1A1A]` (clase arbitraria de Tailwind) o
`style="color:#C8102E"` **en vez de** `bg-simul-black` / `text-simul-red`.

> **Ejemplo en el navbar** (`_navbar.html:17`): `class="… bg-[#1A1A1A] …"`
> en lugar del token `bg-simul-black` que existe justo para esto.

---

## 4. `app.css`: las 8 secciones

247 líneas organizadas en 8 bloques numerados. Documentadas en orden:

### §1 — BASE (líneas 14-23)

```css
body { font-family: 'Inter', sans-serif; background: #ffffff; color: #1A1A1A;
       -webkit-font-smoothing: antialiased; }
h1, h2, h3, h4, h5, h6 { font-family: 'Montserrat', sans-serif; }
```

Define la tipografía **global** (Inter) y hace que **todos** los títulos sean
Montserrat. Es la única regla que aplica la identidad tipográfica de forma
centralizada — el resto la repite inline.

### §2 — SCROLLBAR (líneas 30-57)

Barra de scroll de 6 px, gris `#D1D5DB`, con hover `#9CA3AF`. Y la utilidad
`.scrollbar-hide` (oculta la barra) para la línea de tiempo horizontal
(`contenido.html`). Usada **1 vez**.

### §3 — TARJETA SIMUL (líneas 64-75)

```css
.simul-card {
    background: white; border-radius: 10px; border: 1px solid #E5E7EB;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    transition: box-shadow .2s, transform .2s;
}
.simul-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.10); transform: translateY(-1px); }
```

**La clase más usada del sistema: 60 apariciones.** Es el contenedor estándar
(tarjetas de contenido, paneles de dashboard, filas de tabla, modales).

### §4 — BOTONES (líneas 82-141)

Tres variantes, todas con `font-family: Montserrat`, `border-radius: 8px`,
`padding: 10px 22px`, `font-size: 14px`:

| Clase | Fondo | Texto | Borde | Hover | Usos |
|---|---|---|---|---:|
| `.btn-primary` | `#C8102E` | blanco | — | `#A00D24` | **28** |
| `.btn-secondary` | blanco | `#C8102E` | 2px `#C8102E` | `#FEF2F2` | **17** |
| `.btn-gold` | `#C9A84C` | blanco | — | `#A88535` | **1** |

`.btn-primary` define además `:active { transform: scale(.98) }` y un estado
`:disabled` (fondo `#D1D5DB`, texto `#9CA3AF`).

> Nota: `.btn-gold` se usa **una sola vez** (es la variante "premio"), mientras
> `.btn-primary`/`.btn-secondary` son el 96 % de los botones.

### §5 — ETIQUETAS DE ESTADO Y CATEGORÍA (líneas 148-166)

`.tag` (pastilla: `padding 3px 10px`, `border-radius 20px`, `font-size 11px`) y
**9 variantes de color**:

| Variante | Fondo | Texto | Usos |
|---|---|---:|---:|
| `.tag-pendiente` | `#FEF3C7` | `#92400E` | 5 |
| `.tag-publicado` | `#D1FAE5` | `#065F46` | 5 |
| `.tag-rechazado` | `#FEE2E2` | `#991B1B` | 4 |
| `.tag-blue` | `#DBEAFE` | `#1E40AF` | 10 |
| `.tag-red` | `#FEE2E2` | `#C8102E` | 1 |
| `.tag-purple` | `#EDE9FE` | `#5B21B6` | **0** |
| `.tag-green` | `#D1FAE5` | `#065F46` | **0** |
| `.tag-orange` | `#FEF3C7` | `#92400E` | **0** |
| `.tag-gold` | `#F5EBD0` | `#8A6D1F` | **0** |

**Debt:** `tag-green` y `tag-publicado` son **idénticas**; `tag-orange` y
`tag-pendiente` son **idénticas**. Cuatro variantes (`purple`, `green`, `orange`,
`gold`) están **sin usar** → 4/9 de este bloque es CSS muerto.

### §6 — BARRA DE PROGRESO DORADA (líneas 173-177)

```css
.gold-bar { background: linear-gradient(90deg, #C9A84C, #E2C06A);
            border-radius: 4px; height: 8px; }
```

Barra de gamificación (progreso hacia el siguiente nivel). **3 usos**:
`dashboard_estudiante`, `perfil`, `ranking`.

### §7 — ANIMACIONES (líneas 184-205)

```css
@keyframes fadeIn        { from { opacity:0; transform:translateY(8px) } to {…} }
@keyframes slideInRight  { from { opacity:0; transform:translateX(20px) } to {…} }
@keyframes fadeOut       { from { opacity:1; transform:translateY(0) } to {…} }

.animate-fade-in   { animation: fadeIn .3s ease forwards; }   /* 6 usos */
.animate-slide-right { animation: slideInRight .3s ease forwards; }  /* 0 usos */
```

**CSS muerto aquí:** `@keyframes fadeOut` no lo referencia **ninguna** clase (nadie
lo usa), y `.animate-slide-right` tiene **0 usos**.

### §8 — UTILIDADES (líneas 212-247)

| Clase | Qué hace | Usos |
|---|---|---:|
| `.line-clamp-2` | Recorta el texto a 2 líneas (tarjetas) | 5 |
| `.profile-banner` | Degradado rojo `#C8102E → #8B0000` (cabecera de perfil) | 1 |
| `[data-*-auth-hidden]` | `display:none !important` hasta que `app.js` confirme la sesión | `app.js` (6) |
| `.dot-ring` | Anillo interior blanco en los puntos de la línea de tiempo | **0** |
| `.bar-value` / `.bar-slot` | El valor del gráfico aparece al pasar el cursor | 1 |

**El único `!important` de todo el CSS** está en la regla de `data-auth-hidden`
(línea 231), y es **justificado**: debe ganar a las utilidades de Tailwind
(`hidden`, `flex`) que `app.js` manipula. Es la solución al *flash* de los bloques
con sesión (Parte 3 §9.3).

---

## 5. Clases del sistema: definidas vs. usadas

Resumen de las clases propias de `app.css`:

| Clase | Definida | Usada | Veredicto |
|---|:--:|:--:|---|
| `.simul-card` | ✅ | 60 | ✅ Núcleo |
| `.btn-primary` | ✅ | 28 | ✅ Núcleo |
| `.btn-secondary` | ✅ | 17 | ✅ Núcleo |
| `.tag-*` (pendiente/publicado/rechazado/blue/red) | ✅ | 25 | ✅ |
| `.animate-fade-in` | ✅ | 6 | ✅ |
| `.line-clamp-2` | ✅ | 5 | ✅ |
| `.gold-bar` | ✅ | 3 | ✅ |
| `.scrollbar-hide` | ✅ | 1 | 🟡 Marginal |
| `.profile-banner` | ✅ | 1 | 🟡 Marginal |
| `.btn-gold` | ✅ | 1 | 🟡 Marginal |
| `.bar-value` / `.bar-slot` | ✅ | 1 | 🟡 Marginal |
| `.tag-purple` | ✅ | **0** | ❌ Muerto |
| `.tag-green` | ✅ | **0** | ❌ Muerto (dup. de publicado) |
| `.tag-orange` | ✅ | **0** | ❌ Muerto (dup. de pendiente) |
| `.tag-gold` | ✅ | **0** | ❌ Muerto |
| `.animate-slide-right` | ✅ | **0** | ❌ Muerto |
| `.dot-ring` | ✅ | **0** | ❌ Muerto |
| `@keyframes fadeOut` | ✅ | **0** | ❌ Muerto (sin clase) |

**~7 definiciones muertas** de ~20. Y del sistema de tokens Tailwind (13), solo 4 usos.

---

## 6. El hallazgo central: el sistema de diseño es opcional

El proyecto **tiene** un sistema de diseño, pero lo trata como una sugerencia. La
evidencia, en tres cifras:

| Métrica | Valor | Qué significa |
|---|---:|---|
| Colores hex hardcodeados en plantillas+JS | **338** | Se escribe el color a mano en vez de usar un token |
| Declaraciones `font-family` inline | **386** | Se repite la tipografía en vez de usar `font-display` |
| Clases Tailwind con valor arbitrario `[#hex]` | **116** | `bg-[#1A1A1A]` en vez de `bg-simul-black` |

### El caso de la tipografía

`app.css` ya hace `h1..h6 → Montserrat` y `body → Inter` (§1). Aun así hay
**386** repeticiones inline como esta (mismo navbar):

```django
<a … style="font-family: 'Montserrat', sans-serif;">Explorar</a>
<a … style="font-family: 'Montserrat', sans-serif;">Eventos</a>
<a … style="font-family: 'Montserrat', sans-serif;">Hall de la Fama</a>
<a … style="font-family: 'Montserrat', sans-serif;">Ranking</a>
```

Todas podrían ser `class="font-display"` (que **existe y no se usa**) o simplemente
nada, porque ya son encabezados/`<a>` con clase propia.

### Por qué importa (más allá de la estética)

| Problema | Consecuencia |
|---|---|
| Cambiar el rojo institucional | **134** sustituciones a mano (o un *find-and-replace* arriesgado) |
| Rebranding tipográfico | **386** cambios |
| Auditar contraste | Hay que revisar cada `style="color:…"`, no los tokens |
| Consistencia | Ya hayderiva: `#C8102E` vs `#A00D24` vs `#E8153A` conviven sin criterio claro |
| Peso HTML | Cada `style` infla el HTML servido (sin caché de CSS) |

> **Buena práctica detenida a mitad de camino:** el equipo *creó* los tokens
> (`simul`), pero no los *adoptó*. La corrección es mecánica (reemplazar hex por
> clases) y de alto retorno.

---

## 7. El navbar por dentro

`_navbar.html` (278 líneas, Parte 3 §3.4) es el componente más complejo y el mejor
ejemplo de la mezcla de capas. Sus decisiones de estilo:

| Aspecto | Implementación | Comentario |
|---|---|---|
| Fondo | `class="… bg-[#1A1A1A] …"` (l.17) | Hex **arbitrario** en vez de `bg-simul-black` |
| Sombra | `style="box-shadow: 0 2px 12px rgba(0,0,0,.35)"` (l.18) | Inline, sin clase |
| Posición | `fixed top-0 … z-40` + `style="z-index:50"` en el menú (l.168) | Dos sistemas de z-index a la vez |
| Marca | `<span style="font-family:'Montserrat';font-weight:800;font-size:20px…">SIMUL` (l.38) | 5 propiedades inline |
| Enlaces | `style="font-family:'Montserrat'…"` ×4 | Repetido |
| Puntos | `style="color:#C9A84C"` (l.182) | Hex inline en vez de `text-simul-gold` |
| Botón sesión | `class="btn-primary text-sm px-4 py-2"` (l.269) | ✅ Único punto que **usa** la clase del sistema |
| Datos de sesión | `data-user-name`, `data-user-points`, `data-user-level` | Los rellena `paintUser` |

**14 `style="…"` y 11 `font-family` inline** en un solo archivo. Y solo **2 usos de
tokens** (`text-simul-gold-light`, `hover:text-simul-red`) — la ironía: los únicos
sitios que usan el sistema de diseño son los que **no** podían escribir el color a mano
(porque son variantes `hover:`/`text-` de Tailwind).

### Sin menú móvil

```django
<div class="hidden md:flex items-center gap-1">   {# l.54: enlaces principales #}
```

En pantallas pequeñas (`< md`), los enlaces **Explorar / Eventos / Hall de la Fama /
Ranking** simplemente **desaparecen**, y **no hay botón hamburguesa** que los
sustituya (los 2 *hits* de "toggle" son el menú de usuario, no la navegación).
En móvil solo quedan: logo, lupa, menú de usuario (si hay sesión) y "Iniciar sesión".

> **Hallazgo de UX/responsive:** la navegación principal es inaccesible en móvil
> salvo por enlaces secundarios dentro de las páginas.

---

## 8. Accesibilidad

`app.css` **no define ni un solo `:focus`**, ni `prefers-reduced-motion`, ni usa
variables CSS. Estado:

| Aspecto | Estado | Detalle |
|---|---|---|
| `@media` en app.css | **0** | Todo lo responsive lo aporta Tailwind |
| Variables CSS (`--token`) | **0** | No hay tokens en CSS; los colores se repiten |
| `:focus` / `:focus-visible` | **0** | Se delega en el estilo por defecto del navegador |
| `prefers-reduced-motion` | **0** | Las animaciones **siempre** corren |
| `!important` | **1** | Solo en `data-auth-hidden` (justificado) |

### Contraste de color (WCAG AA = 4.5:1 para texto normal)

| Combinación | Ratio aprox. | ¿Pasa AA? |
|---|---:|:--:|
| Texto `#1A1A1A` sobre blanco (cuerpo) | **~17:1** | ✅ Excelente |
| Blanco sobre `#C8102E` (`.btn-primary`) | **~5.9:1** | ✅ |
| `#C8102E` sobre `#FEE2E2` (`.tag-red`) | **~4.8:1** | ✅ (al límite) |
| Blanco sobre `#C9A84C` (`.btn-gold`) | **~2.3:1** | ❌ **Falla** |

**El único fallo de contraste es `.btn-gold`** (texto blanco sobre dorado). Con
~2.3:1 ni siquiera cumple el umbral de texto grande (3:1). Ocurre una vez, pero es
el botón "premio" — justo el que debería ser más legible. La solución es usar texto
oscuro (`#1A1A1A` o `#8A6D1F`) sobre el dorado.

### Movimiento

`.animate-fade-in` (6 usos) y las transiciones de `.simul-card` corren siempre.
Sin `prefers-reduced-motion`, los usuarios con sensibilidad al movimiento no pueden
desactivarlas. Es una omisión, no un error grave (RNF de accesibilidad no lo exige
explícitamente, pero es la práctica recomendada).

---

## 9. Responsive

Todo el comportamiento adaptable viene de **utilidades de Tailwind**, no de
`app.css`:

| Prefijo | Ocurrencias |
|---|---:|
| `sm:` | 37 |
| `md:` | 13 |
| `lg:` | 30 |
| `xl:` | 4 |
| **Total** | **84** |

El patrón más común es la rejilla que colapsa: `grid md:grid-cols-3 lg:grid-cols-4`,
y el `hidden md:flex` del navbar (§7). El ancho máximo de contenido es
`max-w-[1440px]` (navbar) y cada página centra su bloque con `max-w-*`.

**No hay puntos de quiebre propios** ni ajustes finos en CSS. Es un enfoque
*correcto* (delegar lo responsive en Tailwind) salvo por el hueco del menú móvil (§7).

---

## 10. Hallazgos

### 🔴 10.1 Tailwind por CDN (Play CDN) en "producción"

`cdn.tailwindcss.com` compila en el navegador en cada carga. Es la recomendación
**explícita** de no usar en producción; el comentario de `base.html:53` ya lo sabe
pero no se ha corregido. Impacto: peso, FOUC y dependencia de red (§2). La solución
es compilar Tailwind en el `Dockerfile`/build y servir un CSS estático.

### 🟠 10.2 El sistema de diseño se ignora (338 hex + 386 `font-family`)

El hallazgo central (§6). Existen tokens para todo (11 colores + 2 familias) y se
usan **4 veces** en total; el resto son valores a mano. Consecuencia: rebranding
caro, deriva de color, sin fuente única de verdad.

### 🟠 10.3 `.btn-gold` falla el contraste (2.3:1)

El único fallo WCAG AA detectable (§8). Texto blanco sobre `#C9A84C`.

### 🟠 10.4 Sin navegación móvil

Los enlaces principales son `hidden md:flex` sin menú hamburguesa (§7). En móvil, la
navegación primaria desaparece.

### 🟡 10.5 CSS muerto (~7 reglas)

`.tag-purple`, `.tag-green`, `.tag-orange`, `.tag-gold`, `.animate-slide-right`,
`.dot-ring` y `@keyframes fadeOut`: definidos y nunca usados. Además `tag-green` ≡
`tag-publicado` y `tag-orange` ≡ `tag-pendiente` (duplicación).

### 🟡 10.6 Sin `prefers-reduced-motion` ni estilos de `:focus`

Las animaciones no se pueden desactivar; el foco se delega al navegador (§8).

### 🟡 10.7 Sin variables CSS

`var(--*)` aparece **0** veces. Los colores viven duplicados entre `app.css`, el
`tailwind.config` y cientos de `style` inline. Una capa de custom properties
(`--simul-red: #C8102E` en `:root`) unificaría las tres.

### 🟡 10.8 `z-index` en dos sistemas

El navbar usa la escala de Tailwind (`z-40`) **y** un `style="z-index:50"` inline
(`_navbar.html:168`). No hay escala única de apilamiento.

---

## 11. Cierre de la serie

Con esta parte se cierra el recorrido de SIMUL:

| Parte | Documento | Contenido |
|---|---|---|
| **1** | [`ARQUITECTURA.md`](./ARQUITECTURA.md) | Arquitectura general + backend `.py` línea a línea + requerimientos |
| **2** | [`DATOS.md`](./DATOS.md) | `simul_data.py` (la "BD en Python") + esquema MySQL propuesto |
| **3** | [`FRONTEND.md`](./FRONTEND.md) | Núcleo del frontend (`app.js`, `store.js`, `api.js`, navbar, layout) |
| **4** | [`PAGINAS.md`](./PAGINAS.md) | Las 21 páginas y los 15 scripts + auditoría XSS |
| **5** | `ESTILOS.md` (este) | `app.css`, paleta Tailwind, accesibilidad, responsive |

### La idea que atraviesa las cinco partes

SIMUL es un **prototipo funcional de altísima fidelidad visual** sostenido por
**dos sistemas paralelos que nunca se conectaron**:

1. **El backend real** (`auth_bp`/`product_bp`, JWT + MySQL) — correcto pero
   **desconectado** de la interfaz (Parte 1).
2. **El museo** (`web_bp` + 21 páginas) — funciona **entero en el navegador**
   con datos mock y `localStorage` (Partes 2-4).

Y sobre ellos, un **sistema de diseño declarado pero no adoptado** (Parte 5).

Ninguno de los tres es "código malo": cada uno está bien hecho **para su
propósito** (demostrar, validar diseño, enseñar la arquitectura objetivo). El
trabajo pendiente no es reescribir, sino **conectar y unificar**: API ↔ frontend,
Store ↔ MySQL, tokens ↔ presentación.

### Prioridades sugeridas

| Prioridad | Acción | Parte |
|---|---|---|
| 🔴 | Compilar Tailwind (quitar Play CDN) | 5 §10.1 |
| 🔴 | Conectar `api.js` ↔ `Store` (o eliminar uno) | 1 y 3 |
| 🔴 | Guardas de rol en servidor (no solo cliente) | 1, 4 |
| 🟠 | Migrar `simul_data.py` a MySQL (15 tablas ya diseñadas) | 2 |
| 🟠 | Adoptar los tokens `simul-*` (reemplazar 338 hex) | 5 §10.2 |
| 🟠 | Corregir contraste de `.btn-gold` y añadir menú móvil | 5 §10.3-10.4 |
| 🟡 | Purgar CSS y templates muertos | 5 §10.5, 4 |

---

*Documento generado a partir de `app/static/css/app.css` (247 líneas), la
configuración de Tailwind y las tipografías de `app/templates/base.html`, y una
auditoría de colores, tipografías, clases y accesibilidad sobre las 29 plantillas y
los 18 scripts.*
*Parte 5 de 5. **Serie completa.***
