/* ==========================================================
   MIS APORTES  (RF-DSH-02 + RNF-SEG-04)

   Historial del contenido propuesto. Lo distintivo de esta
   pantalla es el modal de observaciones: cuando el
   administrador rechaza una pieza deja un motivo y el autor
   puede leerlo (nunca el resto de la comunidad).
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const LISTADO = $('.simul-card.overflow-hidden');
  const VACIO   = $('#contributions-empty');

  /* ----------------------------------------------------------
     MODAL DE OBSERVACIONES
     ---------------------------------------------------------- */

  function modalObservaciones(titulo, observaciones) {
    return '' +
      '<h3 class="text-lg mb-1" ' +
      'style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
      'color:#1A1A1A">' +
        SIMUL.escapeHtml(titulo) +
      '</h3>' +

      '<p class="text-xs mb-5" ' +
      'style="font-family:\'Inter\',sans-serif;color:#6B7280">' +
        'Motivo registrado por el administrador al rechazar el aporte.' +
      '</p>' +

      '<div class="p-4 rounded-xl bg-red-50 border-l-4 border-[#C8102E]">' +
        '<p class="text-sm text-gray-700 leading-relaxed" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          SIMUL.escapeHtml(observaciones) +
        '</p>' +
      '</div>' +

      '<div class="mt-6 flex justify-end">' +
        '<button type="button" onclick="SIMUL.closeModal()" ' +
        'class="btn-secondary">Entendido</button>' +
      '</div>';
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    SIMUL.guardPage();

    $$('[data-observations]').forEach(function (boton) {
      boton.addEventListener('click', function () {
        const observaciones = boton.getAttribute('data-observations');

        if (!observaciones) {
          SIMUL.toast('Esta pieza no tiene observaciones registradas', 'info');
          return;
        }

        SIMUL.openModal(
          'Observaciones del revisor',
          modalObservaciones(
            boton.getAttribute('data-title'),
            observaciones
          )
        );
      });
    });

    /* Si el usuario se registra desde cero y no tiene aportes,
       se muestra el estado vacío en lugar de una tabla vacía. */
    const tieneAportes = Store.getProposals().length > 0 ||
                        $$('[data-observations]').length > 0;

    if (!tieneAportes && LISTADO && VACIO) {
      LISTADO.classList.add('hidden');
      VACIO.classList.remove('hidden');
      VACIO.classList.add('flex');
    }
  });

})();
