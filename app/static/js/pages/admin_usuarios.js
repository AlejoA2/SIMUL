/* ==========================================================
   GESTIONAR USUARIOS (ADMIN)
   Lista, cambio de rol y activación contra la API REST.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const FILAS    = $('#users-rows');
  const VACIO    = $('#users-empty');
  const BUSCADOR = $('#users-search');
  const CONTADOR = $('#users-active');

  /* seed.py siembra la tabla rol en este orden. */
  const ID_ROL = {
    estudiante: 1,
    docente: 2,
    admin: 3,
    egresado: 4
  };

  let rol = 'Todos';
  let texto = '';
  let usuarios = [];

  /* ----------------------------------------------------------
     1. FILTRADO
     ---------------------------------------------------------- */

  function filtrar() {
    return usuarios.filter(function (user) {
      const coincideRol = rol === 'Todos' || user.rol === rol;

      const coincideTexto = !texto ||
        String(user.nombre || '').toLowerCase().indexOf(
          texto.toLowerCase()
        ) !== -1 ||
        String(user.correo || '').toLowerCase().indexOf(
          texto.toLowerCase()
        ) !== -1;

      return coincideRol && coincideTexto;
    });
  }

  /* ----------------------------------------------------------
     2. PINTADO
     ---------------------------------------------------------- */

  function avatarDe(user) {
    if (user.foto) return user.foto;

    const inicial = String(user.nombre || '?').trim().charAt(0)
      .toUpperCase() || '?';

    return 'data:image/svg+xml;utf8,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">' +
        '<rect width="64" height="64" fill="#E5E7EB"/>' +
        '<text x="32" y="43" text-anchor="middle" ' +
        'font-family="Arial" font-size="28" fill="#6B7280">' +
        inicial +
        '</text>' +
      '</svg>'
    );
  }

  function opcionesDeRol(actual) {
    const nombres = Object.keys(ID_ROL);

    if (actual && nombres.indexOf(actual) === -1) {
      nombres.unshift(actual);
    }

    return nombres.map(function (nombre) {
      return '<option value="' + SIMUL.escapeHtml(nombre) + '"' +
        (nombre === actual ? ' selected' : '') + '>' +
        SIMUL.escapeHtml(SIMUL.capitalize(nombre)) +
        '</option>';
    }).join('');
  }

  function fila(user) {
    const id = user.id_usuario;
    const activo = user.estado === true;
    const fecha = String(user.fecha_registro || '').slice(0, 10) || '—';
    const puntos = SIMUL.formatNumber(user.puntos_total || 0);

    return '' +
      '<div class="grid grid-cols-[1fr_240px_130px_120px_180px] gap-4 ' +
        'px-5 py-4 items-center border-b border-gray-50 hover:bg-gray-50 ' +
        'transition-colors">' +

        '<div class="flex items-center gap-3 min-w-0">' +
          '<img src="' + SIMUL.escapeHtml(avatarDe(user)) + '" ' +
          'alt="' + SIMUL.escapeHtml(user.nombre) + '" ' +
          'loading="lazy" class="w-9 h-9 rounded-full object-cover shrink-0">' +
          '<span class="min-w-0">' +
            '<span class="block text-sm font-semibold text-gray-800 ' +
            'truncate" style="font-family:\'Montserrat\',sans-serif">' +
              SIMUL.escapeHtml(user.nombre) +
            '</span>' +
            '<span class="block text-xs text-gray-400" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              'Desde ' + SIMUL.escapeHtml(fecha) + ' · ' + puntos + ' pts' +
            '</span>' +
          '</span>' +
        '</div>' +

        '<span class="text-sm text-gray-600 truncate" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(user.correo) +
        '</span>' +

        '<span>' +
          '<select data-role-of="' + SIMUL.escapeHtml(id) + '" ' +
          'class="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 ' +
          'bg-white focus:outline-none focus:ring-2 focus:ring-[#C8102E]/20">' +
            opcionesDeRol(user.rol) +
          '</select>' +
        '</span>' +

        '<span class="tag ' + (activo ? 'tag-publicado' : 'tag-rechazado') + '">' +
          (activo ? 'Activo' : 'Inactivo') +
        '</span>' +

        '<div class="flex justify-end">' +
          '<button type="button" data-toggle-active="' +
            SIMUL.escapeHtml(id) + '" ' +
          'class="px-3 py-1.5 rounded-lg text-xs font-semibold ' +
          (activo
            ? 'bg-red-50 text-red-700 hover:bg-red-100'
            : 'bg-green-50 text-green-700 hover:bg-green-100') +
          ' transition-colors" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            (activo ? 'Desactivar' : 'Activar') +
          '</button>' +
        '</div>' +

      '</div>';
  }

  function pintar() {
    const items = filtrar();

    FILAS.innerHTML = items.map(fila).join('');
    FILAS.classList.toggle('hidden', items.length === 0);

    VACIO.classList.toggle('hidden', items.length !== 0);

    const activos = usuarios.filter(function (u) {
      return u.estado === true;
    }).length;

    if (CONTADOR) {
      CONTADOR.textContent = activos + ' de ' + usuarios.length + ' activos';
    }
  }

  /* ----------------------------------------------------------
     3. CARGA Y ACCIONES
     ---------------------------------------------------------- */

  function cargar() {
    return SIMULApi.usuarios()
      .then(function (filas) {
        usuarios = Array.isArray(filas) ? filas : [];
        pintar();
      })
      .catch(function (error) {
        usuarios = [];
        pintar();
        SIMUL.toast(error.message || 'No se pudo cargar los usuarios', 'error');
      });
  }

  function cambiarRol(id, nombreRol) {
    const numero = SIMULApi.idNumerico(id);
    const idRol = ID_ROL[nombreRol];

    if (!numero || !idRol) {
      SIMUL.toast('Rol no reconocido por el catálogo', 'error');
      return;
    }

    SIMULApi.updateUsuario(numero, { id_rol: idRol })
      .then(function () {
        SIMUL.toast('Rol actualizado a ' + nombreRol, 'success');
        return cargar();
      })
      .catch(function (error) {
        SIMUL.toast(error.message || 'No se pudo cambiar el rol', 'error');
      });
  }

  function alternarActivo(id) {
    const user = usuarios.find(function (u) {
      return String(u.id_usuario) === String(id);
    });
    if (!user) return;

    const numero = SIMULApi.idNumerico(id);
    if (!numero) {
      SIMUL.toast('Usuario no válido', 'error');
      return;
    }

    const nuevoEstado = user.estado !== true;

    SIMULApi.updateUsuario(numero, { estado: nuevoEstado })
      .then(function () {
        SIMUL.toast(
          nuevoEstado
            ? 'Cuenta activada'
            : 'Cuenta desactivada. Conserva su historial.',
          nuevoEstado ? 'success' : 'info'
        );
        return cargar();
      })
      .catch(function (error) {
        SIMUL.toast(error.message || 'No se pudo cambiar el estado', 'error');
      });
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

    cargar();

    if (BUSCADOR) {
      BUSCADOR.addEventListener('input', function (event) {
        texto = event.target.value.trim();
        pintar();
      });
    }

    const filtros = $('#users-role-filters');
    if (filtros) {
      filtros.addEventListener('click', function (event) {
        const boton = event.target.closest('[data-role-filter]');
        if (!boton) return;

        marcarFiltro(boton.getAttribute('data-role-filter'));
      });
    }

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
