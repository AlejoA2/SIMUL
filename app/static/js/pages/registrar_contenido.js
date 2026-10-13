/* ==========================================================
   REGISTRAR CONTENIDO (DOCENTE)  (RF-COM-02)

   El formulario cambia por completo según el tipo de pieza
   que elija el docente: un premio pide entidad otorgante,
   una persona para el Hall de la Fama pide cargo y logros, y
   así sucesivamente.

   Las definiciones de campo llegan desde Python en
   `simul_data.TEACHER_FORMS`; aquí solo se pintan.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const FORMULARIOS = window.SIMUL_TEACHER_FORMS || {};

  const SELECTOR   = $('#content-type-picker');
  const FORMULARIO = $('#register-content-form');
  const CAMPOS     = $('#dynamic-fields');
  const TITULO     = $('#form-title');
  const ERROR      = $('#content-error');
  const ENVIAR     = $('#content-submit');

  const ETIQUETAS = {
    historia: 'Acontecimiento histórico',
    premio: 'Premio',
    proyecto: 'Proyecto',
    evento: 'Evento',
    investigacion: 'Avance de investigación',
    hall: 'Persona para el Hall de la Fama'
  };

  let tipoSeleccionado = null;

  /* ----------------------------------------------------------
     1. CONSTRUCCIÓN DEL FORMULARIO
     ---------------------------------------------------------- */

  /** Elige la plantilla de campos según el tipo elegido. */
  function plantillaDe(tipo) {
    return FORMULARIOS[tipo] || FORMULARIOS.default || [];
  }

  /**
   * Identificador estable a partir de la etiqueta del campo.
   * "Año de ingreso al Hall *" → "ano-de-ingreso-al-hall"
   */
  function clave(texto) {
    return texto
      .toLowerCase()
      /* Separa los diacríticos: A~ + combining tilde → a */
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      /* Todo lo que no sea alfanumérico pasa a guion */
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  }

  function campo(definicion, indice) {
    const id = 'campo-' + indice + '-' + clave(definicion.label);
    const obligatorio = definicion.label.indexOf('*') !== -1;

    if (definicion.type === 'textarea') {
      return '' +
        '<div>' +
          '<label for="' + id + '" class="block mb-2 text-sm font-semibold ' +
          'text-gray-700" style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(definicion.label) +
          '</label>' +
          '<textarea id="' + id + '" data-campo="' + indice + '" ' +
            'placeholder="' + SIMUL.escapeHtml(definicion.placeholder || '') + '" ' +
            'rows="4" class="dyn-input w-full px-4 py-3 border ' +
            'border-gray-200 rounded-xl text-sm focus:outline-none ' +
            'focus:ring-2 focus:border-[#C8102E] focus:ring-[#C8102E]/20 ' +
            'resize-none" style="font-family:\'Inter\',sans-serif"></textarea>' +
          '<p class="field-error hidden text-xs text-red-600 mt-1.5"></p>' +
        '</div>';
    }

    return '' +
      '<div>' +
        '<label for="' + id + '" class="block mb-2 text-sm font-semibold ' +
        'text-gray-700" style="font-family:\'Montserrat\',sans-serif">' +
          SIMUL.escapeHtml(definicion.label) +
        '</label>' +
        '<input type="' + (definicion.type || 'text') + '" ' +
          'id="' + id + '" data-campo="' + indice + '" ' +
          'placeholder="' + SIMUL.escapeHtml(definicion.placeholder || '') + '"' +
          (definicion.type === 'number' ? ' min="1989" max="2030"' : '') +
          ' class="dyn-input w-full px-4 py-3 border border-gray-200 ' +
          'rounded-xl text-sm focus:outline-none focus:ring-2 ' +
          'focus:border-[#C8102E] focus:ring-[#C8102E]/20" ' +
          'style="font-family:\'Inter\',sans-serif">' +
        '<p class="field-error hidden text-xs text-red-600 mt-1.5"></p>' +
      '</div>';
  }

  function pintarCampos(tipo) {
    const plantilla = plantillaDe(tipo);

    CAMPOS.innerHTML = plantilla.map(campo).join('');

    TITULO.textContent =
      ETIQUETAS[tipo] ? 'Datos del ' + ETIQUETAS[tipo].toLowerCase()
                      : 'Completa la información';

    /* Limpia el error anterior al cambiar de tipo. */
    ERROR.classList.add('hidden');
  }

  /* ----------------------------------------------------------
     2. SELECCIÓN DE TIPO
     ---------------------------------------------------------- */

  function seleccionar(tipo) {
    tipoSeleccionado = tipo;

    $$('.type-option').forEach(function (opcion) {
      const activa = opcion.getAttribute('data-content-type') === tipo;

      opcion.classList.toggle('border-[#C8102E]', activa);
      opcion.classList.toggle('bg-red-50', activa);
      opcion.classList.toggle('border-gray-200', !activa);
    });

    FORMULARIO.classList.remove('hidden');
    pintarCampos(tipo);

    FORMULARIO.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ----------------------------------------------------------
     3. VALIDACIÓN
     ---------------------------------------------------------- */

  function validar() {
    const plantilla = plantillaDe(tipoSeleccionado);
    let valido = true;

    plantilla.forEach(function (definicion, indice) {
      const input = $('[data-campo="' + indice + '"]');
      if (!input) return;

      /* Solo son obligatorios los campos marcados con *. */
      const obligatorio = definicion.label.indexOf('*') !== -1;

      if (obligatorio && !input.value.trim()) {
        SIMUL.setFieldError(input, 'Este campo es obligatorio');
        valido = false;
      } else {
        SIMUL.setFieldError(input, '');
      }
    });

    if (!valido && ERROR) {
      ERROR.textContent =
        'Completa los campos obligatorios antes de registrar el contenido.';
      ERROR.classList.remove('hidden');
    }

    return valido;
  }

  /* ----------------------------------------------------------
     4. ENVÍO
     ---------------------------------------------------------- */

  function enviar(evento) {
    evento.preventDefault();

    if (!tipoSeleccionado) {
      if (ERROR) {
        ERROR.textContent = 'Selecciona primero qué tipo de contenido vas a registrar.';
        ERROR.classList.remove('hidden');
      }
      return;
    }

    if (!validar()) return;

    ENVIAR.disabled = true;
    ENVIAR.textContent = 'Registrando…';

    /* Recolecta lo escrito para guardarlo en el catálogo local. */
    const plantilla = plantillaDe(tipoSeleccionado);
    const datos = {};

    plantilla.forEach(function (definicion, indice) {
      const input = $('[data-campo="' + indice + '"]');
      datos[clave(definicion.label)] = input ? input.value.trim() : '';
    });

    const user = Store.getUser();

    /* El contenido nace pendiente: nadie publica sin pasar
       por la bandeja de validación del administrador. */
    Store.upsertContent({
      id: 'n' + Date.now(),
      title: datos['nombre-del-premio'] ||
             datos['nombre-completo'] ||
             datos['nombre-del-proyecto'] ||
             datos['titulo'] ||
             'Contenido sin título',
      year: Number(datos['ano'] || datos['ano-de-ingreso-al-hall']) || new Date().getFullYear(),
      category: ETIQUETAS[tipoSeleccionado] || 'Proyecto',
      categoryTag: 'tag-blue',
      description: datos['descripcion'] ||
                   datos['principales-logros'] || '',
      image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=500&fit=crop&auto=format',
      author: user ? user.name : 'Docente',
      tags: [],
      status: 'pendiente',
      participants: datos['integrantes'] ? [datos['integrantes']] : [],
      technologies: datos['tecnologias-utilizadas']
        ? datos['tecnologias-utilizadas'].split(',').map(function (t) {
            return t.trim();
          })
        : [],
      documents: [],
      observations: ''
    });

    window.setTimeout(function () {
      SIMUL.toast(
        'Contenido registrado. Queda pendiente de validación.',
        'success'
      );
      window.location.href = '/dashboard/docente';
    }, 700);
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    const user = SIMUL.guardPage('teacher');
    if (!user) return;

    $$('.type-option').forEach(function (opcion) {
      opcion.addEventListener('click', function () {
        seleccionar(opcion.getAttribute('data-content-type'));
      });
    });

    if (FORMULARIO) FORMULARIO.addEventListener('submit', enviar);

    /* Al escribir se borra el error del campo. */
    CAMPOS.addEventListener('input', function (event) {
      if (event.target.classList.contains('dyn-input')) {
        SIMUL.setFieldError(event.target, '');
      }
    });
  });

})();
