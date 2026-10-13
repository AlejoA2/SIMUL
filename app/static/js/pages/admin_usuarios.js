/* ==========================================================
   GESTIONAR USUARIOS (ADMIN)  (RF-USR-05)

   Cambio de rol y activación de cuentas. Desactivar no borra
   nada: el usuario conserva sus aportes, comentarios y puntos,
   pero deja poder entrar al museo.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const FILAS   = $('#users-rows');
  const VACIO   = $('#users-empty');
  const BUSCADOR = $('#users-search');
  const CONTADOR = $('#users-active');

  let rol = 'Todos';
  let texto = '';

  /* ----------------------------------------------------------
     1. FILTRADO
     ---------------------------------------------------------- */

  function filtrar() {
    return Store.getUsers().filter(function (user) {
      const coincideRol = rol === 'Todos' || user.role === rol;

      const coincideTexto = !texto ||
        user.name.toLowerCase().indexOf(texto.toLowerCase()) !== -1 ||
        user.email.toLowerCase().indexOf(texto.toLowerCase()) !== -1;

      return coincideRol && coincideTexto;
    });
  }

  /* ----------------------------------------------------------
     2. PINTADO
     ---------------------------------------------------------- */

  function fila(user) {
    const color = window.SIMUL_ROLE_COLORS[user.role] || 'tag-blue';
    const roles = window.SIMUL_USER_ROLES || [];

    const opciones = roles.map(function (nombre) {
      return '<option value="' + SIMUL.escapeHtml(nombre) + '"' +
        (nombre === user.role ? ' selected' : '') + '>' +
        SIMUL.escapeHtml(nombre) +
        '</option>';
    }).join('');

    return '' +
      '<div class="grid grid-cols-[1fr_240px_130px_120px_180px] gap-4 ' +
        'px-5 py-4 items-center border-b border-gray-50 hover:bg-gray-50 ' +
        'transition-colors">' +

        '<div class="flex items-center gap-3 min-w-0">' +
          '<img src="' + SIMUL.escapeHtml(user.avatar) + '" ' +
          'alt="' + SIMUL.escapeHtml(user.name) + '" ' +
          'loading="lazy" class="w-9 h-9 rounded-full object-cover shrink-0">' +
          '<span class="min-w-0">' +
            '<span class="block text-sm font-semibold text-gray-800 ' +
            'truncate" style="font-family:\'Montserrat\',sans-serif">' +
              SIMUL.escapeHtml(user.name) +
            '</span>' +
            '<span class="block text-xs text-gray-400" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              'Desde ' + SIMUL.escapeHtml(user.joined) +
            '</span>' +
          '</span>' +
        '</div>' +

        '<span class="text-sm text-gray-600 truncate" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(user.email) +
        '</span>' +

        '<span>' +
          '<select data-role-of="' + SIMUL.escapeHtml(user.id) + '" ' +
          'class="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 ' +
          'bg-white focus:outline-none focus:ring-2 focus:ring-[#C8102E]/20">' +
            opciones +
          '</select>' +
        '</span>' +

        '<span class="tag ' + (user.active ? 'tag-publicado' : 'tag-rechazado') + '">' +
          (user.active ? 'Activo' : 'Inactivo') +
        '</span>' +

        '<div class="flex justify-end">' +
          '<button type="button" data-toggle-active="' +
            SIMUL.escapeHtml(user.id) + '" ' +
          'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
          (user.active
            ? 'bg-red-50 text-red-700 hover:bg-red-100'
            : 'bg-green-50 text-green-700 hover:bg-green-100') +
          ' transition-colors" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            (user.active ? 'Desactivar' : 'Activar') +
          '</button>' +
        '</div>' +

      '</div>';
  }

  function pintar() {
    const items = filtrar();

    FILAS.innerHTML = items.map(fila).join('');
    FILAS.classList.toggle('hidden', items.length === 0);

    VACIO.classList.toggle('hidden', items.length !== 0);

    const activos = Store.getUsers().filter(function (u) {
      return u.active;
    }).length;

    const total = Store.getUsers().length;

    CONTADOR.textContent = activos + ' de ' + total + ' activos';
  }

  /* ----------------------------------------------------------
     3. ACCIONES
     ---------------------------------------------------------- */

  function cambiarRol(id, nuevoRol) {
    Store.setUserRole(id, nuevoRol);

    /* Aviso al titular: cambiar de rol cambia lo que ve. */
    const user = Store.getUser();
    if (user && String(user.id) === String(id)) {
      Store.updateUser({ role: nuevoRol.toLowerCase() });
      SIMUL.paintUser(Store.getUser());
    }

    pintar();
    SIMUL.toast('Rol actualizado a ' + nuevoRol, 'success');
  }

  function alternarActivo(id) {
    const user = Store.getUsers().find(function (u) {
      return String(u.id) === String(id);
    });
    if (!user) return;

    Store.toggleUserActive(id);
    pintar();

    SIMUL.toast(
      user.active
        ? 'Cuenta desactivada. Conserva su historial.'
        : 'Cuenta activada',
      user.active ? 'info' : 'success'
    );
  }

  /* ----------------------------------------------------------
     4. FILTROS
     ---------------------------------------------------------- */

  function marcarFiltro(valor) {
    rol = valor;

    $$('.role-filter').forEach(function (boton) {
      const activo = boton.getAttribute('data-role-filter') === valor;

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

    Store.initUsers(window.SIMUL_USERS || []);
    pintar();

    if (BUSCADOR) {
      BUSCADOR.addEventListener('input', function (event) {
        texto = event.target.value.trim();
        pintar();
      });
    }

    $('#users-role-filters').addEventListener('click', function (event) {
      const boton = event.target.closest('[data-role-filter]');
      if (!boton) return;

      marcarFiltro(boton.getAttribute('data-role-filter'));
    });

    FILAS.addEventListener('change', function (event) {
      const select = event.target.closest('[data-role-of]');
      if (!select) return;

      cambiarRol(select.getAttribute('data-role-of'), select.value);
    });

    FILAS.addEventListener('click', function (event) {
      const boton = event.target.closest('[data-toggle-active]');
      if (!boton) return;

      alternarActivo(boton.getAttribute('data-toggle-active'));
    });
  });

})();
