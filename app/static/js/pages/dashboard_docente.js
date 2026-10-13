/* ==========================================================
   PANEL DEL DOCENTE  (RF-DSH-04 / RF-PRY-02)

   Además de lo que el servidor ya pintó (contenido registrado
   y distribución por estado), esta pantalla lista los proyectos
   de estudiantes que el docente tiene asignados como asesor.

   Esos proyectos los carga el propio estudiante en
   /proponer-contenido y quedan en `simul.proposals`, así que
   aquí se leen del mismo almacén.
   ========================================================== */

(function () {
  'use strict';

  const $ = SIMUL.$;

  const CONTENEDOR = $('#teacher-proposals');

  /* ----------------------------------------------------------
     1. PROPUESTAS ASESORADAS
     ---------------------------------------------------------- */

  /** El id del docente en el catálogo de asesores. */
  function miIdDeAsesor(user) {
    /* La pantalla se identifica por nombre: es lo único que
       el prototipo daba por ordenado. Con el backend este
       bloque desaparece y el filtro es `asesor_id = ?`. */
    return user.name;
  }

  function tarjeta(propuesta) {
    const badge = {
      pendiente: 'tag-pendiente',
      aprobado:  'tag-publicado',
      rechazado: 'tag-rechazado'
    }[propuesta.status] || 'tag-blue';

    return '' +
      '<a href="/mis-aportes" ' +
      'class="simul-card p-4 block hover:border-[#C8102E] ' +
      'transition-colors">' +

        '<div class="flex items-start justify-between gap-3 mb-2">' +
          '<span class="text-sm font-semibold text-gray-800 line-clamp-2" ' +
          'style="font-family:\'Montserrat\',sans-serif">' +
            SIMUL.escapeHtml(propuesta.name) +
          '</span>' +
          '<span class="tag ' + badge + ' shrink-0">' +
            SIMUL.capitalize(propuesta.status) +
          '</span>' +
        '</div>' +

        '<p class="text-xs text-gray-500 mb-1" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '📅 ' + SIMUL.escapeHtml(propuesta.year || '—') +
        '</p>' +

        '<p class="text-xs text-gray-400 truncate" ' +
        'style="font-family:\'Inter\',sans-serif">' +
          '👥 ' + SIMUL.escapeHtml(propuesta.members || 'Sin integrantes') +
        '</p>' +

      '</a>';
  }

  function pintar() {
    if (!CONTENEDOR) return;

    const user = Store.getUser();
    if (!user) return;

    const propuestas = Store.getProposals();
    const filtradas = propuestas.filter(function (p) {
      return p.teacherName === miIdDeAsesor(user);
    });

    if (filtradas.length === 0) {
      CONTENEDOR.innerHTML =
        '<div class="simul-card p-6 text-center">' +
          '<div class="text-3xl mb-2">💡</div>' +
          '<p class="text-xs text-gray-500" ' +
          'style="font-family:\'Inter\',sans-serif">' +
            'No tienes proyectos asignados todavía.' +
          '</p>' +
        '</div>';
      return;
    }

    CONTENEDOR.innerHTML = filtradas.map(tarjeta).join('');
  }

  /* ----------------------------------------------------------
     ARRANQUE
     ---------------------------------------------------------- */

  document.addEventListener('simul:ready', function () {
    if (!SIMUL.guardPage('teacher')) return;

    pintar();

    /* Si el estudiante envía una propuesta en otra pestaña,
       esta se refleja al volver al panel. */
    window.addEventListener('storage', pintar);
  });

})();
