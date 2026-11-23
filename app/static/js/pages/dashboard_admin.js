/* ==========================================================
   PANEL DEL ADMINISTRADOR
   Los indicadores se leen de /api/museo/admin/kpis.
   ========================================================== */

(function () {
  'use strict';

  const VALOR_DE_KPI = {
    'Premios registrados': function (datos) {
      return datos.contenido.por_tipo.premio;
    },
    'Proyectos publicados': function (datos) {
      return datos.contenido.por_tipo.proyecto;
    },
    'Eventos realizados': function (datos) {
      return datos.contenido.por_tipo.evento;
    },
    'Publicaciones cientificas': function (datos) {
      return datos.contenido.por_tipo.avance_investigacion;
    },
    'Hall de la Fama': function (datos) {
      return datos.contenido.por_tipo.hall;
    },
    'Usuarios activos': function (datos) {
      return datos.usuarios_activos;
    }
  };

  function pintar(datos) {
    SIMUL.$$('[data-kpi]').forEach(function (tarjeta) {
      const obtener = VALOR_DE_KPI[tarjeta.getAttribute('data-kpi')];
      if (!obtener) return;

      const valor = obtener(datos);
      if (valor === undefined || valor === null) return;

      const numero = tarjeta.querySelector('p.text-3xl');

      if (numero) {
        numero.textContent = Number(valor).toLocaleString('es-CO');
      }

      const cambio = tarjeta.querySelector('span.rounded-full');

      if (cambio) {
        cambio.textContent = 'Dato real';
      }
    });
  }

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('admin')) return;

    SIMULApi.kpis()
      .then(pintar)
      .catch(function (error) {
        SIMUL.toast(
          error.message || 'No se pudieron cargar los indicadores',
          'error'
        );
      });
  });
})();
