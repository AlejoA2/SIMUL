/* ==========================================================
   SIMUL - CLIENTE DE LA API

   Todas las pantallas que ejecutan una acción real pasan por
   aquí. El token del inicio de sesión se guarda en el
   navegador y se envía en la cabecera Authorization.

   Respuestas de la API:
     { success, message, data }  → se devuelve `data`
     { success, message, details } → se lanza un error
   ========================================================== */

(function () {
  'use strict';

  const BASE  = '/api/museo';
  const CLAVE = 'simul.token';

  function getToken() {
    try { return localStorage.getItem(CLAVE); }
    catch (e) { return null; }
  }

  function setToken(token) {
    try { localStorage.setItem(CLAVE, token); }
    catch (e) { /* modo privado: la sesión vive solo en memoria */ }
    return token;
  }

  function clearToken() {
    try { localStorage.removeItem(CLAVE); }
    catch (e) { /* nada que limpiar */ }
  }

  function mensajeDeError(cuerpo, status) {
    if (cuerpo && cuerpo.details) {
      if (Array.isArray(cuerpo.details) && cuerpo.details.length) {
        const primero = cuerpo.details[0];
        if (primero && primero.msg) return primero.msg;
        return String(primero);
      }
      if (typeof cuerpo.details === 'string') return cuerpo.details;
    }
    if (cuerpo && cuerpo.message && typeof cuerpo.message === 'string') {
      return cuerpo.message;
    }
    return 'Error ' + status + ' en la petición';
  }

  async function request(path, options) {
    const opciones = options || {};
    const cabeceras = { 'Accept': 'application/json' };
    let cuerpo;

    if (opciones.body !== undefined) {
      cabeceras['Content-Type'] = 'application/json';
      cuerpo = JSON.stringify(opciones.body);
    }

    const token = getToken();
    if (token && opciones.auth !== false) {
      cabeceras['Authorization'] = 'Bearer ' + token;
    }

    let respuesta;
    try {
      respuesta = await fetch(BASE + path, {
        method: opciones.method || 'GET',
        headers: cabeceras,
        body: cuerpo
      });
    } catch (e) {
      throw {
        status: 0,
        message: 'No se pudo conectar con el servidor. Revisa que Docker esté arriba.'
      };
    }

    let json = null;
    try { json = await respuesta.json(); }
    catch (e) { /* respuesta sin cuerpo JSON */ }

    if (!respuesta.ok) {
      throw {
        status: respuesta.status,
        message: mensajeDeError(json, respuesta.status),
        details: json && json.details
      };
    }

    return json && json.data !== undefined ? json.data : json;
  }

  /* ----------------------------------------------------------
     UTILIDADES
     ---------------------------------------------------------- */

  /** Los id del prototipo eran texto; la base usa enteros. */
  function idNumerico(valor) {
    const texto = String(valor === null || valor === undefined ? '' : valor);
    if (!/^\d+$/.test(texto)) return null;
    return Number(texto);
  }

  /** Resumen de la API → ficha que entiende Store. */
  function aTarjeta(item) {
    return {
      id: item.id_contenido,
      title: item.titulo,
      year: item.anio,
      category: item.categoria,
      categoryTag: 'tag-blue',
      description: item.descripcion || '',
      image: item.imagen || '',
      author: (item.autor && item.autor.nombre) || 'Autor del museo',
      tags: item.tipo ? [item.tipo] : [],
      status: item.estado || 'publicado',
      participants: [],
      technologies: [],
      documents: [],
      observations: item.observaciones || ''
    };
  }

  /* ----------------------------------------------------------
     AUTENTICACIÓN Y USUARIOS
     ---------------------------------------------------------- */

  function login(correo, password) {
    return request('/auth/login', {
      method: 'POST',
      auth: false,
      body: { correo: correo, password: password }
    }).then(function (datos) {
      setToken(datos.access_token);
      return datos;
    });
  }

  function register(datos) {
    return request('/auth/register', {
      method: 'POST',
      auth: false,
      body: datos
    });
  }

  function me() {
    return request('/auth/me');
  }

  function updateProfile(id, datos) {
    return request('/admin/usuarios/' + encodeURIComponent(id), {
      method: 'PATCH',
      body: datos
    });
  }

  function usuarios(filtros) {
    const query = new URLSearchParams();
    Object.keys(filtros || {}).forEach(function (clave) {
      if (filtros[clave] !== null && filtros[clave] !== undefined &&
          filtros[clave] !== '') {
        query.append(clave, filtros[clave]);
      }
    });
    const sufijo = query.toString() ? '?' + query.toString() : '';
    return request('/admin/usuarios' + sufijo);
  }

  function updateUsuario(id, datos) {
    return request('/admin/usuarios/' + encodeURIComponent(id), {
      method: 'PATCH',
      body: datos
    });
  }

  function kpis() {
    return request('/admin/kpis');
  }

  /* ----------------------------------------------------------
     CONTENIDO
     ---------------------------------------------------------- */

  function bandeja() {
    return request('/validacion/bandeja');
  }

  function historial(contenidoId) {
    return request('/validacion/' + encodeURIComponent(contenidoId) + '/historial');
  }

  function aprobar(contenidoId, observaciones) {
    return request(
      '/validacion/' + encodeURIComponent(contenidoId) + '/aprobar',
      {
        method: 'POST',
        body: observaciones ? { observaciones: observaciones } : {}
      }
    );
  }

  function rechazar(contenidoId, observaciones) {
    return request(
      '/validacion/' + encodeURIComponent(contenidoId) + '/rechazar',
      {
        method: 'POST',
        body: { observaciones: observaciones }
      }
    );
  }

  function contenido(params) {
    const query = new URLSearchParams();

    Object.keys(params || {}).forEach(function (clave) {
      const valor = params[clave];
      if (valor !== null && valor !== undefined && valor !== '') {
        query.append(clave, valor);
      }
    });

    const sufijo = query.toString() ? '?' + query.toString() : '';
    return request('/contenido/' + sufijo);
  }

  function contenidoDetalle(contenidoId) {
    return request('/contenido/' + encodeURIComponent(contenidoId));
  }

  function crearContenido(datos) {
    return request('/contenido/', {
      method: 'POST',
      body: datos
    });
  }

  function actualizarContenido(contenidoId, datos) {
    return request('/contenido/' + encodeURIComponent(contenidoId), {
      method: 'PATCH',
      body: datos
    });
  }

  function eliminarContenido(contenidoId) {
    return request('/contenido/' + encodeURIComponent(contenidoId), {
      method: 'DELETE'
    });
  }

  function misAportes() {
    return request('/contenido/mis-aportes');
  }

  function favoritos() {
    return request('/contenido/favoritos');
  }

  function toggleFavorito(contenidoId) {
    return request('/contenido/' + encodeURIComponent(contenidoId) + '/favorito', {
      method: 'POST',
      body: {}
    });
  }

  function comentarios(contenidoId) {
    return request(
      '/contenido/' + encodeURIComponent(contenidoId) + '/comentarios',
      { auth: false }
    );
  }

  function comentar(contenidoId, texto, respuestaA) {
    const cuerpo = { texto: texto };
    if (respuestaA) cuerpo.respuesta_a = Number(respuestaA);
    return request(
      '/contenido/' + encodeURIComponent(contenidoId) + '/comentarios',
      { method: 'POST', body: cuerpo }
    );
  }

  function reaccion(contenidoId, tipo) {
    return request('/contenido/' + encodeURIComponent(contenidoId) + '/reaccion', {
      method: 'POST',
      body: { tipo_reaccion: tipo || 'like' }
    });
  }

  function evidencias(contenidoId) {
    return request(
      '/contenido/' + encodeURIComponent(contenidoId) + '/evidencias',
      { auth: false }
    );
  }

  function agregarEvidencia(contenidoId, datos) {
    return request(
      '/contenido/' + encodeURIComponent(contenidoId) + '/evidencias',
      { method: 'POST', body: datos }
    );
  }

  /* ----------------------------------------------------------
     GAMIFICACIÓN Y MUSEO
     ---------------------------------------------------------- */

  function ranking(limite) {
    return request('/gamificacion/ranking' + (limite ? '?limite=' + limite : ''),
      { auth: false });
  }

  function niveles() {
    return request('/gamificacion/niveles', { auth: false });
  }

  function insignias() {
    return request('/gamificacion/insignias', { auth: false });
  }

  function miHistorial() {
    return request('/gamificacion/mi-historial');
  }

  function home() {
    return request('/home', { auth: false });
  }

  window.SIMULApi = {
    getToken: getToken,
    setToken: setToken,
    clearToken: clearToken,
    request: request,
    logout: clearToken,
    idNumerico: idNumerico,
    aTarjeta: aTarjeta,
    login: login,
    register: register,
    me: me,
    updateProfile: updateProfile,
    usuarios: usuarios,
    updateUsuario: updateUsuario,
    kpis: kpis,
    bandeja: bandeja,
    historial: historial,
    aprobar: aprobar,
    rechazar: rechazar,
    contenido: contenido,
    contenidoDetalle: contenidoDetalle,
    crearContenido: crearContenido,
    actualizarContenido: actualizarContenido,
    eliminarContenido: eliminarContenido,
    misAportes: misAportes,
    favoritos: favoritos,
    toggleFavorito: toggleFavorito,
    comentarios: comentarios,
    comentar: comentar,
    reaccion: reaccion,
    evidencias: evidencias,
    agregarEvidencia: agregarEvidencia,
    ranking: ranking,
    niveles: niveles,
    insignias: insignias,
    miHistorial: miHistorial,
    home: home
  };
})();
