/* ==========================================================
   DASHBOARD DEL ESTUDIANTE  (RF-DSH-01 / RF-DSH-02)

   Pinta los aportes del usuario y la barra de progreso hacia
   el siguiente nivel. Los valores salen de la sesión guardada
   en localStorage, no del HTML del servidor.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const NIVEL_MAXIMO_PUNTOS = 2000;

  const GRID_APORTES = $('#dashboard-aportes');
  const BARRA       = $('[data-progress]');
  const CONTADOR_FAVS = $('#favorites-count');
  const NOMBRE_NIVEL = $('[data-user-level-name]');

  const NIVELES = window.SIMUL_LEVEL_NAMES || {};

  /* ----------------------------------------------------------
     1. APORTES DEL USUARIO

     Se buscan por nombre dentro del catálogo, igual que hace
     el prototipo. Cuando exista el backend esto se reemplaza
     por GET /api/contenido?autor=<id>.
     ---------------------------------------------------------- */

  function misAportes(user) {
    const contenido = Store.getContent();
    const miNombre = String(user.name).split(' ').slice(-1)[0];

    return contenido.filter(function (item) {
      return String(item.author).indexOf(user.name) !== -1 ||
             String(item.author).indexOf(miNombre) !== -1;
    });
  }

  function pintarAportes(user) {
    if (!GRID_APORTES) return;

    const aportes = misAportes(user);

    if (aportes.length === 0) {
      GRID_APORTES.innerHTML =
        '<div class="simul-card p-12 text-center">' +
          '<div class="text-4xl mb-3">📝</div>' +
          '<p class="text-sm text-gray-500" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            'Todavía no has aportado contenido al museo.' +
          '</p>' +
          '<a href="/proponer-contenido" class="btn-primary mt-5 inline-block">' +
            'Proponer mi primer proyecto' +
          '</a>' +
        '</div>';
      return;
    }

    GRID_APORTES.innerHTML = aportes.map(function (item) {
      return '' +
        '<article class="simul-card p-5 flex items-center gap-4">' +
          '<img src="' + SIMUL.escapeHtml(item.image) + '" ' +
          'alt="' + SIMUL.escapeHtml(item.title) + '" ' +
          'loading="lazy" ' +
          'class="w-20 h-20 rounded-xl object-cover shrink-0">' +

          '<div class="flex-1 min-w-0">' +
            '<div class="flex items-center gap-2 mb-1">' +
              '<span class="tag ' + SIMUL.escapeHtml(item.categoryTag) + '">' +
                SIMUL.escapeHtml(item.category) +
              '</span>' +
              '<span class="tag tag-' + SIMUL.escapeHtml(item.status) + '">' +
                SIMUL.capitalize(item.status) +
              '</span>' +
            '</div>' +

            '<a href="/contenido/' + encodeURIComponent(item.id) + '" ' +
            'class="block text-sm font-semibold text-gray-800 hover:text-[#C8102E] ' +
            'transition-colors truncate" ' +
            'style="font-family:\'Montserrat\',sans-serif">' +
              SIMUL.escapeHtml(item.title) +
            '</a>' +

            '<p class="text-xs text-gray-400 mt-1" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(item.year) +
            '</p>' +
          '</div>' +

          '<button type="button" data-favorite="' +
            SIMUL.escapeHtml(item.id) + '" ' +
          'class="w-9 h-9 rounded-full border border-gray-200 text-lg ' +
          'leading-none flex items-center justify-center shrink-0 ' +
          'hover:border-[#C9A84C] transition-colors" ' +
          'aria-label="Guardar en favoritos">☆</button>' +
        '</article>';
    }).join('');

    /* Los botones recién pintados heredan el estado guardado. */
    (Store.getFavorites() || []).forEach(function (id) {
      SIMUL.$$('[data-favorite="' + id + '"]').forEach(function (btn) {
        btn.textContent = '★';
        btn.style.color = '#C9A84C';
      });
    });
  }

  /* ----------------------------------------------------------
     2. PROGRESO DE NIVEL
     ---------------------------------------------------------- */

  function pintarProgreso(user) {
    if (BARRA) {
      const pct = Math.min((user.points / NIVEL_MAXIMO_PUNTOS) * 100, 100);
      BARRA.style.width = pct.toFixed(1) + '%';
    }

    if (NOMBRE_NIVEL) {
      NOMBRE_NIVEL.textContent = NIVELES[user.level] || ('Nivel ' + user.level);
    }
  }

  /* ----------------------------------------------------------
     3. CONTADOR DE FAVORITOS
     ---------------------------------------------------------- */

  function pintarFavoritos() {
    if (CONTADOR_FAVS) {
      CONTADOR_FAVS.textContent = (Store.getFavorites() || []).length;
    }
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function (event) {
    /* Esta pantalla es privada: sin sesión se va al login. */
    const user = SIMUL.guardPage('student');
    if (!user) return;

    pintarAportes(user);
    pintarProgreso(user);
    pintarFavoritos();

    document.addEventListener('simul:favorites-changed', pintarFavoritos);
  });

})();
