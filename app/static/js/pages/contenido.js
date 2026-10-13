/* ==========================================================
   DETALLE DE CONTENIDO

   Interacciones de la ficha de una pieza del museo:

     · galería de imágenes con puntos de paginación
     · reacción con contador   (tabla REACCION)
     · guardado en favoritos  (tabla FAVORITO)
     · compartir por enlace o portapapeles
     · comentarios y respuestas anidadas (tabla COMENTARIO)
     · línea del tiempo del contenido histórico
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const itemId      = window.SIMUL_ITEM_ID;
  const item        = (window.SIMUL_CONTENT || []).find(function (c) {
                     return String(c.id) === String(itemId);
                   }) || {};
  const tieneLinea  = window.SIMUL_HAS_TIMELINE === true;
  const eventos     = window.SIMUL_TIMELINE || [];

  /* ----------------------------------------------------------
     1. GALERÍA
     ---------------------------------------------------------- */

  const imagen = $('#detail-image');

  function pintarGaleria(indice) {
    if (!imagen) return;

    /* El prototipo simula tres tomas de la misma imagen
       ajustando saturación y brillo. */
    const variantes = [
      '',
      '&sat=-80',
      '&bri=-20'
    ];

    imagen.src = item.image + (variantes[indice] || '');

    $$('.gallery-dot').forEach(function (dot, i) {
      dot.style.background = i === indice ? '#ffffff' : 'rgba(255,255,255,0.5)';
      dot.style.width = i === indice ? '10px' : '10px';
    });
  }

  /* ----------------------------------------------------------
     2. REACCIÓN
     ---------------------------------------------------------- */

  const botonReact   = $('#btn-react');
  const reactEmoji   = $('#react-emoji');
  const reactContador = $('#react-count');

  function pintarReaccion() {
    const actual = Store.getReactions(itemId);

    if (reactEmoji) reactEmoji.textContent = actual.emoji;
    if (reactContador) reactContador.textContent = actual.count;

    if (botonReact) {
      botonReact.style.borderColor = actual.reacted ? '#C8102E' : '';
      botonReact.style.background = actual.reacted ? '#FEF2F2' : '';
    }
  }

  /* ----------------------------------------------------------
     3. FAVORITOS
     ---------------------------------------------------------- */

  const botonFavorito = $('#btn-favorite');
  const iconoFavorito = $('#favorite-icon');
  const etiquetaFavorito = $('#favorite-label');

  function pintarFavorito() {
    if (!botonFavorito) return;

    const activo = Store.isFavorite(itemId);

    iconoFavorito.textContent = activo ? '★' : '☆';
    etiquetaFavorito.textContent = activo ? 'Guardado' : 'Guardar';
    botonFavorito.style.background = activo ? '#FEF2F2' : '';
  }

  /* ----------------------------------------------------------
     4. COMPARTIR
     ---------------------------------------------------------- */

  function compartir() {
    const url = window.location.href;

    /* El portapapeles solo existe en contextos seguros
       (https o localhost). En http plano se usa el diálogo
       clásico de "compartir". */
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(url).then(function () {
        SIMUL.toast('Enlace copiado al portapapeles', 'success');
      }, function () {
        SIMUL.openModal('Compartir', modalCompartir(url));
      });
    } else {
      SIMUL.openModal('Compartir', modalCompartir(url));
    }
  }

  function modalCompartir(url) {
    return '' +
      '<p class="text-sm text-gray-600 mb-4" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Copia este enlace para compartir la pieza con la comunidad.' +
      '</p>' +
      '<input type="text" readonly value="' + SIMUL.escapeHtml(url) + '" ' +
      'onclick="this.select()" ' +
      'class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm ' +
      'mb-4" style="font-family:\'Inter\',sans-serif">' +
      '<div class="flex gap-2">' +
        '<a href="mailto:?subject=' + encodeURIComponent(item.title || 'SIMUL') +
        '&body=' + encodeURIComponent(url) + '" ' +
        'class="btn-primary flex-1 text-center">Enviar por correo</a>' +
      '</div>';
  }

  /* ----------------------------------------------------------
     5. COMENTARIOS
     ---------------------------------------------------------- */

  const lista      = $('#comment-list');
  const contador   = $('#comment-count');
  const formulario = $('#comment-form');
  const area       = $('#comment-input');
  const botonEnviar = $('#comment-submit');

  /* Respuestas a un comentario: se guardan con `parentId`. */
  let respondiendoA = null;

  function pintarComentarios() {
    if (!lista) return;

    const todos = Store.getComments(itemId);

    if (contador) contador.textContent = todos.length;

    if (todos.length === 0) {
      lista.innerHTML =
        '<p class="text-sm text-gray-400 text-center py-8" ' +
        'style="font-family:\'Inter\',sans-serif">' +
        'Todavía no hay comentarios en esta pieza.</p>';
      return;
    }

    lista.innerHTML = todos.map(function (comentario) {
      const esRespuesta = Boolean(comentario.parentId);
      const padre = esRespuesta
        ? todos.find(function (c) { return c.id === comentario.parentId; })
        : null;

      return '' +
        '<div class="simul-card p-4' +
          (esRespuesta ? ' ml-10 border-l-2 border-[#C8102E]' : '') + '">' +

          '<div class="flex items-center justify-between gap-3 mb-1.5">' +
            '<span class="font-bold text-sm text-gray-800" ' +
            'style="font-family:\'Montserrat\',sans-serif">' +
              SIMUL.escapeHtml(comentario.author) +
            '</span>' +
            '<span class="text-xs text-gray-400 shrink-0">' +
              SIMUL.escapeHtml(comentario.time) +
            '</span>' +
          '</div>' +

          (padre
            ? '<p class="text-xs text-gray-400 mb-1.5" ' +
              'style="font-family:\'Inter\',sans-serif">↩ Respondiendo a ' +
              SIMUL.escapeHtml(padre.author) + '</p>'
            : '') +

          '<p class="text-sm text-gray-700 leading-relaxed" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            SIMUL.escapeHtml(comentario.text) +
          '</p>' +

          '<button type="button" data-reply-to="' + comentario.id + '" ' +
          'data-reply-author="' + SIMUL.escapeHtml(comentario.author) + '" ' +
          'class="text-xs font-semibold mt-2 hover:underline" ' +
          'style="font-family:\'Montserrat\',sans-serif;color:#C8102E">' +
            'Responder' +
          '</button>' +

        '</div>';
    }).join('');
  }

  function publicarComentario() {
    const user = Store.getUser();

    if (!user) {
      window.location.href = '/login';
      return;
    }

    if (!area || !area.value.trim()) {
      SIMUL.toast('Escribe un comentario antes de publicar', 'error');
      return;
    }

    Store.addComment(itemId, user.name, area.value.trim(), respondiendoA);

    area.value = '';
    respondiendoA = null;

    pintarComentarios();
    SIMUL.toast('Comentario publicado', 'success');
  }

  /* ----------------------------------------------------------
     6. LÍNEA DEL TIEMPO
     ---------------------------------------------------------- */

  function iniciarLineaDelTiempo() {
    const track = $('#timeline-track');
    if (!track || !tieneLinea) return;

    const tarjetas = $$('.timeline-card', track);
    let indice = 0;

    function activar(nuevo) {
      indice = Math.max(0, Math.min(nuevo, tarjetas.length - 1));

      tarjetas.forEach(function (tarjeta, i) {
        const activa = i === indice;
        tarjeta.style.borderColor = activa ? '#C8102E' : '#E5E7EB';
        tarjeta.style.background = activa ? '#FEF2F2' : '#ffffff';
      });

      tarjetas[indice].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
      });
    }

    tarjetas.forEach(function (tarjeta, i) {
      tarjeta.addEventListener('click', function () { activar(i); });
    });

    /* Desplazamiento con la rueda del ratón. */
    track.addEventListener('wheel', function (event) {
      if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
      event.preventDefault();
      activar(indice + (event.deltaY > 0 ? 1 : -1));
    });

    activar(0);
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    pintarGaleria(0);
    pintarReaccion();
    pintarFavorito();
    pintarComentarios();
    iniciarLineaDelTiempo();

    $$('.gallery-dot').forEach(function (dot) {
      dot.addEventListener('click', function () {
        pintarGaleria(Number(dot.getAttribute('data-gallery-index')));
      });
    });

    if (botonReact) {
      botonReact.addEventListener('click', function () {
        if (!Store.getUser()) {
          window.location.href = '/login';
          return;
        }

        const actual = Store.toggleReaction(itemId);
        pintarReaccion();

        SIMUL.toast(
          actual.reacted ? 'Reacción registrada' : 'Reacción quitada',
          actual.reacted ? 'success' : 'info'
        );
      });
    }

    if (botonFavorito) {
      botonFavorito.addEventListener('click', function () {
        if (!Store.getUser()) {
          window.location.href = '/login';
          return;
        }

        /* Comparte almacén con las tarjetas del listado: el
           botón grande y el pequeño nunca pueden discrepar. */
        const activo = Store.toggleFavorite(itemId);

        pintarFavorito();
        SIMUL.toast(
          activo ? 'Guardado en favoritos' : 'Eliminado de favoritos',
          activo ? 'success' : 'info'
        );
      });
    }

    const botonCompartir = $('#btn-share');
    if (botonCompartir) {
      botonCompartir.addEventListener('click', function () {
        if (!Store.getUser()) {
          window.location.href = '/login';
          return;
        }
        compartir();
      });
    }

    if (botonEnviar) {
      botonEnviar.addEventListener('click', publicarComentario);
    }

    /* Enter + Ctrl/Cmd publica sin salir del área de texto. */
    if (area) {
      area.addEventListener('keydown', function (event) {
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
          publicarComentario();
        }
      });
    }

    /* Respuestas anidadas. */
    if (lista) {
      lista.addEventListener('click', function (event) {
        const boton = event.target.closest('[data-reply-to]');
        if (!boton) return;

        if (!Store.getUser()) {
          window.location.href = '/login';
          return;
        }

        respondiendoA = boton.getAttribute('data-reply-to');

        if (area) {
          area.focus();
          area.placeholder =
            'Respondiendo a ' + boton.getAttribute('data-reply-author') + '...';
        }
      });
    }

    /* Si se borra el texto se cancela la respuesta pendiente. */
    if (area) {
      area.addEventListener('input', function () {
        if (respondiendoA && area.value.trim() === '') {
          respondiendoA = null;
          area.placeholder = 'Comparte tu opinión sobre esta pieza...';
        }
      });
    }
  });

})();
