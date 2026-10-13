/* ==========================================================
   FAVORITOS  (RF-EXP-04)

   Lista el contenido guardado por el usuario. Los ids viven en
   localStorage; el texto sale del catálogo que entrega la ruta.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const GRID  = $('#favorites-grid');
  const VACIO = $('#favorites-empty');

  /* ----------------------------------------------------------
     PINTADO
     ---------------------------------------------------------- */

  function pintar() {
    if (!GRID) return;

    /* La primera vez se siembra la lista con cuatro piezas para
       que la pantalla no arranque vacía en la demostración. */
    Store.initFavorites(window.SIMUL_SEED_FAVORITES || []);

    const catalogo = Store.getContent();
    const ids = Store.getFavorites() || [];

    /* Se conserva el orden en que el usuario guardó. */
    const items = ids
      .map(function (id) {
        return catalogo.find(function (c) {
          return String(c.id) === String(id);
        });
      })
      .filter(Boolean);

    GRID.classList.toggle('hidden', items.length === 0);
    GRID.classList.toggle('grid', items.length > 0);

    VACIO.classList.toggle('hidden', items.length !== 0);
    VACIO.classList.toggle('flex', items.length === 0);

    GRID.innerHTML = items.map(SIMUL.contentCardHtml).join('');

    /* Refleja el estado de cada botón ★ / ☆. */
    ids.forEach(function (id) {
      SIMUL.$$('[data-favorite="' + id + '"]').forEach(function (btn) {
        btn.textContent = '★';
        btn.style.color = '#C9A84C';
      });
    });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    const user = SIMUL.guardPage();
    if (!user) return;

    pintar();

    /* Quitar un favorito desde esta misma pantalla vacía la
       cuadrícula al instante. */
    document.addEventListener('simul:favorites-changed', function (event) {
      if (!event.detail.active) pintar();
    });
  });

})();
