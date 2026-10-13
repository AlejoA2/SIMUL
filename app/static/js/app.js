/* ==========================================================
   SIMUL - APP
   Comportamiento compartido por todas las páginas.

   Responsabilidades
     1. Guardar las variables que Jinja necesita conocer en el
        servidor (rol, para condicionar bloques del HTML).
     2. Protegerrutas que exigen sesión.
     3. Menú de usuario, notificaciones tipo toast y modales.
     4. Helpers de formato y navegación.

   Sin dependencias: JavaScript plano, sin frameworks.
   ========================================================== */

(function () {
  'use strict';

  /* ----------------------------------------------------------
     1. HELPERS
     ---------------------------------------------------------- */

  const $  = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  /** Escapa texto antes de inyectarlo con innerHTML. */
  function escapeHtml(value) {
    return String(value === null || value === undefined ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatNumber(value) {
    return Number(value || 0).toLocaleString('es-CO');
  }

  /** Capitaliza la primera letra: pendiente → Pendiente. */
  function capitalize(text) {
    const s = String(text || '');
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  /* ----------------------------------------------------------
     2. TOASTS  (tabla NOTIFICACION)
     ---------------------------------------------------------- */

  const TOAST_STYLES = {
    success: { bg: 'bg-emerald-700', icon: '✓' },
    error:   { bg: 'bg-red-700',     icon: '✕' },
    info:    { bg: 'bg-gray-800',    icon: 'ℹ' }
  };

  function toast(message, type) {
    let box = $('#simul-toasts');

    if (!box) {
      box = document.createElement('div');
      box.id = 'simul-toasts';
      box.className =
        'fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none';
      document.body.appendChild(box);
    }

    const style = TOAST_STYLES[type] || TOAST_STYLES.info;

    const node = document.createElement('div');
    node.className =
      'pointer-events-auto flex items-center gap-3 px-5 py-3 rounded-lg ' +
      'shadow-xl text-sm font-medium transition-all duration-300 ' +
      style.bg + ' text-white opacity-100 translate-y-0';
    node.style.fontFamily = 'Montserrat, sans-serif';
    node.style.minWidth = '280px';
    node.innerHTML =
      '<span class="text-base font-bold">' + style.icon + '</span>' +
      '<span>' + escapeHtml(message) + '</span>';

    box.appendChild(node);

    setTimeout(function () {
      node.classList.add('opacity-0', 'translate-y-2');
      setTimeout(function () { node.remove(); }, 300);
    }, 3000);
  }

  /* ----------------------------------------------------------
     3. MODAL
     Un solo contenedor en el DOM reutilizado por todos los
     modales de la aplicación (detalle, rechazo, eliminar…).
     ---------------------------------------------------------- */

  function openModal(title, bodyHtml) {
    closeModal();

    const overlay = document.createElement('div');
    overlay.id = 'simul-modal';
    overlay.className =
      'fixed inset-0 z-50 flex items-center justify-center p-4';
    overlay.style.background = 'rgba(0,0,0,0.5)';

    overlay.innerHTML =
      '<div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg ' +
      'animate-fade-in">' +
        '<div class="flex items-center justify-between px-6 py-4 ' +
             'border-b border-gray-100">' +
          '<h3 style="font-family:\'Montserrat\',sans-serif;' +
                  'font-weight:700;font-size:18px">' +
            escapeHtml(title) +
          '</h3>' +
          '<button data-modal-close ' +
                  'class="p-1.5 rounded-lg hover:bg-gray-100 ' +
                  'transition-colors text-gray-400 hover:text-gray-700">' +
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" ' +
                 'stroke="currentColor" stroke-width="2.5">' +
              '<path d="M18 6 6 18M6 6l12 12"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="px-6 py-5">' + bodyHtml + '</div>' +
      '</div>';

    overlay.addEventListener('click', function (event) {
      /* Clic en el fondo oscuro cierra; clic dentro no. */
      if (event.target === overlay) closeModal();
    });

    document.body.appendChild(overlay);
    return overlay;
  }

  function closeModal() {
    const modal = $('#simul-modal');
    if (modal) modal.remove();
  }

  /* ----------------------------------------------------------
     4. NAVBAR
     El HTML se pinta en Jinja; aquí solo se gestiona el
     estado de sesión y el desplegable del usuario.
     ---------------------------------------------------------- */

  function initNavbar() {
    const toggle = $('#simul-user-toggle');
    const menu   = $('#simul-user-menu');

    if (toggle && menu) {
      toggle.addEventListener('click', function (event) {
        event.stopPropagation();
        menu.classList.toggle('hidden');
      });

      document.addEventListener('click', function () {
        menu.classList.add('hidden');
      });

      menu.addEventListener('click', function (event) {
        event.stopPropagation();
      });
    }

    /* Puede haber más de un botón de cierre de sesión en la
       página (navbar y perfil), así que se delegan todos. */
    $$('[data-action="logout"]').forEach(function (boton) {
      boton.addEventListener('click', function (event) {
        event.preventDefault();
        Store.logout();
        window.location.href = '/';
      });
    });
  }

  /** Rellena los campos con datos de sesión. */
  function paintUser(user) {
    if (!user) return;

    $$('[data-user-name]').forEach(function (el) {
      el.textContent = user.name;
    });

    $$('[data-user-first-name]').forEach(function (el) {
      el.textContent = String(user.name).split(' ')[0];
    });

    $$('[data-user-email]').forEach(function (el) {
      el.textContent = user.email;
    });

    $$('[data-user-avatar]').forEach(function (el) {
      el.src = user.avatar;
      el.alt = user.name;
    });

    $$('[data-user-points]').forEach(function (el) {
      el.textContent = formatNumber(user.points);
    });

    $$('[data-user-level]').forEach(function (el) {
      el.textContent = user.level;
    });

    $$('[data-user-role-label]').forEach(function (el) {
      el.textContent = (window.SIMUL_ROLE_LABELS || {})[user.role] || user.role;
    });

    $$('[data-user-description]').forEach(function (el) {
      el.textContent = user.description || 'Agrega una descripcion sobre ti...';
    });

    /* Los enlaces "Mi Dashboard" dependen del rol activo */
    $$('[data-nav-dashboard]').forEach(function (el) {
      el.href = Store.dashboardPath(user.role);
    });

    /* Lista de insignias del usuario */
    $$('[data-user-badges]').forEach(function (el) {
      el.innerHTML = (user.badges || []).map(function (badge) {
        return '<span class="text-xs px-3 py-1 rounded-full text-xs ' +
               'font-medium bg-gray-100 text-gray-600" ' +
               'style="font-family:\'Inter\',sans-serif">' +
               escapeHtml(badge) + '</span>';
      }).join('');
    });
  }

  /* ----------------------------------------------------------
     5. GUARDA DE RUTAS
     Si no hay sesión, el JS bloquea la vista protegida y
     manda al login (RNF-SEG-02).
     ---------------------------------------------------------- */

  function guardPage(requiredRole) {
    const user = Store.getUser();

    if (!user) {
      window.location.href = '/login';
      return null;
    }

    if (requiredRole && user.role !== requiredRole) {
      window.location.href = Store.dashboardPath(user.role);
      return null;
    }

    paintUser(user);
    return user;
  }

  /** Muestra/oculta bloques según la sesión y el rol activo. */
  function paintAuthBlocks(user) {
    /* Bloques que exigen sesión iniciada */
    $$('[data-requires-auth]').forEach(function (el) {
      if (user) el.removeAttribute('data-auth-hidden');
      else       el.setAttribute('data-auth-hidden', '');
    });

    /* Bloques que solo se ven como visitante (p.ej. "Iniciar sesión") */
    $$('[data-requires-guest]').forEach(function (el) {
      if (user) el.setAttribute('data-auth-hidden', '');
      else       el.removeAttribute('data-auth-hidden');
    });

    /* Bloques de un único rol (menú contextual) */
    $$('[data-role]').forEach(function (el) {
      const roles = el.getAttribute('data-role').split(/\s+/);
      if (user && roles.indexOf(user.role) !== -1) {
        el.removeAttribute('data-auth-hidden');
      } else {
        el.setAttribute('data-auth-hidden', '');
      }
    });
  }

  /* ----------------------------------------------------------
     5. BOTONES DE FAVORITO

     Se delegan en el documento porque las tarjetas se pintan
     en varias pantallas (buscador, favoritos, dashboard) y no
     se pueden enganchar listeners uno por uno.
     ---------------------------------------------------------- */

  function paintFavoriteButton(id) {
    const activo = Store.isFavorite(id);
    $$('[data-favorite="' + id + '"]').forEach(function (btn) {
      btn.textContent = activo ? '★' : '☆';
      btn.style.color = activo ? '#C9A84C' : '';
      btn.setAttribute('aria-pressed', activo ? 'true' : 'false');
    });
  }

  function initFavorites() {
    document.addEventListener('click', function (event) {
      const btn = event.target.closest('[data-favorite]');
      if (!btn) return;

      event.preventDefault();
      event.stopPropagation();

      if (!Store.getUser()) {
        window.location.href = '/login';
        return;
      }

      const id = btn.getAttribute('data-favorite');
      const ahoraEsFavorito = Store.toggleFavorite(id);

      paintFavoriteButton(id);
      toast(
        ahoraEsFavorito ? 'Guardado en favoritos' : 'Eliminado de favoritos',
        ahoraEsFavorito ? 'success' : 'info'
      );

      /* Avisa a la página por si necesita repintarse. */
      document.dispatchEvent(new CustomEvent('simul:favorites-changed', {
        detail: { id: id, active: ahoraEsFavorito }
      }));
    });

    /* Refleja el estado inicial en los botones ya pintados. */
    (Store.getFavorites() || []).forEach(paintFavoriteButton);
  }

  /* ----------------------------------------------------------
     6. ARRANQUE
     ---------------------------------------------------------- */

  function boot() {
    /* Los catálogos simulados se siembran una sola vez. */
    if (window.SIMUL_CONTENT) Store.initContent(window.SIMUL_CONTENT);
    if (window.SIMUL_QUEUE)   Store.initQueue(window.SIMUL_QUEUE);
    if (window.SIMUL_COMMENTS) Store.initComments(window.SIMUL_COMMENTS);
    if (window.SIMUL_REACTIONS) Store.initReactions(window.SIMUL_REACTIONS);
    if (window.SIMUL_USERS)    Store.initUsers(window.SIMUL_USERS);
    Store.initProposals();

    const user = Store.getUser();

    paintAuthBlocks(user);
    if (user) paintUser(user);
    initNavbar();
    initFavorites();

    document.dispatchEvent(new CustomEvent('simul:ready', {
      detail: { user: user }
    }));
  }

  /* ----------------------------------------------------------
     6. TARJETA DE CONTENIDO

     Réplica en JS del partial `partials/_content_card.html`.
     Las páginas que filtran en el navegador (buscador,
     favoritos, dashboard del estudiante) la usan en lugar de
     pedirle al servidor una nueva respuesta.
     ---------------------------------------------------------- */

  function contentCardHtml(item) {
    const tags = (item.tags || []).slice(0, 3).map(function (tag) {
      return '<span class="px-2 py-0.5 rounded-md bg-gray-100 text-gray-600 ' +
             'text-xs">#' + escapeHtml(tag) + '</span>';
    }).join('');

    /* El botón de favorito solo se muestra si hay sesión. */
    const favButton =
      '<button type="button" data-favorite="' + escapeHtml(item.id) + '" ' +
      'class="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 ' +
      'text-lg leading-none flex items-center justify-center shadow-sm ' +
      'hover:bg-white transition-colors" ' +
      'aria-label="Guardar en favoritos">☆</button>';

    return '' +
      '<article class="simul-card overflow-hidden group flex flex-col">' +
        '<div class="relative h-44 overflow-hidden bg-gray-100">' +
          '<img src="' + escapeHtml(item.image) + '" ' +
          'alt="' + escapeHtml(item.title) + '" loading="lazy" ' +
          'class="w-full h-full object-cover transition-transform ' +
          'duration-500 group-hover:scale-105">' +
          '<span class="tag ' + escapeHtml(item.categoryTag || 'tag-blue') +
          ' absolute top-3 left-3">' + escapeHtml(item.category) + '</span>' +
          favButton +
        '</div>' +

        '<div class="p-5 flex-1 flex flex-col">' +
          '<p class="text-xs font-bold mb-2" ' +
          'style="font-family:\'Montserrat\',sans-serif;color:#C8102E">' +
            escapeHtml(item.year) +
            '<span class="text-gray-300 mx-1">·</span>' +
            '<span class="text-gray-500 font-normal" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              escapeHtml(item.author) +
            '</span>' +
          '</p>' +

          '<h3 class="line-clamp-2 mb-2" ' +
          'style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
          'font-size:16px;color:#1A1A1A;line-height:1.35">' +
            escapeHtml(item.title) +
          '</h3>' +

          '<p class="text-gray-500 text-sm line-clamp-2 mb-4" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            escapeHtml(item.description) +
          '</p>' +

          '<div class="flex flex-wrap gap-1.5 mt-auto">' + tags + '</div>' +
        '</div>' +

        '<a href="/contenido/' + encodeURIComponent(item.id) + '" ' +
        'class="block px-5 py-3 border-t border-gray-100 text-center ' +
        'text-sm font-semibold hover:bg-gray-50 transition-colors" ' +
        'style="font-family:\'Montserrat\',sans-serif;color:#C8102E">' +
          'Ver detalle' +
        '</a>' +
      '</article>';
  }

  /* ----------------------------------------------------------
     7. UTILIDADES DE FORMULARIO

     Pintar y limpiar los mensajes de validación que comparten
     todos los formularios del proyecto.
     ---------------------------------------------------------- */

  /** Muestra (o borra) el error asociado a un campo. */
  function setFieldError(input, message) {
    const box = input.closest('div').querySelector('.field-error');
    if (!box) return;

    box.textContent = message || '';
    box.classList.toggle('hidden', !message);

    input.classList.toggle('border-red-400', Boolean(message));
    input.classList.toggle('focus:ring-red-200', Boolean(message));
  }

  /** Resalta visualmente la opción activa de un selector de tarjetas. */
  function markOption(el, active, activeClass) {
    if (!el) return;

    if (active) {
      el.classList.add('border-[#C8102E]', 'bg-red-50');
      el.classList.remove('border-gray-200', 'hover:border-[#C8102E]');
    } else {
      el.classList.remove('border-[#C8102E]', 'bg-red-50');
      el.classList.add('border-gray-200', 'hover:border-[#C8102E]');
    }

    const check = el.querySelector('.role-check');
    if (check) check.classList.toggle('hidden', !active);
  }

  /* ----------------------------------------------------------
     API PÚBLICA
     Se usa desde los scripts de cada página (pages/*.js).
     ---------------------------------------------------------- */

  window.SIMUL = {
    $: $, $$: $$, escapeHtml: escapeHtml,
    formatNumber: formatNumber, capitalize: capitalize,
    toast: toast, openModal: openModal, closeModal: closeModal,
    guardPage: guardPage, paintUser: paintUser, paintAuthBlocks: paintAuthBlocks,
    contentCardHtml: contentCardHtml,
    setFieldError: setFieldError, markOption: markOption
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

})();
