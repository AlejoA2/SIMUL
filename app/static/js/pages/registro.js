/* ==========================================================
   CREAR CUENTA  (RF-USR-01)

   Formulario de registro con validación campo a campo:
   nombre, código según el tipo de cuenta, correo, contraseña
   con requisitos de seguridad, confirmación y aceptación de
   las políticas.

   En la siguiente fase el envío se reemplaza por
   POST /api/auth/register.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const formulario = $('#register-form');
  const panelExito = $('#register-success');

  const campos = {
    nombre:  $('#reg-name'),
    codigo:  $('#reg-code'),
    correo:  $('#reg-email'),
    clave:   $('#reg-password'),
    repetir: $('#reg-confirm'),
    terminos: $('#reg-terms')
  };

  let tipoCuenta = 'student';

  /* ----------------------------------------------------------
     1. TIPO DE CUENTA

     El estudiante se identifica con código de estudiante y
     el docente con código de docente; por eso la etiqueta
     del campo cambia.
     ---------------------------------------------------------- */

  function seleccionarTipo(tipo) {
    tipoCuenta = tipo;

    $$('.role-option').forEach(function (opcion) {
      SIMUL.markOption(
        opcion,
        opcion.getAttribute('data-account-type') === tipo
      );
    });

    const etiqueta = $('#reg-code-label');
    const entrada = campos.codigo;

    if (etiqueta) {
      etiqueta.textContent = tipo === 'teacher'
        ? 'Código de docente *'
        : 'Código de estudiante *';
    }

    if (entrada) {
      entrada.placeholder = tipo === 'teacher'
        ? 'Ej: DOC-0042'
        : 'Ej: 20230145';
    }

    if (entrada) SIMUL.setFieldError(entrada, '');
  }

  /* ----------------------------------------------------------
     2. REQUISITOS DE CONTRASEÑA
     ---------------------------------------------------------- */

  /* Cada regla devuelve si la contraseña la cumple. */
  const REGLAS = [
    { ok: function (v) { return v.length >= 8; },
      texto: '8 caracteres como mínimo' },
    { ok: function (v) { return /[A-Z]/.test(v); },
      texto: 'una letra mayúscula' },
    { ok: function (v) { return /[0-9]/.test(v); },
      texto: 'un número' }
  ];

  function medirFuerza(clave) {
    const barra = $('#password-strength');
    const pista = $('#password-hint');

    if (!barra) return;

    if (!clave) {
      barra.style.width = '0%';
      barra.style.background = '#E5E7EB';
      if (pista) {
        pista.textContent = 'Mínimo 8 caracteres, una mayúscula y un número.';
      }
      return;
    }

    const cumplidas = REGLAS.filter(function (regla) {
      return regla.ok(clave);
    }).length;

    /* 0 reglas → gris, 1 → rojo, 2 → naranja, 3 → verde. */
    const estilos = [
      { width: '0%',   color: '#E5E7EB', texto: 'Contraseña demasiado débil.' },
      { width: '33%',  color: '#DC2626', texto: 'Débil: ' + faltantes(clave) },
      { width: '66%',  color: '#D97706', texto: 'Aceptable: ' + faltantes(clave) },
      { width: '100%', color: '#059669', texto: 'Contraseña segura ✓' }
    ];

    const estado = cumplidas === 0
      ? estilos[0]
      : estilos[cumplidas];

    barra.style.width = estado.width;
    barra.style.background = estado.color;

    if (pista) pista.textContent = estado.texto;
  }

  function faltantes(clave) {
    const pendientes = REGLAS.filter(function (regla) {
      return !regla.ok(clave);
    }).map(function (regla) { return regla.texto; });

    return pendientes.join(' y ');
  }

  /* ----------------------------------------------------------
     3. VALIDACIÓN
     ---------------------------------------------------------- */

  function esCorreoValido(valor) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor);
  }

  function validar() {
    let valido = true;

    /* --- nombre --- */
    if (!campos.nombre.value.trim()) {
      SIMUL.setFieldError(campos.nombre, 'El nombre completo es obligatorio');
      valido = false;
    } else if (campos.nombre.value.trim().length < 3) {
      SIMUL.setFieldError(campos.nombre, 'Escribe tu nombre completo');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.nombre, '');
    }

    /* --- código --- */
    if (!campos.codigo.value.trim()) {
      SIMUL.setFieldError(
        campos.codigo,
        tipoCuenta === 'teacher'
          ? 'El código de docente es obligatorio'
          : 'El código de estudiante es obligatorio'
      );
      valido = false;
    } else {
      SIMUL.setFieldError(campos.codigo, '');
    }

    /* --- correo institucional --- */
    const correo = campos.correo.value.trim();

    if (!correo) {
      SIMUL.setFieldError(campos.correo, 'El correo electrónico es obligatorio');
      valido = false;
    } else if (!esCorreoValido(correo)) {
      SIMUL.setFieldError(campos.correo, 'Escribe un correo electrónico válido');
      valido = false;
    } else if (!/unibre\.edu\.co$/i.test(correo) && !/correo\.unibre\.edu\.co$/i.test(correo)) {
      /* Aviso, no bloqueo: los egresados usan correo personal. */
      SIMUL.setFieldError(
        campos.correo,
        'Usa tu correo institucional @unilibre.edu.co o el @correo.unilibre.edu.co de egresado'
      );
      valido = false;
    } else {
      SIMUL.setFieldError(campos.correo, '');
    }

    /* --- contraseña --- */
    const clave = campos.clave.value;

    if (!clave) {
      SIMUL.setFieldError(campos.clave, 'La contraseña es obligatoria');
      valido = false;
    } else {
      const pendientes = REGLAS.filter(function (regla) {
        return !regla.ok(clave);
      });

      if (pendientes.length) {
        SIMUL.setFieldError(
          campos.clave,
          'La contraseña necesita ' + faltantes(clave)
        );
        valido = false;
      } else {
        SIMUL.setFieldError(campos.clave, '');
      }
    }

    /* --- confirmación --- */
    if (campos.repetir.value !== clave) {
      SIMUL.setFieldError(campos.repetir, 'Las contraseñas no coinciden');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.repetir, '');
    }

    /* --- términos --- */
    if (!campos.terminos.checked) {
      SIMUL.setFieldError(
        campos.terminos,
        'Debes aceptar las políticas para continuar'
      );
      valido = false;
    } else {
      SIMUL.setFieldError(campos.terminos, '');
    }

    return valido;
  }

  /* ----------------------------------------------------------
     4. ENVÍO
     ---------------------------------------------------------- */

  function enviar(evento) {
    evento.preventDefault();

    if (!validar()) {
      /* Lleva el foco al primer campo con problema. */
      const primero = $('.reg-input.border-red-400');
      if (primero) primero.focus();
      return;
    }

    /* Guarda la cuenta recién creada para que el usuario pueda
       entrar sin esperar al backend. */
    Store.register({
      name: campos.nombre.value.trim(),
      email: campos.correo.value.trim(),
      role: tipoCuenta,
      avatar: 'https://ui-avatars.com/api/?name=' +
              encodeURIComponent(campos.nombre.value.trim()) +
              '&background=C8102E&color=fff&size=160',
      points: 0,
      level: 1,
      badges: ['Nuevo miembro'],
      description: 'Cuenta creada en el Museo Digital Interactivo.'
    });

    formulario.classList.add('hidden');
    panelExito.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /* ----------------------------------------------------------
     5. MOSTRAR / OCULTAR CONTRASEÑA
     ---------------------------------------------------------- */

  $$('[data-toggle-password]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      const input = document.getElementById(boton.getAttribute('data-toggle-password'));
      if (!input) return;

      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('DOMContentLoaded', function () {
    if (formulario) formulario.addEventListener('submit', enviar);

    $$('.role-option').forEach(function (opcion) {
      opcion.addEventListener('click', function () {
        seleccionarTipo(opcion.getAttribute('data-account-type'));
      });
    });

    /* La fuerza de la contraseña se recalcula en vivo. */
    if (campos.clave) {
      campos.clave.addEventListener('input', function () {
        medirFuerza(campos.clave.value);

        if (campos.clave.value) SIMUL.setFieldError(campos.clave, '');
      });
    }

    /* Al escribir de nuevo el campo se borra su error. */
    $$('.reg-input').forEach(function (input) {
      input.addEventListener('input', function () {
        SIMUL.setFieldError(input, '');
      });
    });

    if (campos.terminos) {
      campos.terminos.addEventListener('change', function () {
        if (campos.terminos.checked) {
          SIMUL.setFieldError(campos.terminos, '');
        }
      });
    }

    seleccionarTipo('student');
  });

})();
