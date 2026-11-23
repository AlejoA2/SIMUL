/* ==========================================================
   BUSCAR - Filtros y resultados

   El catálogo se consulta en GET /api/museo/contenido. Los
   filtros de texto, categoría y año se envían a la API; el
   resultado que llega se convierte a tarjeta y se pinta.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const SLUG_MAP    = window.SIMUL_CATEGORY_SLUG || {};
  const CATEGORIAS  = window.SIMUL_CATEGORIES || [];

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

  let filasAPI = [];
  let totalAPI = 0;
  let ultimaConsulta = 0;

  /* ----------------------------------------------------------
     DATOS DE LA API → TARJETA
     ---------------------------------------------------------- */

  function aTarjeta(item) {
    return {
      id: item.id_contenido,
      title: item.titulo,
      year: item.anio,
      category: item.categoria,
      categoryTag: 'tag-blue',
      description: item.descripcion,
      image: item.imagen,
      author: (item.autor && item.autor.nombre) || 'Autor del museo',
      tags: item.tipo ? [item.tipo] : [],
      status: 'publicado'
    };
  }

  function parametros() {
    const params = { per_page: 100 };

    if (estado.texto) params.q = estado.texto;
    if (estado.categoria !== 'Todos') params.categoria = estado.categoria;

    /* «Antes de 2019» no es un año exacto: se pide todo y se
       filtra abajo. Para los demás años la API filtra. */
    if (estado.anio !== 'Todos' && estado.anio !== 'Antes de 2019') {
      params.anio = estado.anio;
    }

    return params;
  }

  function pintar(filas) {
    filasAPI = filas || [];
    totalAPI = filasAPI.length;

    grid.innerHTML = filasAPI.map(SIMUL.contentCardHtml).join('');

    grid.classList.toggle('hidden', filasAPI.length === 0);
    vacio.classList.toggle('hidden', filasAPI.length !== 0);
    vacio.classList.toggle('flex', filasAPI.length === 0);

    contador.textContent = totalAPI === 0
      ? 'Sin resultados'
      : totalAPI + (totalAPI === 1
          ? ' resultado encontrado'
          : ' resultados encontrados');
  }

  /* ----------------------------------------------------------
     BÚSQUEDA CONTRA LA API
     ---------------------------------------------------------- */

  function buscar() {
    const numero = ++ultimaConsulta;

    skeleton.classList.remove('hidden');
    grid.classList.add('hidden');
    vacio.classList.add('hidden');

    SIMULApi.contenido(parametros())
      .then(function (respuesta) {
        if (numero !== ultimaConsulta) return;

        const items = (respuesta && respuesta.items) || [];
        let filas = items.map(aTarjeta);

        if (estado.anio === 'Antes de 2019') {
          filas = filas.filter(function (item) {
            return Number(item.year) < 2019;
          });
        }

        pintar(filas);
      })
      .catch(function (error) {
        if (numero !== ultimaConsulta) return;
        pintar([]);
        SIMUL.toast(error.message || 'No se pudo consultar el catálogo', 'error');
      })
      .then(function () {
        if (numero === ultimaConsulta) skeleton.classList.add('hidden');
      });
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

    /* El prototipo no distinguía mayúsculas ni tildes. */
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
