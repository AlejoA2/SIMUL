/* ==========================================================
   PANEL DEL DOCENTE
   Aportes y proyectos leídos desde la API del museo.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const CONTENEDOR = $('#teacher-proposals');
  const TABLA      = $('.simul-card.overflow-hidden');

  const CABECERA =
    '<div ' +
    'class="grid grid-cols-[1fr_110px_110px_80px] gap-4 px-5 py-3 ' +
    'border-b border-gray-100 bg-gray-50" ' +
    'style="font-family: \'Montserrat\', sans-serif; font-size: 11px; ' +
    'font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; ' +
    'color: #6B7280;"' +
    '>' +
      '<span>Título</span>' +
      '<span>Categoría</span>' +
      '<span>Estado</span>' +
      '<span class="text-right">Año</span>' +
    '</div>';

  const CLASE_INDICADORES =
    '.grid.grid-cols-1.sm\\:grid-cols-3.gap-5.mb-8 ' +
    '> .simul-card > p.text-3xl';

  let pares = [];

  /* ----------------------------------------------------------
     1. APORTES REALES
     ---------------------------------------------------------- */

  function tagDeEstado(estado) {
    const mapa = {
      publicado: 'tag-publicado',
      pendiente: 'tag-pendiente',
      rechazado: 'tag-rechazado'
    };

    return mapa[estado] || 'tag-blue';
  }

  function anioDe(item, detalle) {
    if (detalle && detalle.anio) return detalle.anio;
    if (item && item.anio) return item.anio;

    const fecha = String((item && item.fec_crea) || '').slice(0, 4);
    return fecha || '—';
  }

  function integrantesDe(detalle) {
    const lista = (detalle && detalle.integrantes) || [];
    const nombres = lista
      .map(function (persona) { return persona.nombre; })
      .filter(Boolean);

    return nombres.length
      ? nombres.join(', ')
      : 'Sin integrantes registrados';
  }

  function fila(par) {
    const item = par.item;
    const detalle = par.detalle;
    const id = item.id_contenido;
    const estado = item.estado || 'pendiente';

    return '' +
      '<a href="/contenido/' + encodeURIComponent(id) + '" ' +
      'class="grid grid-cols-[1fr_110px_110px_80px] gap-4 px-5 py-4 ' +
      'items-center border-b border-gray-50 hover:bg-gray-50 ' +
      'transition-colors">' +
        '<span class="min-w-0">' +
          '<span class="block text-sm font-semibold text-gray-800 truncate" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(item.titulo || 'Sin título') +
          '</span>' +
          '<span class="block text-xs text-gray-400 truncate" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            SIMUL.escapeHtml(item.tipo || 'Contenido') +
          '</span>' +
        '</span>' +

        '<span class="tag tag-blue">' +
          SIMUL.escapeHtml(item.categoria || '—') +
        '</span>' +

        '<span class="tag ' + tagDeEstado(estado) + '">' +
          SIMUL.capitalize(estado) +
        '</span>' +

        '<span class="text-sm text-gray-500 text-right" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(anioDe(item, detalle)) +
        '</span>' +
      '</a>';
  }

  function tarjetaProyecto(par) {
    const item = par.item;
    const detalle = par.detalle;
    const estado = item.estado || 'pendiente';
    const subtipo = (detalle && detalle.subtipo) || {};
    const asesor = subtipo.asesor;

    return '' +
      '<a href="/contenido/' + encodeURIComponent(item.id_contenido) + '" ' +
      'class="simul-card p-4 block hover:border-[#C8102E] ' +
      'transition-colors">' +

        '<div class="flex items-start justify-between gap-3 mb-2">' +
          '<span class="text-sm font-semibold text-gray-800 line-clamp-2" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(item.titulo || 'Sin título') +
          '</span>' +
          '<span class="tag ' + tagDeEstado(estado) + ' shrink-0">' +
            SIMUL.capitalize(estado) +
          '</span>' +
        '</div>' +

        '<p class="text-xs text-gray-500 mb-1" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '📅 ' + SIMUL.escapeHtml(anioDe(item, detalle)) +
        '</p>' +

        '<p class="text-xs text-gray-400 truncate" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '👥 ' + SIMUL.escapeHtml(integrantesDe(detalle)) +
        '</p>' +

        '<p class="text-xs text-gray-400 mt-1" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '🧑‍🏫 ' + SIMUL.escapeHtml(
            asesor ? 'Asesor: ' + asesor : 'Sin asesor registrado'
          ) +
        '</p>' +

      '</a>';
  }

  /* ----------------------------------------------------------
     2. PINTADO
     ---------------------------------------------------------- */

  function actualizarIndicadores(lista) {
    const nodos = SIMUL.$$(CLASE_INDICADORES);
    if (nodos.length < 3) return;

    const conteo = { publicado: 0, pendiente: 0, rechazado: 0 };

    lista.forEach(function (par) {
      const estado = par.item.estado;
      if (conteo[estado] !== undefined) conteo[estado]++;
    });

    nodos[0].textContent = conteo.publicado;
    nodos[1].textContent = conteo.pendiente;
    nodos[2].textContent = conteo.rechazado;
  }

  function pintar(lista, huboError) {
    pares = lista;
    actualizarIndicadores(pares);

    if (TABLA) {
      const filas = pares.length
        ? pares.map(fila).join('')
        : '<div class="px-5 py-12 text-center">' +
            '<p class="text-3xl mb-3">📭</p>' +
            '<p class="text-sm text-gray-500" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              (huboError
                ? 'No se pudieron cargar tus aportes desde la API.'
                : 'Todavía no has registrado contenido.') +
            '</p>' +
          '</div>';

      TABLA.innerHTML = CABECERA + filas;
    }

    if (!CONTENEDOR) return;

    const proyectos = pares.filter(function (par) {
      return par.item.tipo === 'proyecto';
    });

    if (proyectos.length === 0) {
      CONTENEDOR.innerHTML =
        '<div class="simul-card p-6 text-center">' +
          '<div class="text-3xl mb-2">💡</div>' +
          '<p class="text-xs text-gray-500" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            (huboError
              ? 'No se pudieron cargar tus proyectos desde la API.'
              : 'No tienes proyectos registrados con tu cuenta.') +
          '</p>' +
        '</div>';
      return;
    }

    CONTENEDOR.innerHTML =
      '<p class="text-xs text-gray-500 mb-1" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Proyectos registrados con tu cuenta (datos de la API).' +
      '</p>' +
      proyectos.map(tarjetaProyecto).join('');
  }

  function cargar() {
    return SIMULApi.misAportes()
      .then(function (lista) {
        const aportes = Array.isArray(lista) ? lista : [];

        return Promise.all(aportes.map(function (item) {
          const numero = SIMULApi.idNumerico(item.id_contenido);
          if (!numero) return Promise.resolve(null);

          return SIMULApi.contenidoDetalle(numero)
            .catch(function () { return null; });
        })).then(function (detalles) {
          return aportes.map(function (item, indice) {
            return { item: item, detalle: detalles[indice] };
          });
        });
      })
      .then(function (lista) {
        pintar(lista, false);
      })
      .catch(function (error) {
        pintar([], true);
        SIMUL.toast(
          error.message || 'No se pudieron cargar tus aportes',
          'error'
        );
      });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('teacher')) return;

    cargar();
  });

})();
