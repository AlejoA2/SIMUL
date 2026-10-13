/* ==========================================================
   GESTIONAR CONTENIDO (ADMIN)

   Tabla completa del catálogo con filtro por estado, búsqueda
   por título y dos acciones: despublicar (baja lógica, la
   pieza conserva su historial) y eliminar (baja física).
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const FILAS    = $('#manage-rows');
  const VACIO    = $('#manage-empty');
  const BUSCADOR = $('#manage-search');
  const CONTADOR = null;

  let estado = 'Todos';
  let texto  = '';

  /* ----------------------------------------------------------
     1. FILTRADO
     ---------------------------------------------------------- */

  function filtrar() {
    return Store.getContent().filter(function (item) {
      const coincideEstado = estado === 'Todos' ||
        item.status === estado.toLowerCase();

      const coincideTexto = !texto ||
        item.title.toLowerCase().indexOf(texto.toLowerCase()) !== -1;

      return coincideEstado && coincideTexto;
    });
  }

  /* ----------------------------------------------------------
     2. PINTADO
     ---------------------------------------------------------- */

  function fila(item) {
    return '' +
      '<div class="grid grid-cols-[1fr_110px_120px_90px_170px] gap-4 ' +
        'px-5 py-4 items-center border-b border-gray-50 hover:bg-gray-50 ' +
        'transition-colors">' +

        '<div class="flex items-center gap-3 min-w-0">' +
          '<img src="' + SIMUL.escapeHtml(item.image) + '" ' +
          'alt="' + SIMUL.escapeHtml(item.title) + '" ' +
          'loading="lazy" class="w-10 h-10 rounded-lg object-cover ' +
          'shrink-0">' +
          '<span class="min-w-0">' +
            '<a href="/contenido/' + encodeURIComponent(item.id) + '" ' +
            'class="block text-sm font-semibold text-gray-800 truncate ' +
            'hover:text-[#C8102E] transition-colors" ' +
            'style="font-family:\'Montserrat\',sans-serif">' +
              SIMUL.escapeHtml(item.title) +
            '</a>' +
            '<span class="block text-xs text-gray-400 truncate" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(item.author) +
            '</span>' +
          '</span>' +
        '</div>' +

        '<span class="tag ' + SIMUL.escapeHtml(item.categoryTag || 'tag-blue') + '">' +
          SIMUL.escapeHtml(item.category) +
        '</span>' +

        '<span class="tag tag-' + SIMUL.escapeHtml(item.status) + '">' +
          SIMUL.capitalize(item.status) +
        '</span>' +

        '<span class="text-sm text-gray-500 text-right" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(item.year) +
        '</span>' +

        '<div class="flex justify-end gap-2">' +
          (item.status === 'publicado'
            ? '<button type="button" data-unpublish="' +
                SIMUL.escapeHtml(item.id) + '" ' +
                'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
                'bg-amber-50 text-amber-700 hover:bg-amber-100 ' +
                'transition-colors" style="font-family:\'Montserrat\',sans-serif">' +
                'Despublicar' +
              '</button>'
            : '') +

          (item.status !== 'publicado'
            ? '<button type="button" data-publish="' +
                SIMUL.escapeHtml(item.id) + '" ' +
                'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
                'bg-green-50 text-green-700 hover:bg-green-100 ' +
                'transition-colors" style="font-family:\'Montserrat\',sans-serif">' +
                'Publicar' +
              '</button>'
            : '') +

          '<button type="button" data-delete="' +
            SIMUL.escapeHtml(item.id) + '" ' +
            'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
            'bg-red-50 text-red-700 hover:bg-red-100 transition-colors" ' +
            'style="font-family:\'Montserrat\',sans-serif">' +
            'Eliminar' +
          '</button>' +
        '</div>' +

      '</div>';
  }

  function pintar() {
    const items = filtrar();

    FILAS.innerHTML = items.map(fila).join('');
    FILAS.classList.toggle('hidden', items.length === 0);

    VACIO.classList.toggle('hidden', items.length !== 0);
  }

  /* ----------------------------------------------------------
     3. ACCIONES
     ---------------------------------------------------------- */

  function despublicar(id) {
    /* Baja lógica: el registro sigue existiendo y conserva su
       historial de validaciones. */
    Store.setContentStatus(id, 'pendiente');
    pintar();
    SIMUL.toast('Contenido despublicado', 'info');
  }

  function publicar(id) {
    Store.setContentStatus(id, 'publicado');
    pintar();
    SIMUL.toast('Contenido publicado', 'success');
  }

  function modalEliminar(item) {
    return '' +
      '<div class="text-center mb-5">' +
        '<div class="text-5xl mb-3">🗑️</div>' +
        '<h3 class="text-lg" ' +
        'style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
        'color:#1A1A1A">' +
          SIMUL.escapeHtml(item.title) +
        '</h3>' +
      '</div>' +

      '<p class="text-sm text-gray-600 leading-relaxed mb-6" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Esta acción borra la pieza del catálogo de forma permanente, ' +
        'junto con sus comentarios, reacciones y favoritos. ' +
        'Si solo quieres retirarla de la vista pública usa ' +
        '<strong>Despublicar</strong> en su lugar.' +
      '</p>' +

      '<div class="flex justify-end gap-3">' +
        '<button type="button" onclick="SIMUL.closeModal()" ' +
        'class="btn-secondary">Cancelar</button>' +
        '<button type="button" id="delete-confirm" class="btn-primary" ' +
        'style="background:#DC2626">Eliminar definitivamente</button>' +
      '</div>';
  }

  function eliminar(id) {
    const item = Store.findContent(id);
    if (!item) return;

    const modal = SIMUL.openModal('Eliminar contenido', modalEliminar(item));

    modal.querySelector('#delete-confirm').addEventListener('click', function () {
      Store.deleteContent(id);
      SIMUL.closeModal();
      pintar();
      SIMUL.toast('Contenido eliminado', 'info');
    });
  }

  /* ----------------------------------------------------------
     4. FILTROS
     ---------------------------------------------------------- */

  function marcarFiltro(valor) {
    estado = valor;

    $$('.manage-filter').forEach(function (boton) {
      const activo = boton.getAttribute('data-manage-filter') === valor;

      boton.classList.toggle('bg-[#C8102E]', activo);
      boton.classList.toggle('text-white', activo);
      boton.classList.toggle('bg-white', !activo);
      boton.classList.toggle('text-gray-600', !activo);
      boton.classList.toggle('border', !activo);
      boton.classList.toggle('border-gray-200', !activo);
    });

    pintar();
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('admin')) return;

    pintar();

    if (BUSCADOR) {
      BUSCADOR.addEventListener('input', function (event) {
        texto = event.target.value.trim();
        pintar();
      });
    }

    $('#manage-filters').addEventListener('click', function (event) {
      const boton = event.target.closest('[data-manage-filter]');
      if (!boton) return;

      marcarFiltro(boton.getAttribute('data-manage-filter'));
    });

    /* Delegación: las filas se repintan tras cada acción. */
    FILAS.addEventListener('click', function (event) {
      const despublicarBoton = event.target.closest('[data-unpublish]');
      const publicarBoton   = event.target.closest('[data-publish]');
      const eliminarBoton   = event.target.closest('[data-delete]');

      if (despublicarBoton) {
        despublicar(despublicarBoton.getAttribute('data-unpublish'));
      } else if (publicarBoton) {
        publicar(publicarBoton.getAttribute('data-publish'));
      } else if (eliminarBoton) {
        eliminar(eliminarBoton.getAttribute('data-delete'));
      }
    });
  });

})();
