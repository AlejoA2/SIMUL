/* ==========================================================
   INICIAR SESIÓN  (RF-USR-01)

   El formulario valida correo y contraseña y después llama a
   POST /api/museo/auth/login. El token que devuelve se guarda
   para que las pantallas puedan ejecutar acciones contra la
   API con la sesión del usuario.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;
  const $$ = (SIMUL.$$ || function (selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  });

  const EMAILS = window.SIMUL_ROLE_EMAILS || {};

  /* La API devuelve estudiante/docente/admin; la interfaz usa
     student/teacher/admin desde el corte 2. */
  const ROLES_API = {
    estudiante: 'student',
    docente: 'teacher',
    admin: 'admin',
    egresado: 'student'
  };

  const formulario = $('#login-form');
  const inputEmail = $('#login-email');
  const inputPassword = $('#login-password');
  const botonEnviar = $('#login-submit');
  const errorGeneral = $('#login-error');

  let rolSeleccionado = 'student';

  /* ----------------------------------------------------------
     1. SELECCIÓN DE ROL
     ---------------------------------------------------------- */

  function seleccionarRol(rol) {
    rolSeleccionado = rol;

    $$('.role-option').forEach(function (opcion) {
      SIMUL.markOption(
        opcion,
        opcion.getAttribute('data-role-option') === rol
      );
    });

    /* Cada rol trae su propio correo de demostración. */
    if (inputEmail) inputEmail.value = EMAILS[rol] || '';

    ocultarError(inputEmail);
    ocultarError(inputPassword);
    ocultarErrorGeneral();
  }

  /* ----------------------------------------------------------
     2. VALIDACIÓN
     ---------------------------------------------------------- */

  function esCorreoValido(valor) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor);
  }

  function validar() {
    let valido = true;

    const correo = inputEmail ? inputEmail.value.trim() : '';
    const clave  = inputPassword ? inputPassword.value : '';

    if (!correo) {
      SIMUL.setFieldError(inputEmail, 'El correo electrónico es obligatorio');
      valido = false;
    } else if (!esCorreoValido(correo)) {
      SIMUL.setFieldError(inputEmail, 'Escribe un correo electrónico válido');
      valido = false;
    } else {
      ocultarError(inputEmail);
    }

    if (!clave) {
      SIMUL.setFieldError(inputPassword, 'La contraseña es obligatoria');
      valido = false;
    } else {
      ocultarError(inputPassword);
    }

    return valido;
  }

  function ocultarError(input) {
    if (input) SIMUL.setFieldError(input, '');
  }

  function mostrarErrorGeneral(mensaje) {
    if (!errorGeneral) return;
    errorGeneral.textContent = mensaje;
    errorGeneral.classList.remove('hidden');
  }

  function ocultarErrorGeneral() {
    if (errorGeneral) errorGeneral.classList.add('hidden');
  }

  /* ----------------------------------------------------------
     3. ENVÍO
     ---------------------------------------------------------- */

  function mostrarCarga(activo) {
    if (!botonEnviar) return;
    botonEnviar.disabled = activo;
    botonEnviar.textContent = activo ? 'Verificando…' : 'Iniciar sesión';
  }

  function enviar(evento) {
    evento.preventDefault();

    if (!validar()) return;

    const correo = inputEmail.value.trim();
    const clave  = inputPassword.value;

    mostrarCarga(true);
    ocultarErrorGeneral();

    SIMULApi.login(correo, clave)
      .then(function (datos) {
        const usuario = datos.user || {};
        const rol = ROLES_API[usuario.rol] || rolSeleccionado;

        /* Guardamos el token y reflejamos los datos reales del
           usuario (nombre, puntos y nivel vienen de MySQL). */
        Store.login(rol);
        Store.updateUser({
          id: usuario.id_usuario,
          name: usuario.nombre,
          email: usuario.correo,
          avatar: usuario.foto || (EMAILS[rol] && Store.roleUsers()[rol]
            ? Store.roleUsers()[rol].avatar : ''),
          points: usuario.puntos_total || 0,
          level: (usuario.nivel && usuario.nivel.numero) || 1,
          description: usuario.biografia || '',
          badges: (Store.roleUsers()[rol] || {}).badges || []
        });

        window.location.href = Store.dashboardPath(rol);
      })
      .catch(function (error) {
        mostrarErrorGeneral(error.message || 'No se pudo iniciar sesión');
        mostrarCarga(false);
      });
  }

  /* ----------------------------------------------------------
     4. MOSTRAR / OCULTAR CONTRASEÑA
     ---------------------------------------------------------- */

  function alternarVisibilidad() {
    if (!inputPassword) return;

    const visible = inputPassword.type === 'text';
    inputPassword.type = visible ? 'password' : 'text';

    const boton = $('#toggle-password');
    if (boton) {
      boton.setAttribute(
        'aria-label',
        visible ? 'Mostrar contraseña' : 'Ocultar contraseña'
      );
    }
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  function iniciar() {
    if (formulario) formulario.addEventListener('submit', enviar);

    $$('.role-option').forEach(function (opcion) {
      opcion.addEventListener('click', function () {
        seleccionarRol(opcion.getAttribute('data-role-option'));
      });
    });

    const botonVer = $('#toggle-password');
    if (botonVer) botonVer.addEventListener('click', alternarVisibilidad);

    /* Limpia el error en cuanto el usuario corrige el campo. */
    [inputEmail, inputPassword].forEach(function (input) {
      if (input) input.addEventListener('input', function () {
        ocultarError(input);
        ocultarErrorGeneral();
      });
    });

    /* Si ya hay sesión abierta no tiene sentido volver al login. */
    if (Store.getUser()) {
      window.location.href = Store.dashboardPath(Store.getUser().role);
      return;
    }

    seleccionarRol('student');
    if (inputPassword) inputPassword.focus();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }

})();
