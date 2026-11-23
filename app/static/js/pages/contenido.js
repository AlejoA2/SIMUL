/* ==========================================================
   DETALLE DE CONTENIDO

   La ficha se alimenta de la API: detalle, reacciones,
   comentarios y evidencias. Publicar y reaccionar también
   pasan por SIMULApi. El favorito lo gestiona app.js global
   (delegado en [data-favorite]); aquí solo se refleja su estado.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const itemId = SIMULApi.idNumerico(window.SIMUL_ITEM_ID);
  let item = (window.SIMUL_CONTENT || []).find(function (c) {
    return SIMULApi.idNumerico(c.id) === itemId;
  }) || {};

  const tieneLinea  = window.SIMUL_HAS_TIMELINE === true;
  const eventos     = window.SIMUL_TIMELINE || [];

  let sinContenido  = false;
  let comentarios   = [];
  let mensajeComentarios = 'Todavía no hay comentarios en esta pieza.';
  let reaccion      = { tipo: 'like', total: 0, activo: false };

  function texto(valor) {
    return valor === null || valor === undefined ? '' : String(valor);
  }

  function tarjetaPorTitulo(titulo) {
    return $$('.simul-card.p-6').find(function (card) {
      const h3 = $('h3', card);
      return h3 && h3.textContent.indexOf(titulo) !== -1;
    });
  }

  /* ----------------------------------------------------------
     1. GALERÍA
     ---------------------------------------------------------- */

  const imagen = $('#detail-image');

  function pintarGaleria(indice) {
    if (!imagen || sinContenido || !item.image) return;

    /* Tres variantes de la misma imagen simulan el carrusel. */
    const variantes = ['', '&sat=-80', '&bri=-20'];

    imagen.src = item.image + (variantes[indice] || '');

    $$('.gallery-dot').forEach(function (dot, i) {
      dot.style.background = i === indice ? '#ffffff' : 'rgba(255,255,255,0.5)';
      dot.style.width = '10px';
    });
  }

  /* ----------------------------------------------------------
     2. REACCIÓN
     ---------------------------------------------------------- */

  const botonReact    = $('#btn-react');
  const reactEmoji    = $('#react-emoji');
  const reactContador = $('#react-count');

  function pintarReaccion() {
    if (reactEmoji) reactEmoji.textContent = '👏';
    if (reactContador) reactContador.textContent = SIMUL.formatNumber(reaccion.total);

    if (botonReact) {
      botonReact.style.borderColor = reaccion.activo ? '#C8102E' : '';
      botonReact.style.background = reaccion.activo ? '#FEF2F2' : '';
      botonReact.setAttribute('aria-pressed', reaccion.activo ? 'true' : 'false');
    }
  }

  /* El detalle trae el conteo agregado; la respuesta de
     reaccionar trae además el estado del usuario. */
  function aplicarConteo(datos) {
    if (!datos) return;

    if (datos.tipo_reaccion) reaccion.tipo = datos.tipo_reaccion;

    if (datos.total !== undefined) {
      reaccion.total = Number(datos.total) || 0;
    } else if (datos.conteo !== undefined) {
      reaccion.total = Number(datos.conteo) || 0;
    }

    pintarReaccion();
  }

  function aplicarReaccion(datos) {
    if (!datos) return;

    aplicarConteo(datos);

    if (datos.reaccionado !== undefined) {
      reaccion.activo = Boolean(datos.reaccionado);
    } else if (datos.activo !== undefined) {
      reaccion.activo = Boolean(datos.activo);
    } else if (datos.es_activo !== undefined) {
      reaccion.activo = Boolean(datos.es_activo);
    } else {
      reaccion.activo = !reaccion.activo;
    }

    pintarReaccion();
  }

  /* ----------------------------------------------------------
     3. FAVORITOS (solo estado; la acción vive en app.js)
     ---------------------------------------------------------- */

  const botonFavorito = $('#btn-favorite');

  /* Al añadir data-favorite, el manejador delegado de app.js
     atiende este botón igual que los de las tarjetas. */
  if (botonFavorito && itemId) {
    botonFavorito.setAttribute('data-favorite', String(itemId));
  }

  function pintarFavorito() {
    if (!botonFavorito || !itemId) return;

    const activo = Store.isFavorite(itemId);

    /* app.js pinta el botón como una sola ★; se recupera el
       par de etiquetas sin repetir la acción de guardar. */
    botonFavorito.innerHTML =
      '<span id="favorite-icon">' + (activo ? '★' : '☆') + '</span>' +
      '<span id="favorite-label">' + (activo ? 'Guardado' : 'Guardar') + '</span>';
    botonFavorito.style.background = activo ? '#FEF2F2' : '';
    botonFavorito.setAttribute('aria-pressed', activo ? 'true' : 'false');
  }

  /* ----------------------------------------------------------
     4. COMPARTIR
     ---------------------------------------------------------- */

  function compartir() {
    const url = window.location.href;

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

  const lista       = $('#comment-list');
  const contador    = $('#comment-count');
  const area        = $('#comment-input');
  const botonEnviar = $('#comment-submit');

  let respondiendoA = null;

  function normalizarComentarios(datos) {
    return (datos || []).map(function (c) {
      return {
        id: c.id_comentario || c.id_coment || c.id,
        author: (c.autor && c.autor.nombre) ||
                (typeof c.autor === 'string' ? c.autor : '') ||
                c.nombre || 'Usuario del museo',
        text: c.texto || '',
        time: texto(c.fecha),
        parentId: c.respuesta_a || null
      };
    });
  }

  function pintarComentarios() {
    if (!lista) return;

    if (contador) contador.textContent = comentarios.length;

    if (comentarios.length === 0) {
      lista.innerHTML =
        '<p class="text-sm text-gray-400 text-center py-8" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(mensajeComentarios) +
        '</p>';
      return;
    }

    lista.innerHTML = comentarios.map(function (comentario) {
      const esRespuesta = Boolean(comentario.parentId);
      const padre = esRespuesta
        ? comentarios.find(function (c) { return c.id === comentario.parentId; })
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

          '<button type="button" data-reply-to="' +
            SIMUL.escapeHtml(comentario.id) + '" ' +
          'data-reply-author="' + SIMUL.escapeHtml(comentario.author) + '" ' +
          'class="text-xs font-semibold mt-2 hover:underline" ' +
          'style="font-family:\'Montserrat\',sans-serif;color:#C8102E">' +
            'Responder' +
          '</button>' +

        '</div>';
    }).join('');
  }

  function publicarComentario() {
    if (!Store.getUser()) {
      window.location.href = '/login';
      return;
    }

    if (!area || !area.value.trim()) {
      SIMUL.toast('Escribe un comentario antes de publicar', 'error');
      return;
    }

    const textoComentario = area.value.trim();
    if (botonEnviar) botonEnviar.disabled = true;

    SIMULApi.comentar(itemId, textoComentario, respondiendoA)
      .then(function () {
        area.value = '';
        respondiendoA = null;
        area.placeholder = 'Comparte tu opinión sobre esta pieza...';
        return cargarComentarios();
      })
      .then(function () {
        SIMUL.toast('Comentario publicado', 'success');
        if (botonEnviar) botonEnviar.disabled = false;
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        if (botonEnviar) botonEnviar.disabled = false;
      });
  }

  /* ----------------------------------------------------------
     6. DETALLE Y EVIDENCIAS
     ---------------------------------------------------------- */

  function pintarDetalle(datos) {
    if (!datos) return;

    item = {
      id: datos.id_contenido || itemId,
      title: datos.titulo || item.title,
      image: datos.imagen || item.image,
      year: datos.anio || item.year,
      category: datos.categoria || item.categoria,
      description: datos.descripcion || item.descripcion,
      author: (datos.autor && datos.autor.nombre) || item.author,
      status: datos.estado || item.status
    };

    const titulo = $('h1');
    if (titulo) {
      titulo.textContent = item.title;

      const autor = titulo.nextElementSibling;
      if (autor && autor.tagName === 'P') {
        autor.textContent = '✍️  ' + texto(item.author);
      }

      const etiquetas = titulo.previousElementSibling;
      if (etiquetas) {
        const spans = $$('span', etiquetas);
        if (spans[0]) spans[0].textContent = texto(item.category);
        if (spans[1]) spans[1].textContent = texto(item.year);
        if (spans[2]) {
          spans[2].textContent = SIMUL.capitalize(texto(item.status));
          spans[2].className = 'tag tag-' + texto(item.status);
        }
      }
    }

    const descripcion = $('p.text-lg');
    if (descripcion) descripcion.textContent = texto(item.description);

    const integrantes = datos.integrantes || [];
    const cardParticipantes = tarjetaPorTitulo('Participantes');
    const ulParticipantes = cardParticipantes && $('ul', cardParticipantes);
    if (ulParticipantes && integrantes.length) {
      ulParticipantes.innerHTML = integrantes.map(function (persona) {
        return '<li class="text-sm text-gray-600" ' +
          'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(persona.nombre || '') +
        '</li>';
      }).join('');
    }

    const tecnologias = datos.tecnologias || [];
    const cardTecnologias = tarjetaPorTitulo('Tecnologías');
    const cajaTecnologias = cardTecnologias && $('.flex.flex-wrap', cardTecnologias);
    if (cajaTecnologias && tecnologias.length) {
      cajaTecnologias.innerHTML = tecnologias.map(function (tech) {
        return '<span class="tag tag-blue">' + SIMUL.escapeHtml(tech) + '</span>';
      }).join('');
    }

    pintarGaleria(0);

    const filas = datos.reacciones || [];
    const fila = filas.find(function (r) {
      return r.tipo_reaccion === reaccion.tipo;
    }) || filas[0];
    if (fila) aplicarConteo(fila);
  }

  function pintarEvidencias(datos) {
    const card = tarjetaPorTitulo('Documentos');
    const ul = card && $('ul', card);
    if (!ul) return;

    const evidencias = datos || [];
    if (!evidencias.length) {
      ul.innerHTML = '<li class="text-sm text-gray-400">Sin documentos adjuntos</li>';
      return;
    }

    ul.innerHTML = evidencias.map(function (evidencia) {
      const url = texto(evidencia.url_archivo);
      const nombre = texto(evidencia.alt_text) || url || 'Evidencia';
      const icono = evidencia.tipo === 'video'
        ? '🎬'
        : (evidencia.tipo === 'doc' ? '📄' : '📷');

      return '' +
        '<li class="flex items-start gap-3">' +
          '<span class="text-lg leading-none mt-0.5">' + icono + '</span>' +
          '<span class="flex-1 min-w-0">' +
            '<a href="' + SIMUL.escapeHtml(url) + '" ' +
            'target="_blank" rel="noopener" ' +
            'class="block text-sm text-gray-700 hover:text-[#C8102E] ' +
            'transition-colors truncate" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(nombre) +
            '</a>' +
            '<span class="text-xs text-gray-400">' +
              SIMUL.escapeHtml(evidencia.tipo || '') +
            '</span>' +
          '</span>' +
        '</li>';
    }).join('');
  }

  function cargarDetalle() {
    if (sinContenido) return Promise.resolve();

    return SIMULApi.contenidoDetalle(itemId)
      .then(function (detalle) {
        if (sinContenido) return;
        pintarDetalle(detalle);
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        mostrarVacio('Este contenido no está disponible en la base de datos.');
      });
  }

  function cargarComentarios() {
    if (sinContenido) return Promise.resolve();

    return SIMULApi.comentarios(itemId)
      .then(function (datos) {
        comentarios = normalizarComentarios(datos);
        mensajeComentarios = 'Todavía no hay comentarios en esta pieza.';
        pintarComentarios();
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        if (sinContenido) return;
        mensajeComentarios = 'No se pudieron cargar los comentarios.';
        comentarios = [];
        pintarComentarios();
      });
  }

  function cargarEvidencias() {
    if (sinContenido) return Promise.resolve();

    return SIMULApi.evidencias(itemId)
      .then(function (datos) {
        pintarEvidencias(datos);
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        if (sinContenido) return;
        pintarEvidencias([]);
      });
  }

  function mostrarVacio(mensaje) {
    sinContenido = true;

    if (imagen && imagen.parentElement) {
      imagen.parentElement.innerHTML =
        '<div class="w-full h-full flex items-center justify-center p-8 text-center">' +
          '<p class="text-sm text-gray-400" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            SIMUL.escapeHtml(mensaje) +
          '</p>' +
        '</div>';
    }

    mensajeComentarios = mensaje;
    comentarios = [];
    pintarComentarios();

    reaccion = { tipo: 'like', total: 0, activo: false };
    pintarReaccion();
    pintarEvidencias([]);
  }

  /* ----------------------------------------------------------
     7. LÍNEA DEL TIEMPO
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
    iniciarLineaDelTiempo();

    /* Id no numérico: no hay fila en la base de datos. Mejor
       mostrar un estado vacío que pintar datos del prototipo. */
    if (!itemId) {
      mostrarVacio('Este contenido no está disponible en la base de datos.');
      return;
    }

    pintarGaleria(0);
    pintarReaccion();
    pintarFavorito();
    pintarComentarios();

    cargarDetalle();
    cargarComentarios();
    cargarEvidencias();

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

        SIMULApi.reaccion(itemId, 'like')
          .then(function (datos) {
            aplicarReaccion(datos);
            /* Si el backend no devuelve el total, se recarga el detalle. */
            if (!datos || datos.total === undefined) cargarDetalle();
            SIMUL.toast(
              reaccion.activo ? 'Reacción registrada' : 'Reacción quitada',
              reaccion.activo ? 'success' : 'info'
            );
          })
          .catch(function (error) {
            SIMUL.toast(error.message);
          });
      });
    }

    /* app.js pinta el botón ★ cuando cambia el favorito. */
    document.addEventListener('simul:favorites-changed', pintarFavorito);

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

    if (area) {
      area.addEventListener('keydown', function (event) {
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
          publicarComentario();
        }
      });

      area.addEventListener('input', function () {
        if (respondiendoA && area.value.trim() === '') {
          respondiendoA = null;
          area.placeholder = 'Comparte tu opinión sobre esta pieza...';
        }
      });
    }

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
  });

})();
