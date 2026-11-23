/* ==========================================================
   ADJUNTAR EVIDENCIAS
   Cada archivo se registra con POST /contenido/<id>/evidencias.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const ICONOS = window.SIMUL_FILE_ICONS || {};

  const ZONA    = $('#evidence-dropzone');
  const INPUT   = $('#evidence-files');
  const LISTA   = $('#evidence-list');
  const VACIO   = $('#evidence-empty');
  const RESUMEN = $('#evidence-summary');
  const ENVIAR  = $('#evidence-submit');
  const PANTALLA = $('#evidence-done');

  /* Los dos ejemplos del prototipo pasan a ser registros reales. */
  let archivos = [
    {
      id: 'ejemplo-1',
      nombre: 'Informe_Final_SISTEC.pdf',
      extension: 'pdf',
      tamano: '3.2 MB',
      tipo: 'doc',
      url_archivo: 'Informe_Final_SISTEC.pdf',
      alt_text: 'Informe_Final_SISTEC.pdf'
    },
    {
      id: 'ejemplo-2',
      nombre: 'Presentacion_Premio.pptx',
      extension: 'pptx',
      tamano: '8.7 MB',
      tipo: 'doc',
      url_archivo: 'Presentacion_Premio.pptx',
      alt_text: 'Presentacion_Premio.pptx'
    }
  ];

  let contenidoId = null;
  let aviso = null;
  let guardando = false;

  /* ----------------------------------------------------------
     1. ID DEL CONTENIDO
     ---------------------------------------------------------- */

  function idDesdePagina() {
    const candidatos = [];

    if (window.SIMUL_CONTENT_ID !== undefined &&
        window.SIMUL_CONTENT_ID !== null &&
        window.SIMUL_CONTENT_ID !== '') {
      candidatos.push(window.SIMUL_CONTENT_ID);
    }

    const parametros = new URLSearchParams(window.location.search);

    candidatos.push(parametros.get('id'));
    candidatos.push(parametros.get('contenido_id'));

    const partes = window.location.pathname.split('/').filter(Boolean);
    candidatos.push(partes[partes.length - 1]);

    for (let i = 0; i < candidatos.length; i++) {
      const numero = SIMULApi.idNumerico(candidatos[i]);
      if (numero) return numero;
    }

    return null;
  }

  function crearAviso() {
    aviso = document.createElement('p');

    aviso.id = 'evidence-content-id';
    aviso.className = 'text-xs text-gray-500 mb-6';
    aviso.style.fontFamily = 'Inter, sans-serif';

    aviso.textContent = contenidoId
      ? 'Evidencias para el contenido #' + contenidoId + '.'
      : 'No se indicó el contenido. Abre esta página con ?id=<número> ' +
        'o define window.SIMUL_CONTENT_ID.';

    if (ZONA && ZONA.parentNode) {
      ZONA.parentNode.insertBefore(aviso, ZONA);
    }
  }

  /* ----------------------------------------------------------
     2. PINTADO
     ---------------------------------------------------------- */

  function iconoDe(archivo) {
    return ICONOS[archivo.extension] || ICONOS[archivo.tipo] || '📄';
  }

  function pintar() {
    LISTA.innerHTML = archivos.map(function (archivo) {
      return '' +
        '<li class="simul-card p-4">' +
          '<div class="flex items-center gap-4">' +

            '<span class="text-2xl shrink-0">' +
              iconoDe(archivo) +
            '</span>' +

            '<span class="flex-1 min-w-0">' +
              '<span class="flex items-center gap-2">' +
                '<span class="text-sm font-semibold text-gray-800 ' +
                'truncate" style="font-family:\'Montserrat\',sans-serif">' +
                  SIMUL.escapeHtml(archivo.nombre) +
                '</span>' +
                '<span class="tag tag-blue shrink-0">' +
                  SIMUL.capitalize(archivo.tipo) +
                '</span>' +
              '</span>' +

              '<span class="flex items-center gap-3 mt-2">' +
                '<span class="text-xs text-gray-400 truncate">' +
                  (archivo.tipo === 'foto'
                    ? 'Texto alternativo: ' + archivo.alt_text
                    : 'URL: ' + archivo.url_archivo) +
                '</span>' +
                '<span class="text-xs text-gray-400 shrink-0">' +
                  SIMUL.escapeHtml(archivo.tamano) +
                '</span>' +
              '</span>' +
            '</span>' +

            '<button type="button" data-remove="' + archivo.id + '" ' +
              'class="text-gray-400 hover:text-red-600 transition-colors ' +
              'shrink-0" aria-label="Quitar archivo">✕</button>' +
          '</div>' +
        '</li>';
    }).join('');

    const hay = archivos.length > 0;

    VACIO.classList.toggle('hidden', hay);

    RESUMEN.textContent = !contenidoId
      ? 'Sin contenido asociado'
      : hay
        ? archivos.length + (archivos.length === 1
            ? ' archivo'
            : ' archivos')
        : '0 archivos';

    ENVIAR.disabled = guardando || !hay || !contenidoId;
    ENVIAR.textContent = guardando ? 'Guardando…' : 'Guardar evidencias';
  }

  /* ----------------------------------------------------------
     3. SELECCIÓN DE ARCHIVOS
     ---------------------------------------------------------- */

  function tipoDe(extension) {
    if (['png', 'jpg', 'jpeg', 'gif', 'webp'].indexOf(extension) !== -1) {
      return 'foto';
    }
    if (['mp4', 'webm', 'mov'].indexOf(extension) !== -1) {
      return 'video';
    }
    return 'doc';
  }

  function agregar(listaRecibida) {
    Array.prototype.forEach.call(listaRecibida, function (file) {
      const extension = (file.name.split('.').pop() || '').toLowerCase();
      const tipo = tipoDe(extension);

      archivos.push({
        id: 'f' + Date.now() + Math.random().toString(36).slice(2, 7),
        nombre: file.name,
        extension: extension,
        tamano: (file.size / 1024 / 1024).toFixed(1) + ' MB',
        tipo: tipo,
        url_archivo: file.name,
        alt_text: tipo === 'foto' ? file.name : ''
      });
    });

    pintar();
  }

  if (INPUT) {
    INPUT.addEventListener('change', function () {
      if (INPUT.files && INPUT.files.length) agregar(INPUT.files);
    });
  }

  if (ZONA) {
    ['dragenter', 'dragover'].forEach(function (evento) {
      ZONA.addEventListener(evento, function (e) {
        e.preventDefault();
        ZONA.classList.add('border-[#C8102E]', 'bg-red-50/30');
      });
    });

    ['dragleave', 'drop'].forEach(function (evento) {
      ZONA.addEventListener(evento, function (e) {
        e.preventDefault();
        ZONA.classList.remove('border-[#C8102E]', 'bg-red-50/30');
      });
    });

    ZONA.addEventListener('drop', function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        agregar(e.dataTransfer.files);
      }
    });
  }

  if (LISTA) {
    LISTA.addEventListener('click', function (event) {
      const boton = event.target.closest('[data-remove]');
      if (!boton) return;

      const id = boton.getAttribute('data-remove');
      archivos = archivos.filter(function (a) { return a.id !== id; });
      pintar();
    });
  }

  /* ----------------------------------------------------------
     4. ENVÍO A LA API
     ---------------------------------------------------------- */

  function mostrarResultado(guardadas, fallidas) {
    if (!PANTALLA) return;

    const texto = PANTALLA.querySelector('p');

    if (texto) {
      texto.textContent =
        'Se guardaron ' + guardadas +
        (guardadas === 1 ? ' evidencia' : ' evidencias') +
        ' en el contenido #' + contenidoId + '.' +
        (fallidas
          ? ' No se pudieron guardar ' + fallidas + '.'
          : '');
    }

    SIMUL.$$('#evidence-dropzone, #evidence-list, #evidence-empty, ' +
             '#evidence-submit').forEach(function (el) {
      el.classList.add('hidden');
    });

    if (aviso) aviso.classList.add('hidden');

    PANTALLA.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function enviar() {
    if (!contenidoId) {
      SIMUL.toast(
        'No se indicó el contenido de las evidencias',
        'error'
      );
      return;
    }

    if (archivos.length === 0) {
      SIMUL.toast('Adjunta al menos un archivo antes de guardar', 'error');
      return;
    }

    const pendientes = archivos.slice();
    let guardadas = 0;
    let fallidas = 0;
    let cadena = Promise.resolve();

    guardando = true;
    ENVIAR.disabled = true;
    ENVIAR.textContent = 'Guardando…';

    pendientes.forEach(function (archivo) {
      cadena = cadena
        .then(function () {
          return SIMULApi.agregarEvidencia(contenidoId, {
            tipo: archivo.tipo,
            url_archivo: archivo.url_archivo,
            alt_text: archivo.alt_text
          });
        })
        .then(function () {
          guardadas++;
          archivos = archivos.filter(function (a) {
            return a.id !== archivo.id;
          });
          pintar();
        })
        .catch(function (error) {
          fallidas++;
          SIMUL.toast(
            error.message || 'No se pudo guardar ' + archivo.nombre,
            'error'
          );
        });
    });

    cadena.then(function () {
      guardando = false;
      pintar();

      if (guardadas === 0) return;

      mostrarResultado(guardadas, fallidas);

      if (!fallidas) {
        SIMUL.toast('Evidencias guardadas en la base', 'success');
      }
    }).catch(function (error) {
      guardando = false;
      pintar();
      SIMUL.toast(error.message || 'No se pudo completar el envío', 'error');
    });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('teacher')) return;

    contenidoId = idDesdePagina();
    crearAviso();
    pintar();

    if (ENVIAR) ENVIAR.addEventListener('click', enviar);
  });

})();
