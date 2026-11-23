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
    return request('/contenido/' + sufijo, { auth: false });
  }

  window.SIMULApi = {
    getToken: getToken,
    setToken: setToken,
    clearToken: clearToken,
    request: request,
    login: login,
    logout: clearToken,
    bandeja: bandeja,
    historial: historial,
    aprobar: aprobar,
    rechazar: rechazar,
    contenido: contenido
  };
})();
