/* ==========================================================
   FAVORITOS  (RF-EXP-04)

   La lista viene de SIMULApi.favoritos(). Cada resumen se
   convierte con aTarjeta y se pinta con contentCardHtml. El
   botón ★ sigue siendo responsabilidad de app.js.
   ========================================================== */

(function () {
  'use strict';

  const $  = SIMUL.$;
  const $$ = SIMUL.$$;

  const GRID  = $('#favorites-grid');
  const VACIO = $('#favorites-empty');

  function alternarVista(hayFavoritos) {
    if (GRID) {
      GRID.classList.toggle('hidden', !hayFavoritos);
      GRID.classList.toggle('grid', hayFavoritos);
    }

    if (VACIO) {
      VACIO.classList.toggle('hidden', hayFavoritos);
      VACIO.classList.toggle('flex', !hayFavoritos);
    }
  }

  function mensaje(markup) {
    if (VACIO) VACIO.innerHTML = markup;
    alternarVista(false);
  }

  function sinSesion() {
    mensaje('' +
      '<div class="text-6xl mb-5">🔒</div>' +
      '<h3 style="font-family:\'Montserrat\',sans-serif;font-weight:700;' +
      'font-size:22px;color:#1A1A1A">' +
        'Inicia sesión para ver tus favoritos' +
      '</h3>' +
      '<p class="text-gray-500 mt-2 max-w-sm" ' +
      'style="font-family:\'Inter\',sans-serif">' +
        'Tu lista de favoritos está asociada a tu cuenta.' +
      '</p>' +
      '<a href="/login" class="btn-primary mt-6">Iniciar sesión</a>'
    );
  }

  function pintar() {
    if (!GRID) return Promise.resolve();

    if (!Store.getUser()) {
      sinSesion();
      return Promise.resolve();
    }

    return SIMULApi.favoritos()
      .then(function (datos) {
        const tarjetas = (datos || []).map(SIMULApi.aTarjeta);

        GRID.innerHTML = tarjetas.map(SIMUL.contentCardHtml).join('');
        alternarVista(tarjetas.length > 0);

        /* Todo lo que aparece aquí es favorito: refleja la ★
           sin volver a lanzar la acción de guardar. */
        $$('[data-favorite]', GRID).forEach(function (boton) {
          boton.textContent = '★';
          boton.style.color = '#C9A84C';
          boton.setAttribute('aria-pressed', 'true');
        });
      })
      .catch(function (error) {
        SIMUL.toast(error.message);
        GRID.innerHTML = '';
        alternarVista(false);
      });
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    pintar();

    /* app.js ya actualizó Store y avisó del cambio: solo
       necesitamos pedir la lista otra vez a la API. */
    document.addEventListener('simul:favorites-changed', function () {
      pintar();
    });
  });

})();
