/* ==========================================================
   BUSCAR - Filtros y resultados

   Reproduce el buscador del prototipo: texto libre, categoría
   y año. El filtrado ocurre aquí en el navegador sobre el
   catálogo que entrega la vista (RF-EXP-02).

   En la siguiente fase, este archivo se sustituye por las
   llamadas a GET /api/contenido con query params.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const CATALOGO    = window.SIMUL_CONTENT || [];
  const SLUG_MAP    = window.SIMUL_CATEGORY_SLUG || {};
  const CATEGORIAS  = window.SIMUL_CATEGORIES || [];
  const ANIOS       = window.SIMUL_YEARS || [];

  const estado = {
    texto: window.SIMUL_INITIAL_QUERY || '',
    categoria: 'Todos',
    anio: 'Todos'
  };

  const input      = $('#search-input');
  const grid       = $('#search-results');
  const skeleton   = $('#search-skeleton');
  const vacio      = $('#search-empty');
  const contador   = $('#search-count');
  const selectCat  = $('#search-cat-mobile');
  const selectAnio = $('#search-year-mobile');
  const botonLimpiar = $('#search-clear');

  /* ----------------------------------------------------------
     FILTRADO
     ---------------------------------------------------------- */

  /** Solo se muestra lo publicado en el museo. */
  function publicados() {
    return Store.getContent().filter(function (item) {
      return item.status === 'publicado';
    });
  }

  function coincide(item) {
    /* Texto libre: título o etiquetas. */
    if (estado.texto) {
      const texto = estado.texto.toLowerCase();

      const enTitulo = item.title.toLowerCase().indexOf(texto) !== -1;
      const enEtiquetas = (item.tags || []).some(function (tag) {
        return tag.toLowerCase().indexOf(texto) !== -1;
      });

      if (!enTitulo && !enEtiquetas) return false;
    }

    /* Categoría */
    if (estado.categoria !== 'Todos' && item.category !== estado.categoria) {
      return false;
    }

    /* Año: "Antes de 2019" agrupa todo lo anterior. */
    if (estado.anio !== 'Todos') {
      if (estado.anio === 'Antes de 2019') {
        if (item.year >= 2019) return false;
      } else if (String(item.year) !== estado.anio) {
        return false;
      }
    }

    return true;
  }

  function pintar() {
    const resultados = publicados().filter(coincide);

    grid.innerHTML = resultados
      .map(SIMUL.contentCardHtml)
      .join('');

    grid.classList.toggle('hidden', resultados.length === 0);
    vacio.classList.toggle('hidden', resultados.length !== 0);
    vacio.classList.toggle('flex', resultados.length === 0);

    contador.textContent = resultados.length === 0
      ? 'Sin resultados'
      : resultados.length + (resultados.length === 1
          ? ' resultado encontrado'
          : ' resultados encontrados');
  }

  /** El prototipo muestra un esqueleto ~250 ms antes de pintar. */
  function buscar() {
    skeleton.classList.remove('hidden');
    grid.classList.add('hidden');
    vacio.classList.add('hidden');

    window.clearTimeout(buscar.timer);

    buscar.timer = window.setTimeout(function () {
      skeleton.classList.add('hidden');
      pintar();
    }, 250);
  }

  /* ----------------------------------------------------------
     SINCRONIZACIÓN DE LOS FILTROS
     ---------------------------------------------------------- */

  /** Marca como activo un filtro de la barra lateral. */
  function marcarFiltros(atributo, valor) {
    $$('[' + atributo + ']').forEach(function (boton) {
      const activo = boton.getAttribute(atributo) === valor;

      boton.className = boton.className
        .replace(/bg-\[#C8102E\][^ ]* ?/g, '')
        .replace(/text-white ?/g, '')
        .replace(/hover:bg-gray-100 ?/g, '');

      boton.className = activo
        ? 'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors mb-0.5 ' +
          'bg-[#C8102E] text-white font-semibold'
        : 'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors mb-0.5 ' +
          'text-gray-600 hover:bg-gray-100';
    });
  }

  function aplicarCategoria(valor) {
    estado.categoria = valor;
    marcarFiltros('data-filter-category', valor);
    if (selectCat) selectCat.value = valor;
    buscar();
  }

  function aplicarAnio(valor) {
    estado.anio = valor;
    marcarFiltros('data-filter-year', valor);
    if (selectAnio) selectAnio.value = valor;
    buscar();
  }

  /* ----------------------------------------------------------
     ENLACE PROFUNDO  /buscar?cat=eventos
     ---------------------------------------------------------- */

  function leerParametros() {
    const params = new URLSearchParams(window.location.search);

    const slug = params.get('cat');
    if (slug && SLUG_MAP[slug]) {
      estado.categoria = SLUG_MAP[slug];
    }

    const q = params.get('q');
    if (q) {
      estado.texto = q;
      if (input) input.value = q;
    }

    /* El prototipo no distingue mayúsculas de los nombres de
       categoría; aquí se comparan sin tildes ni mayúsculas. */
    const normalizado = estado.categoria.toLowerCase().replace('í', 'i');
    const categoria = CATEGORIAS.find(function (c) {
      return c.toLowerCase().replace('í', 'i') === normalizado;
    });

    estado.categoria = categoria || 'Todos';
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    leerParametros();

    /* Refleja el estado inicial en la barra lateral. */
    $$('[data-filter-category]').forEach(function (boton) {
      if (boton.getAttribute('data-filter-category') === estado.categoria) {
        boton.className =
          'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors mb-0.5 ' +
          'bg-[#C8102E] text-white font-semibold';
      }
    });

    if (input) {
      input.addEventListener('input', function (event) {
        estado.texto = event.target.value.trim();
        buscar();
      });
    }

    $$('[data-filter-category]').forEach(function (boton) {
      boton.addEventListener('click', function () {
        aplicarCategoria(boton.getAttribute('data-filter-category'));
      });
    });

    $$('[data-filter-year]').forEach(function (boton) {
      boton.addEventListener('click', function () {
        aplicarAnio(boton.getAttribute('data-filter-year'));
      });
    });

    if (selectCat) {
      selectCat.addEventListener('change', function (event) {
        aplicarCategoria(event.target.value);
      });
    }

    if (selectAnio) {
      selectAnio.addEventListener('change', function (event) {
        aplicarAnio(event.target.value);
      });
    }

    if (botonLimpiar) {
      botonLimpiar.addEventListener('click', function () {
        estado.texto = '';
        estado.anio = 'Todos';

        if (input) input.value = '';
        aplicarCategoria('Todos');
        aplicarAnio('Todos');
      });
    }

    buscar();
  });

})();
