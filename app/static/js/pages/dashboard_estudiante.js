/* ==========================================================
   DASHBOARD DEL ESTUDIANTE
   Aportes, favoritos, progreso y ranking leídos de la API.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const NIVEL_MAXIMO_PUNTOS = 2000;

  const GRID_APORTES  = $('#dashboard-aportes');
  const BARRA         = $('[data-progress]');
  const CONTADOR_FAVS = $('#favorites-count');
  const NOMBRE_NIVEL  = $('[data-user-level-name]');

  const NIVELES = window.SIMUL_LEVEL_NAMES || {};

  let usuario = null;
  let favoritos = [];
  let aportes = [];

  /* ----------------------------------------------------------
     1. APORTES DEL USUARIO
     ---------------------------------------------------------- */

  function imagenDe(detalle) {
    if (detalle && detalle.imagen) return detalle.imagen;

    return 'data:image/svg+xml;utf8,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">' +
        '<rect width="120" height="120" fill="#E5E7EB"/>' +
        '<text x="60" y="72" text-anchor="middle" ' +
        'font-family="Arial" font-size="48" fill="#9CA3AF">📝</text>' +
      '</svg>'
    );
  }

  function anioDe(item, detalle) {
    if (detalle && detalle.anio) return detalle.anio;
    if (item && item.anio) return item.anio;

    const fecha = String((item && item.fec_crea) || '').slice(0, 4);
    return fecha || '—';
  }

  function esFavorito(id) {
    return favoritos.indexOf(String(id)) !== -1;
  }

  function tarjeta(item, detalle) {
    const id = item.id_contenido;
    const titulo = item.titulo || 'Sin título';
    const categoria = item.categoria || 'Contenido';
    const estado = item.estado || 'pendiente';
    const autor = (detalle && detalle.autor && detalle.autor.nombre) ||
      (usuario && usuario.name) || 'Autor del museo';

    return '' +
      '<article class="simul-card p-5 flex items-center gap-4">' +
        '<img src="' + SIMUL.escapeHtml(imagenDe(detalle)) + '" ' +
        'alt="' + SIMUL.escapeHtml(titulo) + '" ' +
        'loading="lazy" ' +
        'class="w-20 h-20 rounded-xl object-cover shrink-0">' +

        '<div class="flex-1 min-w-0">' +
          '<div class="flex items-center gap-2 mb-1">' +
            '<span class="tag tag-blue">' +
              SIMUL.escapeHtml(categoria) +
            '</span>' +
            '<span class="tag tag-' + SIMUL.escapeHtml(estado) + '">' +
              SIMUL.capitalize(estado) +
            '</span>' +
          '</div>' +

          '<a href="/contenido/' + encodeURIComponent(id) + '" ' +
          'class="block text-sm font-semibold text-gray-800 hover:text-[#C8102E] ' +
          'transition-colors truncate" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(titulo) +
          '</a>' +

          '<p class="text-xs text-gray-400 mt-1" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            SIMUL.escapeHtml(anioDe(item, detalle)) + ' · ' +
            SIMUL.escapeHtml(autor) +
          '</p>' +
        '</div>' +

        '<button type="button" data-favorite="' +
          SIMUL.escapeHtml(id) + '" ' +
        'aria-pressed="' + (esFavorito(id) ? 'true' : 'false') + '" ' +
        'class="w-9 h-9 rounded-full border border-gray-200 text-lg ' +
        'leading-none flex items-center justify-center shrink-0 ' +
        'hover:border-[#C9A84C] transition-colors" ' +
        'aria-label="Guardar en favoritos">' +
          (esFavorito(id) ? '★' : '☆') +
        '</button>' +
      '</article>';
  }

  function pintarVacio(mensaje) {
    GRID_APORTES.innerHTML =
      '<div class="simul-card p-12 text-center">' +
        '<div class="text-4xl mb-3">📝</div>' +
        '<p class="text-sm text-gray-500" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(mensaje) +
        '</p>' +
        '<a href="/proponer-contenido" class="btn-primary mt-5 inline-block">' +
          'Proponer mi primer proyecto' +
        '</a>' +
      '</div>';
  }

  function pintarAportes(pares) {
    if (!GRID_APORTES) return;

    if (pares.length === 0) {
      pintarVacio('Todavía no has aportado contenido al museo.');
      return;
    }

    GRID_APORTES.innerHTML = pares.map(function (par) {
      return tarjeta(par.item, par.detalle);
    }).join('');

    pintarEstrellas();
  }

  function cargarAportes() {
    return SIMULApi.misAportes()
      .then(function (lista) {
        aportes = Array.isArray(lista) ? lista : [];

        return Promise.all(aportes.map(function (item) {
          const numero = SIMULApi.idNumerico(item.id_contenido);
          if (!numero) return Promise.resolve(null);

          return SIMULApi.contenidoDetalle(numero)
            .catch(function () { return null; });
        }));
      })
      .then(function (detalles) {
        const pares = aportes.map(function (item, indice) {
          return { item: item, detalle: detalles[indice] };
        });

        pintarAportes(pares);
      })
      .catch(function (error) {
        aportes = [];
        pintarVacio(
          'No se pudieron cargar tus aportes: ' +
          (error.message || 'error de conexión')
        );
        SIMUL.toast(
          error.message || 'No se pudieron cargar tus aportes',
          'error'
        );
      });
  }

  /* ----------------------------------------------------------
     2. FAVORITOS
     ---------------------------------------------------------- */

  function pintarEstrellas() {
    if (!GRID_APORTES) return;

    SIMUL.$$('[data-favorite]', GRID_APORTES).forEach(function (btn) {
      const activo = esFavorito(btn.getAttribute('data-favorite'));

      btn.textContent = activo ? '★' : '☆';
      btn.style.color = activo ? '#C9A84C' : '';
      btn.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
  }

  function pintarFavoritos() {
    if (CONTADOR_FAVS) {
      CONTADOR_FAVS.textContent = favoritos.length;
    }
    pintarEstrellas();
  }

  function cargarFavoritos() {
    return SIMULApi.favoritos()
      .then(function (lista) {
        favoritos = (lista || []).map(function (item) {
          return String(item.id_contenido || item.id || '');
        }).filter(Boolean);

        pintarFavoritos();
      })
      .catch(function (error) {
        favoritos = [];
        pintarFavoritos();
        SIMUL.toast(
          error.message || 'No se pudieron cargar los favoritos',
          'error'
        );
      });
  }

  /* ----------------------------------------------------------
     3. PROGRESO Y RANKING
     ---------------------------------------------------------- */

  function pintarProgreso(datos) {
    const info = datos && datos.usuario ? datos.usuario : null;
    if (!info) return;

    const puntos = Number(info.puntos_total || 0);
    const nivel = info.nivel || {};

    const puntosEl = $('[data-user-points]');
    if (puntosEl) puntosEl.textContent = SIMUL.formatNumber(puntos);

    if (BARRA) {
      const pct = Math.min((puntos / NIVEL_MAXIMO_PUNTOS) * 100, 100);
      BARRA.style.width = pct.toFixed(1) + '%';
    }

    const nivelEl = $('[data-user-level]');
    if (nivelEl && nivel.numero) nivelEl.textContent = nivel.numero;

    if (NOMBRE_NIVEL) {
      NOMBRE_NIVEL.textContent = nivel.nombre ||
        NIVELES[nivel.numero] ||
        (nivel.numero ? 'Nivel ' + nivel.numero : '—');
    }
  }

  function cargarProgreso() {
    return SIMULApi.miHistorial()
      .then(pintarProgreso)
      .catch(function (error) {
        SIMUL.toast(
          error.message || 'No se pudo cargar tu progreso',
          'error'
        );
      });
  }

  function cargarRanking() {
    return SIMULApi.ranking(100)
      .then(function (filas) {
        const yo = (filas || []).find(function (fila) {
          if (!usuario) return false;

          return String(fila.id_usuario) === String(usuario.id) ||
            fila.nombre === usuario.name;
        });
        if (!yo) return;

        const destino = SIMUL.$('a[href="/ranking"] p');
        if (destino) destino.textContent = '#' + yo.posicion;
      })
      .catch(function (error) {
        SIMUL.toast(error.message || 'No se pudo cargar el ranking', 'error');
      });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    usuario = SIMUL.guardPage('student');
    if (!usuario) return;

    cargarAportes();
    cargarFavoritos();
    cargarProgreso();
    cargarRanking();

    document.addEventListener('simul:favorites-changed', cargarFavoritos);
  });

})();
