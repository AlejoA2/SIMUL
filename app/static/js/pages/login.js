/* ==========================================================
   INICIAR SESIÓN  (RF-USR-01)

   El prototipo dejaba elegir rol y contraseña fija. Aquí se
   mantiene ese comportamiento, pero con las validaciones
   reales del formulario (correo válido, contraseña no vacía).

   Cuando exista el backend, este archivo hace:

       const res = await fetch('/api/auth/login', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ email, password })
       });
       const { access_token, user } = await res.json();

   y guarda `user` con la misma forma que usa Store hoy.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;
  const $$ = (SIMUL.$$ || function (selector) {
    return Array.prototype.slice.call(document.querySelectorAll(selector));
  });

  const EMAILS = window.SIMUL_ROLE_EMAILS || {};
  const PASSWORD_DEMO = window.SIMUL_DEMO_PASSWORD;

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

    /* Verificación de credenciales contra los perfiles de
       demostración. Sin base de datos, la contraseña correcta
       es la misma para los tres roles. */
    const correo = inputEmail.value.trim();
    const clave  = inputPassword.value;

    const correoEsperado = EMAILS[rolSeleccionado];

    if (correo.toLowerCase() !== String(correoEsperado).toLowerCase()) {
      mostrarErrorGeneral(
        'Ese correo no corresponde al rol seleccionado. Revisa el rol o usa el correo de demostración.'
      );
      return;
    }

    if (clave !== PASSWORD_DEMO) {
      mostrarErrorGeneral(
        'Contraseña incorrecta. En modo demostración la contraseña es ' +
        PASSWORD_DEMO + '.'
      );
      return;
    }

    mostrarCarga(true);
    ocultarErrorGeneral();

    /* El retardo imita la latencia de una petición real para
       que la transición de estados sea visible. */
    window.setTimeout(function () {
      Store.login(rolSeleccionado);
      window.location.href = Store.dashboardPath(rolSeleccionado);
    }, 600);
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
