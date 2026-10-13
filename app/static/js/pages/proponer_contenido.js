/* ==========================================================
   PROPUESTA DE PROYECTO  (RF-PRY-01)

   Formulario largo con validación en el navegador, selección
   múltiple de tecnologías, vista previa del docente asesor y
   carga simulada de evidencias.

   Al enviar, la propuesta queda en `simul.proposals` para que
   el panel del docente pueda verla asignada.
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

  const campos = {
    nombre:      $('#prop-name'),
    anio:        $('#prop-year'),
    categoria:   $('#prop-category'),
    integrantes: $('#prop-members'),
    asesor:      $('#prop-teacher'),
    descripcion: areaDescripcion,
    resultados:  $('#prop-results')
  };

  /* Archivos cargados con su barra de progreso. */
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

    lista.innerHTML = archivos.map(function (archivo) {
      const colores = archivo.progreso === 100
        ? { fondo: '#059669', texto: 'Listo' }
        : { fondo: '#C8102E', texto: Math.round(archivo.progreso) + '%' };

      return '' +
        '<li class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 ' +
        'border border-gray-100">' +
          '<span class="text-xl">📄</span>' +
          '<span class="flex-1 min-w-0">' +
            '<span class="block text-sm text-gray-700 truncate" ' +
            'style="font-family:\'Inter\',sans-serif">' +
              SIMUL.escapeHtml(archivo.nombre) +
            '</span>' +
            '<span class="block h-1.5 rounded-full bg-gray-200 mt-2 ' +
            'overflow-hidden">' +
              '<span class="block h-full rounded-full" ' +
              'style="width:' + archivo.progreso + '%;' +
              'background:' + colores.fondo + '"></span>' +
            '</span>' +
          '</span>' +
          '<span class="text-xs text-gray-400 shrink-0">' +
            SIMUL.escapeHtml(archivo.tamano) +
          '</span>' +
          '<span class="text-xs font-semibold shrink-0 w-10 text-right" ' +
          'style="font-family:\'Montserrat\',sans-serif;color:' +
            colores.fondo + '">' + colores.texto + '</span>' +
          '<button type="button" data-remove-file="' + archivo.id + '" ' +
          'class="text-gray-400 hover:text-red-600 transition-colors ' +
          'shrink-0" aria-label="Quitar archivo">✕</button>' +
        '</li>';
    }).join('');
  }

  /* Progreso simulado con temporizadores, igual que en el
     prototipo: el archivo "sube" sin tocar el servidor. */
  function agregarArchivos(listaRecibida) {
    Array.prototype.forEach.call(listaRecibida, function (file) {
      const archivo = {
        id: 'f' + Date.now() + Math.random().toString(36).slice(2, 7),
        nombre: file.name,
        tamano: formato(file.size),
        progreso: 0
      };

      archivos.push(archivo);

      const intervalo = window.setInterval(function () {
        archivo.progreso += Math.random() * 25 + 5;

        if (archivo.progreso >= 100) {
          archivo.progreso = 100;
          window.clearInterval(intervalo);
        }

        pintarArchivos();
      }, 350);
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

  function enviar(evento) {
    evento.preventDefault();

    if (errorGeneral) errorGeneral.classList.add('hidden');

    if (!validar()) {
      const primero = $('.prop-input.border-red-400');
      if (primero) primero.focus();
      return;
    }

    /* Espera a que terminen de "subir" los archivos. */
    if (archivos.some(function (a) { return a.progreso < 100; })) {
      mostrarErrorGeneral(
        'Espera a que terminen de cargar los archivos antes de enviar.'
      );
      return;
    }

    const user = Store.getUser();
    const opcionAsesor = campos.asesor.selectedOptions[0];

    Store.addProposal({
      name: campos.nombre.value.trim(),
      year: campos.anio.value,
      category: campos.categoria.value,
      members: campos.integrantes.value.trim(),
      teacherId: campos.asesor.value,
      teacherName: opcionAsesor ? opcionAsesor.getAttribute('data-name') : '',
      description: campos.descripcion.value.trim(),
      technologies: tecnologíasElegidas(),
      results: campos.resultados.value.trim(),
      documents: archivos.map(function (a) {
        return { name: a.nombre, size: a.tamano };
      }),
      studentName: user ? user.name : '',
      studentEmail: user ? user.email : ''
    });

    /* Resumen de la propuesta enviada. */
    const resumen = $('#proposal-summary');
    if (resumen) {
      resumen.textContent =
        campos.nombre.value.trim() + ' · ' +
        campos.anio.value + ' · ' +
        archivos.length + (archivos.length === 1
          ? ' evidencia adjunta'
          : ' evidencias adjuntas');
    }

    botonEnviar.disabled = true;
    botonEnviar.textContent = 'Enviando…';

    window.setTimeout(function () {
      formulario.classList.add('hidden');
      panelExito.classList.remove('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 700);
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
