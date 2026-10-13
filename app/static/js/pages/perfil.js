/* ==========================================================
   MI PERFIL  (RF-USR-03)

   La descripción pública es el único campo editable de este
   corte. Se guarda en la sesión del navegador y se refleja en
   el resto de pantallas, porque todas leen del mismo sitio.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const BOTON_EDITAR   = $('#edit-description');
  const EDITOR         = $('#description-editor');
  const AREA           = $('#description-input');
  const BOTON_GUARDAR  = $('#description-save');
  const BOTON_CANCELAR = $('#description-cancel');

  const LIMITE = 300;

  /* ----------------------------------------------------------
     1. EDITAR DESCRIPCIÓN
     ---------------------------------------------------------- */

  function abrirEditor(user) {
    if (!AREA) return;

    AREA.value = user.description || '';
    AREA.maxLength = LIMITE;

    EDITOR.classList.remove('hidden');
    BOTON_EDITAR.classList.add('hidden');
    AREA.focus();
  }

  function cerrarEditor() {
    EDITOR.classList.add('hidden');
    BOTON_EDITAR.classList.remove('hidden');
  }

  function guardar(user) {
    const texto = AREA.value.trim();

    if (!texto) {
      SIMUL.toast('La descripción no puede quedar vacía', 'error');
      return;
    }

    /* Se recorta al límite para no romper el diseño de las
       tarjetas donde se muestra el texto del usuario. */
    const recortada = texto.slice(0, LIMITE);

    Store.updateUser({ description: recortada });

    /* Se repinta con el texto ya guardado. */
    SIMUL.paintUser(Store.getUser());

    cerrarEditor();
    SIMUL.toast('Descripción actualizada', 'success');
  }

  /* ----------------------------------------------------------
     2. PROGRESO DE NIVEL

     El ancho se calcula con los puntos de la sesión para que
     quede sincronizado si el usuario cambia de cuenta.
     ---------------------------------------------------------- */

  function pintarProgreso(user) {
    const barra = SIMUL.$('.simul-card .gold-bar');
    if (!barra) return;

    const pct = Math.min((user.points / 2000) * 100, 100);
    barra.style.width = pct.toFixed(1) + '%';
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    const user = SIMUL.guardPage();
    if (!user) return;

    pintarProgreso(user);

    if (BOTON_EDITAR) {
      BOTON_EDITAR.addEventListener('click', function () {
        abrirEditor(user);
      });
    }

    if (BOTON_GUARDAR) {
      BOTON_GUARDAR.addEventListener('click', function () {
        guardar(user);
      });
    }

    if (BOTON_CANCELAR) {
      BOTON_CANCELAR.addEventListener('click', cerrarEditor);
    }

    /* Ctrl/Cmd + Enter guarda sin sacar el foco del área. */
    if (AREA) {
      AREA.addEventListener('keydown', function (event) {
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
          guardar(user);
        }
        if (event.key === 'Escape') cerrarEditor();
      });
    }
  });

})();
