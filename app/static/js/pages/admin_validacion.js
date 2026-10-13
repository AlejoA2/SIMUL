/* ==========================================================
   BANNERJA DE VALIDACIÓN (ADMIN)  (RF-VAL-01 / RF-VAL-03)

   Cola única para los siete tipos de contenido: un proyecto, un
   premio, una persona para el Hall de la Fama o un aviso
   institucional llegan todos al mismo sitio, que es el punto
   fuerte del modelo de `CONTENIDO` como supertipo.

   Aprobar marca la pieza como publicada y la añade al catálogo.
   Rechazar exige escribir observaciones: son las que el autor
   lee después en "Mis aportes" (RNF-SEG-04).
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

  /* ----------------------------------------------------------
     1. PINTADO DE LA COLA
     ---------------------------------------------------------- */

  function cola() {
    const items = Store.getQueue();

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
    const total = Store.getQueue().length;

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

  function aprobar(id) {
    const item = Store.getQueue().find(function (i) {
      return String(i.id) === String(id);
    });
    if (!item) return;

    /* La pieza entra al catálogo ya como publicada. */
    Store.upsertContent({
      id: 'pub-' + item.id,
      title: item.title,
      year: Number(String(item.date).slice(0, 4)) || new Date().getFullYear(),
      category: item.type,
      categoryTag: 'tag-blue',
      description: item.description,
      image: item.image,
      author: item.author,
      tags: item.tags || [],
      status: 'publicado',
      participants: [item.author],
      technologies: [],
      documents: item.documents || [],
      observations: ''
    });

    Store.dropFromQueue(id);
    pintar();

    SIMUL.toast('Contenido aprobado y publicado', 'success');

    /* La pantalla de publicación resume las acciones que se
       dispararon al aprobar (línea del tiempo, notificaciones,
       índice de búsqueda, puntos al autor). */
    window.setTimeout(function () {
      window.location.href = '/admin/publicacion';
    }, 900);
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
        'Escribe el motivo del rechazo: es obligatorio (RNF-SEG-04).' +
      '</p>' +

      '<div class="flex justify-end gap-3 mt-6">' +
        '<button type="button" onclick="SIMUL.closeModal()" ' +
        'class="btn-secondary">Cancelar</button>' +
        '<button type="button" id="reject-confirm" ' +
        'class="btn-primary">Confirmar rechazo</button>' +
      '</div>';
  }

  function rechazar(id) {
    const item = Store.getQueue().find(function (i) {
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

      if (!motivo) {
        error.classList.remove('hidden');
        return;
      }

      /* El motivo queda en la pieza para que el autor lo lea. */
      Store.upsertContent({
        id: 'rech-' + item.id,
        title: item.title,
        year: Number(String(item.date).slice(0, 4)) || new Date().getFullYear(),
        category: item.type,
        categoryTag: 'tag-blue',
        description: item.description,
        image: item.image,
        author: item.author,
        tags: item.tags || [],
        status: 'rechazado',
        participants: [item.author],
        technologies: [],
        documents: item.documents || [],
        observations: motivo
      });

      Store.dropFromQueue(id);
      SIMUL.closeModal();
      pintar();

      SIMUL.toast('Contenido rechazado con observaciones', 'info');
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

    Store.initQueue(window.SIMUL_QUEUE || []);
    pintar();

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
        aprobar(aprobarBoton.getAttribute('data-approve'));
      } else if (rechazarBoton) {
        rechazar(rechazarBoton.getAttribute('data-reject'));
      } else if (detalleBoton) {
        const item = Store.getQueue().find(function (i) {
          return String(i.id) === detalleBoton.getAttribute('data-preview');
        });

        window.location.href = '/contenido/' +
          encodeURIComponent(item ? item.id : '');
      }
    });
  });

})();
