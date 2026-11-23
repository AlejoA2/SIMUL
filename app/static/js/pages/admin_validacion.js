/* ==========================================================
   BANDEJA DE VALIDACIÓN (ADMIN)  (RF-VAL-01 / RF-VAL-03)

   La cola se carga desde GET /api/museo/validacion/bandeja.
   Aprobar y rechazar llaman a la API: el cambio se guarda en
   MySQL y la pantalla se vuelve a consultar para refrescarse.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const LISTA    = $('#queue-list');
  const VACIO    = $('#queue-empty');
  const FILTROS  = $('#queue-filters');
  const CONTADOR = $('#queue-counter');

  const COLOR_POR_TIPO = {
    'Proyecto': '#2563EB',
    'Investigacion': '#DC2626',
    'Investigación': '#DC2626',
    'Premio': '#D97706',
    'Evento': '#059669',
    'Hall de la Fama': '#C9A84C'
  };

  let filtro = 'Todos';
  let colaRemota = [];
  let ocupado = false;

  /* ----------------------------------------------------------
     1. PINTADO DE LA COLA

     La fuente es la API. Cada fila que devuelve la consulta se
     convierte al formato que espera la tarjeta de la bandeja.
     ---------------------------------------------------------- */

  /** Fila de la API → tarjeta de la bandeja. */
  function aBandeja(item) {
    return {
      id: item.id_contenido,
      type: item.categoria || item.tipo || 'Contenido',
      date: String(item.fec_crea || '').slice(0, 10),
      title: item.titulo,
      author: item.autor || 'Autor del museo',
      description: item.descripcion || '',
      image: item.imagen || '',
      tags: item.tipo ? [item.tipo] : [],
      documents: []
    };
  }

  function cargarBandeja() {
    return SIMULApi.bandeja()
      .then(function (filas) {
        colaRemota = (filas || []).map(aBandeja);
        pintar();
        return colaRemota;
      })
      .catch(function (error) {
        colaRemota = [];
        pintar();
        SIMUL.toast(error.message || 'No se pudo cargar la bandeja', 'error');
        return colaRemota;
      });
  }

  function todos() {
    return colaRemota;
  }

  function cola() {
    const items = todos();

    return filtro === 'Todos'
      ? items
      : items.filter(function (item) { return item.type === filtro; });
  }

  function tarjeta(item) {
    const color = COLOR_POR_TIPO[item.type] || '#6B7280';

    const documentos = (item.documents || []).map(function (doc) {
      return '' +
        '<li class="flex items-center gap-2 text-sm text-gray-600" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '<span>📄</span>' +
          '<span class="flex-1 min-w-0 truncate">' +
            SIMUL.escapeHtml(doc.name) +
          '</span>' +
          '<span class="text-xs text-gray-400 shrink-0">' +
            SIMUL.escapeHtml(doc.size) +
          '</span>' +
        '</li>';
    }).join('');

    const etiquetas = (item.tags || []).map(function (tag) {
      return '<span class="tag tag-blue">' + SIMUL.escapeHtml(tag) + '</span>';
    }).join('');

    return '' +
      '<article class="simul-card p-5">' +
        '<div class="flex flex-col lg:flex-row gap-5">' +

          '<img src="' + SIMUL.escapeHtml(item.image) + '" ' +
          'alt="' + SIMUL.escapeHtml(item.title) + '" ' +
          'class="w-full lg:w-64 h-44 lg:h-auto rounded-xl object-cover ' +
          'shrink-0" loading="lazy">' +

          '<div class="flex-1 min-w-0">' +

            '<div class="flex items-center gap-2 mb-2 flex-wrap">' +
              '<span class="tag" style="background:' + color + '18;color:' +
                color + '">' + SIMUL.escapeHtml(item.type) + '</span>' +
              '<span class="text-xs text-gray-400">' +
                SIMUL.escapeHtml(item.date) +
              '</span>' +
            '</div>' +

            '<h2 class="mb-1.5" ' +
            'style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
            'font-size:17px;color:#1A1A1A;line-height:1.3">' +
              SIMUL.escapeHtml(item.title) +
            '</h2>' +

            '<p class="text-xs text-gray-500 mb-3" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              '✍️ ' + SIMUL.escapeHtml(item.author) +
            '</p>' +

            '<p class="text-sm text-gray-600 leading-relaxed mb-4" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(item.description) +
            '</p>' +

            (etiquetas ? '<div class="flex flex-wrap gap-1.5 mb-4">' +
              etiquetas + '</div>' : '') +

            (documentos
              ? '<details class="mb-4">' +
                  '<summary class="cursor-pointer text-sm font-semibold ' +
                  'text-gray-600 hover:text-[#C8102E] transition-colors" ' +
                  'style="font-family:\'Montserrat\',sans-serif">' +
                    '📎 Ver ' + (item.documents || []).length +
                    ' evidencia(s)' +
                  '</summary>' +
                  '<ul class="mt-3 flex flex-col gap-2 pl-4">' +
                    documentos +
                  '</ul>' +
                '</details>'
              : '') +

            '<div class="flex flex-wrap gap-3">' +
              '<button type="button" data-approve="' +
                SIMUL.escapeHtml(item.id) + '" class="btn-primary">' +
                'Aprobar y publicar' +
              '</button>' +
              '<button type="button" data-reject="' +
                SIMUL.escapeHtml(item.id) + '" class="btn-secondary">' +
                'Rechazar' +
              '</button>' +
              '<button type="button" data-preview="' +
                SIMUL.escapeHtml(item.id) + '" ' +
                'class="text-sm font-semibold text-gray-500 ' +
                'hover:text-[#C8102E] transition-colors self-center" ' +
                'style="font-family:\'Montserrat\',sans-serif">' +
                'Ver detalle' +
              '</button>' +
            '</div>' +

          '</div>' +
        '</div>' +
      '</article>';
  }

  function pintar() {
    const items = cola();
    const total = todos().length;

    LISTA.innerHTML = items.map(tarjeta).join('');

    LISTA.classList.toggle('hidden', items.length === 0);
    VACIO.classList.toggle('hidden', items.length !== 0);
    VACIO.classList.toggle('flex', items.length === 0);

    CONTADOR.textContent = total === 1
      ? '1 pendiente'
      : total + ' pendientes';
  }

  /* ----------------------------------------------------------
     2. APROBAR  (RF-VAL-04)
     ---------------------------------------------------------- */

  function aprobar(id, boton) {
    if (ocupado) return;
    ocupado = true;
    if (boton) boton.disabled = true;

    function terminar() {
      ocupado = false;
      if (boton) boton.disabled = false;
    }

    /* La API hace todo en una sola operación: publica, guarda
       la decisión, avisa al autor y suma puntos. */
    SIMULApi.aprobar(id)
      .then(function () {
        SIMUL.toast('Contenido aprobado y guardado en la base', 'success');
        return cargarBandeja();
      })
      .then(function () {
        window.setTimeout(function () {
          window.location.href = '/admin/publicacion';
        }, 900);
      })
      .catch(function (error) {
        SIMUL.toast(error.message || 'No se pudo aprobar', 'error');
      })
      .then(terminar, terminar);
  }

  /* ----------------------------------------------------------
     3. RECHAZAR
     ---------------------------------------------------------- */

  function modalRechazo(item) {
    return '' +
      '<p class="text-sm text-gray-600 mb-4" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Rechazando: <strong>' + SIMUL.escapeHtml(item.title) + '</strong>' +
      '</p>' +

      '<label for="reject-reason" class="block mb-2 text-sm ' +
      'font-semibold text-gray-700" ' +
      'style="font-family:\'Montserrat\',sans-serif">' +
        'Observaciones *' +
      '</label>' +

      '<textarea id="reject-reason" rows="5" ' +
      'placeholder="Explica qué debe corregirse. El autor recibirá este ' +
      'texto en su historial de aportes." ' +
      'class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm ' +
      'focus:outline-none focus:ring-2 focus:border-[#C8102E] ' +
      'focus:ring-[#C8102E]/20 resize-none" ' +
      'style="font-family:\'Inter\',sans-serif"></textarea>' +

      '<p id="reject-error" class="hidden text-xs text-red-600 mt-1.5">' +
        'Escribe al menos 5 caracteres: el motivo es obligatorio.' +
      '</p>' +

      '<div class="flex justify-end gap-3 mt-6">' +
        '<button type="button" onclick="SIMUL.closeModal()" ' +
        'class="btn-secondary">Cancelar</button>' +
        '<button type="button" id="reject-confirm" ' +
        'class="btn-primary">Confirmar rechazo</button>' +
      '</div>';
  }

  function rechazar(id) {
    const item = todos().find(function (i) {
      return String(i.id) === String(id);
    });
    if (!item) return;

    const modal = SIMUL.openModal(
      'Rechazar contenido',
      modalRechazo(item)
    );

    const confirmar = modal.querySelector('#reject-confirm');

    confirmar.addEventListener('click', function () {
      const motivo = modal.querySelector('#reject-reason').value.trim();
      const error  = modal.querySelector('#reject-error');

      if (motivo.length < 5) {
        error.classList.remove('hidden');
        return;
      }

      if (ocupado) return;
      ocupado = true;
      confirmar.disabled = true;

      /* El motivo viaja a la API: allí se valida y se guarda en
         la decisión y en el aviso al autor. */
      SIMULApi.rechazar(id, motivo)
        .then(function () {
          SIMUL.closeModal();
          SIMUL.toast('Rechazo guardado en la base', 'info');
          return cargarBandeja();
        })
        .catch(function (fallo) {
          error.textContent = fallo.message || 'No se pudo rechazar';
          error.classList.remove('hidden');
          SIMUL.toast(fallo.message || 'No se pudo rechazar', 'error');
        })
        .then(function () {
          ocupado = false;
          confirmar.disabled = false;
        }, function () {
          ocupado = false;
          confirmar.disabled = false;
        });
    });
  }

  /* ----------------------------------------------------------
     4. FILTROS POR TIPO
     ---------------------------------------------------------- */

  function marcarFiltro(tipo) {
    filtro = tipo;

    $$('.queue-filter').forEach(function (boton) {
      const activo = boton.getAttribute('data-queue-filter') === tipo;

      boton.style.background = activo ? '#C8102E' : '#ffffff';
      boton.style.color = activo ? '#ffffff' : '#4B5563';
      boton.style.borderColor = activo ? '#C8102E' : '#E5E7EB';
    });

    pintar();
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('admin')) return;

    cargarBandeja();

    if (FILTROS) {
      FILTROS.addEventListener('click', function (event) {
        const boton = event.target.closest('[data-queue-filter]');
        if (!boton) return;

        marcarFiltro(boton.getAttribute('data-queue-filter'));
      });
    }

    /* Delegación de las tres acciones de cada tarjeta. */
    LISTA.addEventListener('click', function (event) {
      const aprobarBoton = event.target.closest('[data-approve]');
      const rechazarBoton = event.target.closest('[data-reject]');
      const detalleBoton = event.target.closest('[data-preview]');

      if (aprobarBoton) {
        aprobar(aprobarBoton.getAttribute('data-approve'), aprobarBoton);
      } else if (rechazarBoton) {
        rechazar(rechazarBoton.getAttribute('data-reject'));
      } else if (detalleBoton) {
        const item = todos().find(function (i) {
          return String(i.id) === detalleBoton.getAttribute('data-preview');
        });

        window.location.href = '/contenido/' +
          encodeURIComponent(item ? item.id : '');
      }
    });
  });

})();
