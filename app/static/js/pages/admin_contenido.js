/* ==========================================================
   GESTIONAR CONTENIDO (ADMIN)
   Catálogo cargado desde la API. Publicar/despublicar y
   eliminar escriben en MySQL y la lista se vuelve a consultar.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const FILAS    = $('#manage-rows');
  const VACIO    = $('#manage-empty');
  const BUSCADOR = $('#manage-search');

  let estado = 'Todos';
  let texto  = '';
  let items = [];

  /* ----------------------------------------------------------
     1. CARGA
     ---------------------------------------------------------- */

  function cargar() {
    const parametros = { per_page: 100 };

    if (estado !== 'Todos') {
      parametros.estado = estado.toLowerCase();
    }

    return SIMULApi.contenido(parametros)
      .then(function (respuesta) {
        const filas = (respuesta && respuesta.items) || [];

        items = filas.map(SIMULApi.aTarjeta);
        pintar();
      })
      .catch(function (error) {
        items = [];
        pintar();
        SIMUL.toast(
          error.message || 'No se pudo cargar el contenido',
          'error'
        );
      });
  }

  /* ----------------------------------------------------------
     2. FILTRADO Y PINTADO
     ---------------------------------------------------------- */

  function filtrar() {
    return items.filter(function (item) {
      const coincideEstado = estado === 'Todos' ||
        item.status === estado.toLowerCase();

      const coincideTexto = !texto ||
        String(item.title || '').toLowerCase().indexOf(
          texto.toLowerCase()
        ) !== -1;

      return coincideEstado && coincideTexto;
    });
  }

  function imagenDe(item) {
    if (item.image) return item.image;

    return 'data:image/svg+xml;utf8,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">' +
        '<rect width="64" height="64" fill="#E5E7EB"/>' +
        '<text x="32" y="44" text-anchor="middle" ' +
        'font-family="Arial" font-size="30" fill="#9CA3AF">📄</text>' +
      '</svg>'
    );
  }

  function fila(item) {
    const id = item.id;

    return '' +
      '<div class="grid grid-cols-[1fr_110px_120px_90px_170px] gap-4 ' +
        'px-5 py-4 items-center border-b border-gray-50 hover:bg-gray-50 ' +
        'transition-colors">' +

        '<div class="flex items-center gap-3 min-w-0">' +
          '<img src="' + SIMUL.escapeHtml(imagenDe(item)) + '" ' +
          'alt="' + SIMUL.escapeHtml(item.title) + '" ' +
          'loading="lazy" class="w-10 h-10 rounded-lg object-cover ' +
          'shrink-0">' +
          '<span class="min-w-0">' +
            '<a href="/contenido/' + encodeURIComponent(id) + '" ' +
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
          SIMUL.escapeHtml(item.year || '—') +
        '</span>' +

        '<div class="flex justify-end gap-2">' +
          (item.status === 'publicado'
            ? '<button type="button" data-unpublish="' +
                SIMUL.escapeHtml(id) + '" ' +
                'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
                'bg-amber-50 text-amber-700 hover:bg-amber-100 ' +
                'transition-colors" style="font-family:\'Montserrat\',sans-serif">' +
                'Despublicar' +
              '</button>'
            : '') +

          (item.status !== 'publicado'
            ? '<button type="button" data-publish="' +
                SIMUL.escapeHtml(id) + '" ' +
                'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
                'bg-green-50 text-green-700 hover:bg-green-100 ' +
                'transition-colors" style="font-family:\'Montserrat\',sans-serif">' +
                'Publicar' +
              '</button>'
            : '') +

          '<button type="button" data-delete="' +
            SIMUL.escapeHtml(id) + '" ' +
            'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
            'bg-red-50 text-red-700 hover:bg-red-100 transition-colors" ' +
            'style="font-family:\'Montserrat\',sans-serif">' +
            'Eliminar' +
          '</button>' +
        '</div>' +

      '</div>';
  }

  function pintar() {
    const visibles = filtrar();

    FILAS.innerHTML = visibles.map(fila).join('');
    FILAS.classList.toggle('hidden', visibles.length === 0);

    VACIO.classList.toggle('hidden', visibles.length !== 0);
  }

  /* ----------------------------------------------------------
     3. ACCIONES
     ---------------------------------------------------------- */

  function cambiarEstado(id, estadoNuevo, mensaje, tipo) {
    const numero = SIMULApi.idNumerico(id);
    if (!numero) {
      SIMUL.toast('Contenido no válido', 'error');
      return;
    }

    SIMULApi.actualizarContenido(numero, { estado: estadoNuevo })
      .then(function () {
        SIMUL.toast(mensaje, tipo);
        return cargar();
      })
      .catch(function (error) {
        SIMUL.toast(
          error.message || 'No se pudo actualizar el contenido',
          'error'
        );
      });
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
        'junto con sus comentarios, reacciones y evidencias. ' +
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
    const item = items.find(function (i) {
      return String(i.id) === String(id);
    });
    if (!item) return;

    const modal = SIMUL.openModal('Eliminar contenido', modalEliminar(item));
    const confirmar = modal.querySelector('#delete-confirm');
    const numero = SIMULApi.idNumerico(id);

    confirmar.addEventListener('click', function () {
      if (!numero) {
        SIMUL.toast('Contenido no válido', 'error');
        return;
      }

      confirmar.disabled = true;

      SIMULApi.eliminarContenido(numero)
        .then(function () {
          SIMUL.closeModal();
          SIMUL.toast('Contenido eliminado', 'info');
          return cargar();
        })
        .catch(function (error) {
          confirmar.disabled = false;
          SIMUL.toast(
            error.message || 'No se pudo eliminar el contenido',
            'error'
          );
        });
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

    cargar();
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('admin')) return;

    cargar();

    if (BUSCADOR) {
      BUSCADOR.addEventListener('input', function (event) {
        texto = event.target.value.trim();
        pintar();
      });
    }

    const filtros = $('#manage-filters');
    if (filtros) {
      filtros.addEventListener('click', function (event) {
        const boton = event.target.closest('[data-manage-filter]');
        if (!boton) return;

        marcarFiltro(boton.getAttribute('data-manage-filter'));
      });
    }

    FILAS.addEventListener('click', function (event) {
      const despublicarBoton = event.target.closest('[data-unpublish]');
      const publicarBoton   = event.target.closest('[data-publish]');
      const eliminarBoton   = event.target.closest('[data-delete]');

      if (despublicarBoton) {
        cambiarEstado(
          despublicarBoton.getAttribute('data-unpublish'),
          'pendiente',
          'Contenido despublicado: vuelve a la bandeja de validación',
          'info'
        );
      } else if (publicarBoton) {
        cambiarEstado(
          publicarBoton.getAttribute('data-publish'),
          'publicado',
          'Contenido publicado',
          'success'
        );
      } else if (eliminarBoton) {
        eliminar(eliminarBoton.getAttribute('data-delete'));
      }
    });
  });

})();
