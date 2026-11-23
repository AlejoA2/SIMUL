/* ==========================================================
   MIS APORTES  (RF-DSH-02 + RNF-SEG-04)

   El historial sale de SIMULApi.misAportes(). El modal de
   observaciones sigue siendo el canal privado entre el autor
   y el revisor cuando una pieza fue rechazada.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const LISTADO = $('.simul-card.overflow-hidden');
  const VACIO   = $('#contributions-empty');
  const RESUMEN = LISTADO ? LISTADO.previousElementSibling : null;

  function texto(valor) {
    return valor === null || valor === undefined ? '' : String(valor);
  }

  function fechaCorta(valor) {
    const textoValor = texto(valor);
    if (!textoValor) return '';

    const fecha = new Date(textoValor);
    if (!isNaN(fecha.getTime())) return fecha.toLocaleDateString('es-CO');

    return textoValor;
  }

  /* ----------------------------------------------------------
     MODAL DE OBSERVACIONES
     ---------------------------------------------------------- */

  function modalObservaciones(titulo, observaciones) {
    return '' +
      '<h3 class="text-lg mb-1" ' +
      'style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
      'color:#1A1A1A">' +
        SIMUL.escapeHtml(titulo) +
      '</h3>' +

      '<p class="text-xs mb-5" ' +
      'style="font-family:\'Inter\',sans-serif;color:#6B7280">' +
        'Motivo registrado por el administrador al rechazar el aporte.' +
      '</p>' +

      '<div class="p-4 rounded-xl bg-red-50 border-l-4 border-[#C8102E]">' +
        '<p class="text-sm text-gray-700 leading-relaxed" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(observaciones) +
        '</p>' +
      '</div>' +

      '<div class="mt-6 flex justify-end">' +
        '<button type="button" onclick="SIMUL.closeModal()" ' +
        'class="btn-secondary">Entendido</button>' +
      '</div>';
  }

  /* ----------------------------------------------------------
     PINTADO
     ---------------------------------------------------------- */

  function filaAporte(item) {
    const titulo = texto(item.titulo);
    const estado = texto(item.estado || 'pendiente');
    const observaciones = texto(item.observaciones);
    const tipo = texto(item.tipo || item.categoria || '—');
    const fecha = fechaCorta(item.fec_crea || item.anio);

    return '' +
      '<div class="grid grid-cols-[1fr_120px_130px_110px] gap-4 ' +
      'px-5 py-4 items-center border-b border-gray-50">' +

        '<div class="min-w-0">' +
          '<p class="text-sm font-semibold text-gray-800 truncate" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(titulo) +
          '</p>' +

          (estado === 'rechazado'
            ? '<button type="button" ' +
              'data-observations="' + SIMUL.escapeHtml(observaciones) + '" ' +
              'data-title="' + SIMUL.escapeHtml(titulo) + '" ' +
              'class="text-xs font-semibold mt-1 hover:underline" ' +
              'style="font-family:\'Inter\',sans-serif;color:#C8102E">' +
                'Ver observaciones del revisor' +
              '</button>'
            : '') +
        '</div>' +

        '<span class="tag tag-blue">' + SIMUL.escapeHtml(tipo) + '</span>' +

        '<span class="tag tag-' + SIMUL.escapeHtml(estado) + '">' +
          SIMUL.escapeHtml(SIMUL.capitalize(estado)) +
        '</span>' +

        '<span class="text-sm text-gray-500 text-right" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(fecha) +
        '</span>' +

      '</div>';
  }

  function pintarResumen(items) {
    if (!RESUMEN) return;

    const conteos = { publicado: 0, pendiente: 0, rechazado: 0 };
    items.forEach(function (item) {
      const estado = texto(item.estado);
      if (conteos[estado] !== undefined) conteos[estado] += 1;
    });

    Object.keys(conteos).forEach(function (estado) {
      const etiqueta = $('.tag-' + estado, RESUMEN);
      const numero = etiqueta && etiqueta.nextElementSibling;
      if (numero) numero.textContent = conteos[estado];
    });
  }

  function pintar(items) {
    if (!LISTADO) return;

    const cabecera = $('.grid', LISTADO);
    LISTADO.innerHTML =
      (cabecera ? cabecera.outerHTML : '') +
      items.map(filaAporte).join('');

    LISTADO.classList.toggle('hidden', items.length === 0);

    if (VACIO) {
      VACIO.classList.toggle('hidden', items.length !== 0);
      VACIO.classList.toggle('flex', items.length === 0);
    }

    pintarResumen(items);
  }

  function mostrarMensaje(markup) {
    if (LISTADO) LISTADO.classList.add('hidden');
    if (RESUMEN) RESUMEN.classList.add('hidden');

    if (VACIO) {
      VACIO.innerHTML = markup;
      VACIO.classList.remove('hidden');
      VACIO.classList.add('flex');
    }
  }

  function sinSesion() {
    mostrarMensaje('' +
      '<div class="text-6xl mb-5">🔒</div>' +
      '<h3 style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
      'font-size:22px;color:#1A1A1A">' +
        'Inicia sesión para ver tus aportes' +
      '</h3>' +
      '<p class="text-gray-500 mt-2 max-w-sm" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'El historial de aportes está asociado a tu cuenta.' +
      '</p>' +
      '<a href="/login" class="btn-primary mt-6">Iniciar sesión</a>'
    );
  }

  /* El resumen de mis-aportes ya trae observaciones. Si no
     vienen, se consulta el detalle solo para los rechazos. */
  function completarObservaciones(items) {
    return Promise.all(items.map(function (item) {
      if (texto(item.estado) !== 'rechazado' || texto(item.observaciones)) {
        return Promise.resolve(item);
      }

      return SIMULApi.contenidoDetalle(item.id_contenido)
        .then(function (detalle) {
          return Object.assign({}, item, {
            observaciones: (detalle && detalle.observaciones) || ''
          });
        })
        .catch(function (error) {
          SIMUL.toast(error.message);
          return item;
        });
    }));
  }

  function cargar() {
    if (!Store.getUser()) {
      sinSesion();
      return Promise.resolve();
    }

    return SIMULApi.misAportes()
      .then(function (datos) {
        return completarObservaciones(datos || []);
      })
      .then(function (items) {
        pintar(items);
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        if (LISTADO) LISTADO.classList.add('hidden');
        if (VACIO) {
          VACIO.innerHTML =
            '<p class="text-sm text-gray-400" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              'No se pudieron cargar tus aportes.' +
            '</p>';
          VACIO.classList.remove('hidden');
          VACIO.classList.add('flex');
        }
      });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    /* Delegado: las filas se pintan después de este listener. */
    if (LISTADO) {
      LISTADO.addEventListener('click', function (event) {
        const boton = event.target.closest('[data-observations]');
        if (!boton) return;

        const observaciones = boton.getAttribute('data-observations') || '';
        if (!observaciones) {
          SIMUL.toast('Esta pieza no tiene observaciones registradas', 'info');
          return;
        }

        SIMUL.openModal(
          'Observaciones del revisor',
          modalObservaciones(
            boton.getAttribute('data-title'),
            observaciones
          )
        );
      });
    }

    cargar();
  });

})();
