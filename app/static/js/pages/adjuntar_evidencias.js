/* ==========================================================
   ADJUNTAR EVIDENCIAS  (RNF-ACC-01)

   Lista de archivos con barra de progreso simulada. Al enviar
   confirma que todo terminó de cargar; en la siguiente fase
   se reemplaza por POST /api/contenido/<id>/evidencias con
   multipart/form-data.
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

  /* Los dos archivos que ya traía el prototipo al abrir la
     pantalla: uno completo y otro a medio cargar. */
  let archivos = [
    { id: '1', nombre: 'Informe_Final_SISTEC.pdf', tamano: '3.2 MB',
      tipo: 'pdf', progreso: 100 },
    { id: '2', nombre: 'Presentacion_Premio.pptx', tamano: '8.7 MB',
      tipo: 'pptx', progreso: 68 }
  ];

  /* ----------------------------------------------------------
     1. PINTADO
     ---------------------------------------------------------- */

  function iconoDe(tipo) {
    return ICONOS[String(tipo).toLowerCase()] || '📄';
  }

  function pintar() {
    LISTA.innerHTML = archivos.map(function (archivo) {
      const completo = archivo.progreso >= 100;

      return '' +
        '<li class="simul-card p-4">' +
          '<div class="flex items-center gap-4">' +

            '<span class="text-2xl shrink-0">' +
              iconoDe(archivo.tipo) +
            '</span>' +

            '<span class="flex-1 min-w-0">' +
              '<span class="flex items-center gap-2">' +
                '<span class="text-sm font-semibold text-gray-800 ' +
                'truncate" style="font-family:\'Montserrat\',sans-serif">' +
                  SIMUL.escapeHtml(archivo.nombre) +
                '</span>' +
                (completo
                  ? '<span class="text-green-600 text-xs shrink-0">✓</span>'
                  : '') +
              '</span>' +

              '<span class="flex items-center gap-3 mt-2">' +
                '<span class="flex-1 h-1.5 rounded-full bg-gray-200 ' +
                'overflow-hidden">' +
                  '<span class="block h-full rounded-full ' +
                  'transition-all duration-300" style="width:' +
                    archivo.progreso + '%;background:' +
                    (completo ? '#059669' : '#C8102E') + '"></span>' +
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

    /* Estado vacío y contador. */
    const hay = archivos.length > 0;

    VACIO.classList.toggle('hidden', hay);

    RESUMEN.textContent = hay
      ? archivos.length + (archivos.length === 1
          ? ' archivo'
          : ' archivos')
      : '0 archivos';

    /* Solo se habilita el envío si no hay cargas en curso. */
    ENVIAR.disabled = !hay || archivos.some(function (a) {
      return a.progreso < 100;
    });

    ENVIAR.textContent = ENVIAR.disabled && hay
      ? 'Espera a que termine la carga…'
      : 'Guardar evidencias';
  }

  /* ----------------------------------------------------------
     2. CARGA
     ---------------------------------------------------------- */

  function agregar(listaRecibida) {
    Array.prototype.forEach.call(listaRecibida, function (file) {
      const extension = (file.name.split('.').pop() || '').toLowerCase();

      const archivo = {
        id: 'f' + Date.now() + Math.random().toString(36).slice(2, 7),
        nombre: file.name,
        tamano: (file.size / 1024 / 1024).toFixed(1) + ' MB',
        tipo: extension,
        progreso: 0
      };

      archivos.push(archivo);

      /* Progreso simulado: sube en saltos hasta llegar a 100. */
      const intervalo = window.setInterval(function () {
        archivo.progreso += Math.random() * 22 + 6;

        if (archivo.progreso >= 100) {
          archivo.progreso = 100;
          window.clearInterval(intervalo);
        }

        pintar();
      }, 320);
    });

    pintar();
  }

  if (INPUT) {
    INPUT.addEventListener('change', function () {
      if (INPUT.files && INPUT.files.length) agregar(INPUT.files);
    });
  }

  /* Arrastrar y soltar sobre toda la zona. */
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

  /* ----------------------------------------------------------
     3. QUITAR ARCHIVOS
     ---------------------------------------------------------- */

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
     4. ENVÍO
     ---------------------------------------------------------- */

  function enviar() {
    if (archivos.length === 0) {
      SIMUL.toast('Adjunta al menos un archivo antes de guardar', 'error');
      return;
    }

    const pendientes = archivos.filter(function (a) {
      return a.progreso < 100;
    });

    if (pendientes.length) {
      SIMUL.toast('Espera a que terminen de cargar los archivos', 'info');
      return;
    }

    ENVIAR.disabled = true;
    ENVIAR.textContent = 'Guardando…';

    window.setTimeout(function () {
      /* Se oculta el formulario y se muestra la confirmación. */
      SIMUL.$$('#evidence-dropzone, #evidence-list, #evidence-empty, ' +
               '#evidence-submit').forEach(function (el) {
        el.classList.add('hidden');
      });

      PANTALLA.classList.remove('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 700);
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (SIMUL.guardPage('teacher')) pintar();
    if (ENVIAR) ENVIAR.addEventListener('click', enviar);
  });

})();
