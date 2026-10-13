/* ==========================================================
   SIMUL - STORE
   Capa de estado del frontend sobre localStorage.

   En este corte NO hay base de datos: toda la "persistencia"
   vive en el navegador. El objetivo es que al conectar la API
   REST solo se cambie este archivo y no las páginas.

   Claves usadas
     simul.user        → sesión activa (rol, nombre, puntos…)
     simul.favorites   → ids de contenido guardado
     simul.content     → contenido creado/editado por el usuario
     simul.queue       → bandeja de validación del admin
     simul.comments    → comentarios por contenido
     simul.reactions   → reacciones por contenido
     simul.proposals   → proyectos propuestos por estudiantes
     simul.users       → usuarios que administra el admin
   ========================================================== */

const Store = (() => {

  /* ---------- helpers de bajo nivel ---------- */

  function read(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      /* Cuota llena o modo privado: la app sigue funcionando
         en memoria, simplemente no recuerda entre recargas. */
    }
    return value;
  }

  function remove(key) {
    localStorage.removeItem(key);
  }

  /* ======================================================
     SESIÓN  (tabla USUARIO)
     ====================================================== */

  function getUser() {
    return read('simul.user', null);
  }

  function setUser(user) {
    return write('simul.user', user);
  }

  function logout() {
    remove('simul.user');
  }

  /** Perfiles de demostración que expone la pantalla de login. */
  function roleUsers() {
    return window.SIMUL_ROLE_USERS || {};
  }

  /**
   * Inicia sesión con uno de los perfiles de demostración.
   * Guarda una copia del usuario para que la interfaz pueda
   * trabajar sin volver a preguntar al servidor.
   */
  function login(role) {
    const user = roleUsers()[role];
    if (!user) return null;

    return setUser({
      name: user.name,
      email: user.email,
      role: user.role,
      avatar: user.avatar,
      points: user.points,
      level: user.level,
      badges: user.badges.slice(),
      description: user.description
    });
  }

  /**
   * Registra una cuenta nueva. Solo la guarda como pendiente:
   * abrir sesión tiene que pasar antes por el login.
   */
  function register(user) {
    const pendientes = read('simul.pendingUsers', []);

    pendientes.push(Object.assign(
      { id: 'u' + Date.now(), points: 0, level: 1, badges: [] },
      user
    ));

    write('simul.pendingUsers', pendientes);
    return user;
  }

  function getPendingUsers() {
    return read('simul.pendingUsers', []);
  }

  function updateUser(patch) {
    const current = getUser();
    if (!current) return null;
    return setUser(Object.assign({}, current, patch));
  }

  /** Ruta del dashboard según el rol (RF-USR-02). */
  function dashboardPath(role) {
    if (role === 'student') return '/dashboard/estudiante';
    if (role === 'teacher') return '/dashboard/docente';
    if (role === 'admin')   return '/dashboard/admin';
    return '/';
  }

  /* ======================================================
     FAVORITOS  (tabla FAVORITO)
     ====================================================== */

  function getFavorites() {
    return read('simul.favorites', null);
  }

  /** Sin sesión todavía no hay lista: se usa una semilla. */
  function initFavorites(seed) {
    if (getFavorites() === null) {
      write('simul.favorites', seed);
    }
    return getFavorites();
  }

  function isFavorite(id) {
    const list = getFavorites() || [];
    return list.indexOf(String(id)) !== -1;
  }

  function toggleFavorite(id) {
    const list = (getFavorites() || []).slice();
    const key = String(id);
    const at = list.indexOf(key);

    if (at === -1) {
      list.push(key);
    } else {
      list.splice(at, 1);
    }

    write('simul.favorites', list);
    return at === -1;
  }

  function removeFavorite(id) {
    write('simul.favorites',
          (getFavorites() || []).filter(x => x !== String(id)));
  }

  /* ======================================================
     CONTENIDO  (tabla CONTENIDO)
     Copia editable del catálogo que llega desde el servidor.
     Permite que altas, bajas y estados sobrevivan a la
     recarga sin tocar la base de datos.
     ====================================================== */

  function initContent(seed) {
    if (read('simul.content', null) === null) {
      write('simul.content', seed);
    }
    return getContent();
  }

  function getContent() {
    return read('simul.content', []);
  }

  function findContent(id) {
    return getContent().find(c => c.id === String(id)) || null;
  }

  function upsertContent(item) {
    const list = getContent();
    const at = list.findIndex(c => c.id === String(item.id));

    if (at === -1) {
      list.unshift(item);
    } else {
      list[at] = Object.assign({}, list[at], item);
    }

    write('simul.content', list);
    return item;
  }

  function setContentStatus(id, status) {
    return upsertContent({ id: String(id), status: status });
  }

  function deleteContent(id) {
    write('simul.content',
          getContent().filter(c => c.id !== String(id)));
  }

  /* ======================================================
     BANDEJA DE VALIDACIÓN  (CONTENIDO.estado)
     ====================================================== */

  function initQueue(seed) {
    if (read('simul.queue', null) === null) {
      write('simul.queue', seed);
    }
    return getQueue();
  }

  function getQueue() {
    return read('simul.queue', []);
  }

  function dropFromQueue(id) {
    write('simul.queue', getQueue().filter(i => i.id !== String(id)));
  }

  /* ======================================================
     COMENTARIOS  (tabla COMENTARIO)
     `parentId` es la FK autoreferenciada que arma los hilos.
     ====================================================== */

  function initComments(seed) {
    if (read('simul.comments', null) === null) {
      write('simul.comments', seed);
    }
    return getComments();
  }

  function getComments(contentId) {
    const all = read('simul.comments', []);
    return all.filter(c => c.contentId === String(contentId));
  }

  function addComment(contentId, author, text, parentId) {
    const all = read('simul.comments', []);
    const comment = {
      id: 'c' + Date.now(),
      contentId: String(contentId),
      author: author,
      text: text,
      time: 'Ahora',
      parentId: parentId || null
    };
    all.unshift(comment);
    write('simul.comments', all);
    return comment;
  }

  /* ======================================================
     REACCIONES  (tabla REACCION)
     ====================================================== */

  function initReactions(seed) {
    if (read('simul.reactions', null) === null) {
      write('simul.reactions', seed);
    }
    return getReactions();
  }

  function getReactions(contentId) {
    return read('simul.reactions', {})[String(contentId)] ||
           { emoji: '👏', count: 0, reacted: false };
  }

  function toggleReaction(contentId) {
    const all = read('simul.reactions', {});
    const key = String(contentId);
    const current = all[key] || { emoji: '👏', count: 0, reacted: false };

    const next = {
      emoji: current.emoji,
      count: current.reacted
        ? Math.max(current.count - 1, 0)
        : current.count + 1,
      reacted: !current.reacted
    };

    all[key] = next;
    write('simul.reactions', all);
    return next;
  }

  /* ======================================================
     PROPUESTAS DE ESTUDIANTES
     ====================================================== */

  function initProposals() {
    if (read('simul.proposals', null) === null) {
      write('simul.proposals', []);
    }
    return getProposals();
  }

  function getProposals() {
    return read('simul.proposals', []);
  }

  function getProposalsByTeacher(teacherId) {
    return getProposals().filter(p => p.teacherId === teacherId);
  }

  function addProposal(data) {
    const list = getProposals();
    const proposal = Object.assign({
      id: 'prop-' + Date.now(),
      status: 'pendiente',
      createdAt: new Date().toISOString()
    }, data);

    list.unshift(proposal);
    write('simul.proposals', list);
    return proposal;
  }

  function updateProposalStatus(id, status) {
    const list = getProposals().map(p =>
      p.id === id ? Object.assign({}, p, { status: status }) : p
    );
    write('simul.proposals', list);
  }

  /* ======================================================
     USUARIOS DEL SISTEMA  (tabla USUARIO)
     ====================================================== */

  function initUsers(seed) {
    if (read('simul.users', null) === null) {
      write('simul.users', seed);
    }
    return getUsers();
  }

  function getUsers() {
    return read('simul.users', []);
  }

  function setUserRole(id, role) {
    write('simul.users', getUsers().map(u =>
      u.id === String(id) ? Object.assign({}, u, { role: role }) : u
    ));
  }

  function toggleUserActive(id) {
    write('simul.users', getUsers().map(u =>
      u.id === String(id)
        ? Object.assign({}, u, { active: !u.active })
        : u
    ));
  }

  /* ======================================================
     UTILIDADES
     ====================================================== */

  /** Reinicia todo el estado simulado (botón de demo). */
  function reset() {
    [
      'simul.user', 'simul.favorites', 'simul.content', 'simul.queue',
      'simul.comments', 'simul.reactions', 'simul.proposals', 'simul.users',
      'simul.pendingUsers'
    ].forEach(remove);
  }

  return {
    read, write, remove, reset,
    getUser, setUser, logout, updateUser, dashboardPath,
    login, register, getPendingUsers, roleUsers,
    getFavorites, initFavorites, isFavorite, toggleFavorite, removeFavorite,
    initContent, getContent, findContent, upsertContent,
    setContentStatus, deleteContent,
    initQueue, getQueue, dropFromQueue,
    initComments, getComments, addComment,
    initReactions, getReactions, toggleReaction,
    initProposals, getProposals, getProposalsByTeacher,
    addProposal, updateProposalStatus,
    initUsers, getUsers, setUserRole, toggleUserActive
  };
})();
