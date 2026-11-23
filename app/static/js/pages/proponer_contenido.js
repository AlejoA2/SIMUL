/* ==========================================================
   PROPUESTA DE PROYECTO  (RF-PRY-01)

   Formulario largo con validación en el navegador, selección
   múltiple de tecnologías y vista previa del docente asesor.

   Al enviar, SIMULApi.crearContenido guarda un proyecto en la
   API. Los archivos elegidos se listan, pero no se suben: el
   modulo de evidencias no recibe archivos desde esta vista.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const formulario   = $('#proposal-form');
  const panelExito   = $('#proposal-success');
  const botonEnviar  = $('#proposal-submit');
  const errorGeneral = $('#proposal-error');
  const areaDescripcion = $('#prop-description');
  const contador     = $('#description-counter');

  const LIMITE_DESCRIPCION = 600;
  const TEXTO_ENVIAR = botonEnviar ? botonEnviar.textContent : 'Enviar propuesta';
  const IMAGEN_POR_DEFECTO =
    'https://images.unsplash.com/photo-1518770660439-4636190af475' +
    '?w=800&h=500&fit=crop&auto=format';

  const campos = {
    nombre:      $('#prop-name'),
    anio:        $('#prop-year'),
    categoria:   $('#prop-category'),
    integrantes: $('#prop-members'),
    asesor:      $('#prop-teacher'),
    descripcion: areaDescripcion,
    resultados:  $('#prop-results')
  };

  /* Archivos seleccionados en el navegador (no se transmiten). */
  let archivos = [];

  /* ----------------------------------------------------------
     1. DOCENTE ASESOR
     ---------------------------------------------------------- */

  function pintarAsesor() {
    const panel   = $('#teacher-preview');
    const avatar  = $('#teacher-avatar');
    const nombre  = $('#teacher-name');
    const opcion  = campos.asesor.selectedOptions[0];

    if (!panel) return;

    if (!opcion || !opcion.value) {
      panel.classList.add('hidden');
      return;
    }

    avatar.src = opcion.getAttribute('data-avatar');
    nombre.textContent = opcion.getAttribute('data-name');
    panel.classList.remove('hidden');
  }

  /* ----------------------------------------------------------
     2. TECNOLOGÍAS
     ---------------------------------------------------------- */

  function tecnologíasElegidas() {
    return $$('.tech-option input:checked').map(function (input) {
      return input.value;
    });
  }

  function pintarTecnologias() {
    $$('.tech-option').forEach(function (etiqueta) {
      const marcado = etiqueta.querySelector('input').checked;

      etiqueta.className = etiqueta.className
        .replace(/bg-\[#C8102E\] ?/g, '')
        .replace(/text-white ?/g, '')
        .replace(/border-\[#C8102E\] ?/g, '');

      etiqueta.className = marcado
        ? 'tech-option cursor-pointer px-3.5 py-2 rounded-lg border ' +
          'border-[#C8102E] bg-[#C8102E] text-white text-sm select-none ' +
          'transition-colors'
        : 'tech-option cursor-pointer px-3.5 py-2 rounded-lg border ' +
          'border-gray-200 text-sm text-gray-600 hover:border-[#C8102E] ' +
          'transition-colors select-none';
    });
  }

  /* ----------------------------------------------------------
     3. CONTADOR DE CARACTERES
     ---------------------------------------------------------- */

  if (areaDescripcion && contador) {
    areaDescripcion.maxLength = LIMITE_DESCRIPCION;

    areaDescripcion.addEventListener('input', function () {
      contador.textContent = areaDescripcion.value.length + ' / ' + LIMITE_DESCRIPCION;
    });
  }

  /* ----------------------------------------------------------
     4. ARCHIVOS
     ---------------------------------------------------------- */

  const zona  = $('#dropzone');
  const input = $('#proposal-files');
  const lista = $('#proposal-files-list');

  function formato(bytes) {
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  }

  function pintarArchivos() {
    if (!lista) return;

    if (!archivos.length) {
      lista.innerHTML = '';
      return;
    }

    const aviso =
      '<li class="text-xs text-gray-400" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Los archivos seleccionados no se suben: la API guarda solo ' +
        'los datos de la propuesta.' +
      '</li>';

    lista.innerHTML = aviso + archivos.map(function (archivo) {
      return '' +
        '<li class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 ' +
        'border border-gray-100">' +
          '<span class="text-xl">📄</span>' +
          '<span class="flex-1 min-w-0">' +
            '<span class="block text-sm text-gray-700 truncate" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(archivo.nombre) +
            '</span>' +
          '</span>' +
          '<span class="text-xs text-gray-400 shrink-0">' +
            SIMUL.escapeHtml(archivo.tamano) +
          '</span>' +
          '<span class="text-xs font-semibold shrink-0 w-20 text-right" ' +
          'style="font-family:\'Montserrat\',sans-serif;color:#6B7280">' +
            'Sin subir' +
          '</span>' +
          '<button type="button" data-remove-file="' + archivo.id + '" ' +
          'class="text-gray-400 hover:text-red-600 transition-colors ' +
          'shrink-0" aria-label="Quitar archivo">✕</button>' +
        '</li>';
    }).join('');
  }

  function agregarArchivos(listaRecibida) {
    Array.prototype.forEach.call(listaRecibida, function (file) {
      archivos.push({
        id: 'f' + Date.now() + Math.random().toString(36).slice(2, 7),
        nombre: file.name,
        tamano: formato(file.size)
      });
    });

    pintarArchivos();
  }

  if (zona && input) {
    input.addEventListener('change', function () {
      if (input.files && input.files.length) agregarArchivos(input.files);
    });

    /* Arrastrar y soltar. */
    ['dragenter', 'dragover'].forEach(function (evento) {
      zona.addEventListener(evento, function (e) {
        e.preventDefault();
        zona.classList.add('border-[#C8102E]', 'bg-red-50/30');
      });
    });

    ['dragleave', 'drop'].forEach(function (evento) {
      zona.addEventListener(evento, function (e) {
        e.preventDefault();
        zona.classList.remove('border-[#C8102E]', 'bg-red-50/30');
      });
    });

    zona.addEventListener('drop', function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        agregarArchivos(e.dataTransfer.files);
      }
    });
  }

  if (lista) {
    lista.addEventListener('click', function (event) {
      const boton = event.target.closest('[data-remove-file]');
      if (!boton) return;

      const id = boton.getAttribute('data-remove-file');
      archivos = archivos.filter(function (a) { return a.id !== id; });
      pintarArchivos();
    });
  }

  /* ----------------------------------------------------------
     5. VALIDACIÓN
     ---------------------------------------------------------- */

  function validar() {
    let valido = true;

    if (!campos.nombre.value.trim()) {
      SIMUL.setFieldError(campos.nombre, 'El nombre del proyecto es obligatorio');
      valido = false;
    } else if (campos.nombre.value.trim().length < 5) {
      SIMUL.setFieldError(campos.nombre, 'Describe el proyecto con más detalle');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.nombre, '');
    }

    if (!campos.anio.value) {
      SIMUL.setFieldError(campos.anio, 'Indica el año del proyecto');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.anio, '');
    }

    if (!campos.categoria.value) {
      SIMUL.setFieldError(campos.categoria, 'Selecciona el tipo de proyecto');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.categoria, '');
    }

    if (!campos.integrantes.value.trim()) {
      SIMUL.setFieldError(campos.integrantes, 'Indica al menos un integrante');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.integrantes, '');
    }

    if (!campos.asesor.value) {
      SIMUL.setFieldError(campos.asesor, 'Selecciona el docente asesor');
      valido = false;
    } else {
      SIMUL.setFieldError(campos.asesor, '');
    }

    const descripcion = campos.descripcion.value.trim();

    if (!descripcion) {
      SIMUL.setFieldError(campos.descripcion, 'La descripción es obligatoria');
      valido = false;
    } else if (descripcion.length < 30) {
      SIMUL.setFieldError(
        campos.descripcion,
        'La descripción debe tener al menos 30 caracteres'
      );
      valido = false;
    } else {
      SIMUL.setFieldError(campos.descripcion, '');
    }

    if (!campos.resultados.value.trim()) {
      SIMUL.setFieldError(
        campos.resultados,
        'Indica al menos un resultado obtenido'
      );
      valido = false;
    } else {
      SIMUL.setFieldError(campos.resultados, '');
    }

    return valido;
  }

  /* ----------------------------------------------------------
     6. ENVÍO
     ---------------------------------------------------------- */

  function mostrarErrorGeneral(mensaje) {
    if (!errorGeneral) return;
    errorGeneral.textContent = mensaje;
    errorGeneral.classList.remove('hidden');
  }

  function ajustarMensajeExito() {
    if (!panelExito) return;

    const parrafo = panelExito.querySelector('p.text-gray-500');
    if (!parrafo) return;

    const enlace = parrafo.querySelector('a');
    parrafo.textContent =
      'Tu propuesta quedó registrada y pendiente de validación. ' +
      'Podrás seguir su estado desde ';
    if (enlace) parrafo.appendChild(enlace);
  }

  function enviar(evento) {
    evento.preventDefault();

    if (errorGeneral) errorGeneral.classList.add('hidden');

    if (!validar()) {
      const primero = $('.prop-input.border-red-400');
      if (primero) primero.focus();
      return;
    }

    const titulo = campos.nombre.value.trim();
    const opcionAsesor = campos.asesor.selectedOptions[0];
    const nombreAsesor = opcionAsesor
      ? opcionAsesor.getAttribute('data-name') || ''
      : '';
    const idAsesor = SIMULApi.idNumerico(campos.asesor.value);

    let descripcion = campos.descripcion.value.trim();

    /* Si el asesor es texto, se conserva su nombre, sin inventar id. */
    if (idAsesor === null && nombreAsesor) {
      descripcion += '\n\nDocente asesor: ' + nombreAsesor;
    }

    const payload = {
      titulo: titulo,
      tipo: 'proyecto',
      categoria: campos.categoria.value,
      anio: Number(campos.anio.value),
      descripcion: descripcion,
      imagen: IMAGEN_POR_DEFECTO,
      alt_text: 'Imagen representativa del proyecto ' + titulo,
      tecnologias: tecnologíasElegidas(),
      participantes: campos.integrantes.value.trim()
        .split(',').map(function (nombre) { return nombre.trim(); })
        .filter(function (nombre) { return nombre.length > 0; }),
      resultados_impacto: campos.resultados.value.trim()
    };

    if (idAsesor !== null) payload.id_asesor = idAsesor;

    botonEnviar.disabled = true;
    botonEnviar.textContent = 'Enviando…';

    SIMULApi.crearContenido(payload)
      .then(function (creado) {
        /* Resumen de la propuesta enviada. */
        const resumen = $('#proposal-summary');
        if (resumen) {
          resumen.textContent =
            titulo + ' · ' + campos.anio.value + ' · ' +
            (creado && creado.id_contenido
              ? 'ID ' + creado.id_contenido
              : 'pendiente de validación');
        }

        ajustarMensajeExito();

        formulario.classList.add('hidden');
        panelExito.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        if (archivos.length) {
          SIMUL.toast(
            'Propuesta guardada. Los archivos seleccionados no se subieron; ' +
            'solo se registraron los datos.',
            'info'
          );
        } else {
          SIMUL.toast('Propuesta guardada correctamente.', 'success');
        }
      })
      .catch(function (error) {
        mostrarErrorGeneral(error.message);
        botonEnviar.disabled = false;
        botonEnviar.textContent = TEXTO_ENVIAR;
        SIMUL.toast(error.message);
      });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    const user = SIMUL.guardPage('student');
    if (!user) return;

    if (formulario) formulario.addEventListener('submit', enviar);

    if (campos.asesor) {
      campos.asesor.addEventListener('change', function () {
        pintarAsesor();
        SIMUL.setFieldError(campos.asesor, '');
      });
    }

    $$('.tech-option').forEach(function (etiqueta) {
      etiqueta.addEventListener('click', function () {
        /* El clic se procesa después de que el checkbox cambie. */
        window.setTimeout(pintarTecnologias, 0);
      });
    });

    $$('.prop-input').forEach(function (campo) {
      campo.addEventListener('change', function () {
        SIMUL.setFieldError(campo, '');
      });
    });

    pintarTecnologias();
  });

})();
