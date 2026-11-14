-- ============================================================
-- SIMUL · Museo Digital Interactivo
-- DDL MySQL 8.4 — Modelo Entidad-Relación (25 tablas)
-- Fuente: diagrama proyectosimul(desenredado).drawio
-- Base: simul_db (definida en docker-compose.yml)
-- ============================================================

CREATE DATABASE IF NOT EXISTS simul_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE simul_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. ROL
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rol (
  id_rol      INT AUTO_INCREMENT PRIMARY KEY,
  nombre      ENUM('estudiante','docente','admin','egresado') NOT NULL,
  descripcion VARCHAR(255) NULL,
  UNIQUE KEY uq_rol_nombre (nombre)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. NIVEL (catálogo de gamificación — RF-GAM-01)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nivel (
  id_nivel    INT AUTO_INCREMENT PRIMARY KEY,
  numero      TINYINT NOT NULL,
  nombre      VARCHAR(40) NOT NULL,
  puntos_min  INT NOT NULL,
  puntos_max  INT NOT NULL,
  UNIQUE KEY uq_nivel_numero (numero)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. USUARIO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
  id_usuario       INT AUTO_INCREMENT PRIMARY KEY,
  id_rol           INT NOT NULL,
  id_nivel         INT NOT NULL DEFAULT 1,
  nombre           VARCHAR(120) NOT NULL,
  correo           VARCHAR(180) NOT NULL,
  password_hash    VARCHAR(255) NOT NULL,
  foto             VARCHAR(255) NULL,
  biografia        TEXT NULL,
  programa_cohorte VARCHAR(120) NULL,
  estado           TINYINT(1) NOT NULL DEFAULT 1,
  puntos_total     INT NOT NULL DEFAULT 0,
  fecha_registro   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_usuario_correo (correo),
  KEY idx_usuario_puntos (puntos_total),
  CONSTRAINT fk_usuario_rol
    FOREIGN KEY (id_rol) REFERENCES rol (id_rol)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_usuario_nivel
    FOREIGN KEY (id_nivel) REFERENCES nivel (id_nivel)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. INSIGNIA (BADGES_CATALOG)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS insignia (
  id_insig          INT AUTO_INCREMENT PRIMARY KEY,
  nombre            VARCHAR(60) NOT NULL,
  icono             VARCHAR(8) NOT NULL,
  puntos_requeridos INT NOT NULL,
  UNIQUE KEY uq_insignia_nombre (nombre)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. USUARIO_INSIGNIA (N:M)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario_insignia (
  id_usuario     INT NOT NULL,
  id_insig       INT NOT NULL,
  fecha_otorgada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usuario, id_insig),
  CONSTRAINT fk_usuinsig_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_usuinsig_insignia
    FOREIGN KEY (id_insig) REFERENCES insignia (id_insig)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. CONTENIDO (núcleo — 7 tipos en herencia 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contenido (
  id_contenido  INT AUTO_INCREMENT PRIMARY KEY,
  tipo          ENUM('acontecimiento','premio','proyecto',
                     'avance_investigacion','evento','noticia',
                     'hall') NOT NULL,
  titulo        VARCHAR(200) NOT NULL,
  categoria     VARCHAR(80) NOT NULL,
  id_autor      INT NOT NULL,
  estado        ENUM('pendiente','publicado','rechazado')
                  NOT NULL DEFAULT 'pendiente',
  observaciones TEXT NULL,
  id_validador  INT NULL,
  fec_crea      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fec_valid     DATETIME NULL,
  KEY idx_contenido_estado (estado),
  KEY idx_contenido_tipo (tipo),
  KEY idx_contenido_categoria (categoria),
  KEY idx_contenido_fec_crea (fec_crea),
  CONSTRAINT fk_contenido_autor
    FOREIGN KEY (id_autor) REFERENCES usuario (id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_contenido_validador
    FOREIGN KEY (id_validador) REFERENCES usuario (id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. ACONTECIMIENTO (subtipo 1:1 — PK compartida)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS acontecimiento (
  id_contenido INT PRIMARY KEY,
  anio         YEAR NOT NULL,
  descripcion  TEXT NOT NULL,
  KEY idx_acontecimiento_anio (anio),
  CONSTRAINT fk_acont_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 8. PREMIO (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS premio (
  id_contenido INT PRIMARY KEY,
  anio         YEAR NOT NULL,
  lugar        VARCHAR(150) NULL,
  descripcion  TEXT NOT NULL,
  CONSTRAINT fk_premio_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 9. GRUPO_INVESTIGACION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grupo_investigacion (
  id_grupo    INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(120) NOT NULL,
  tipo        ENUM('semillero','grupo') NOT NULL,
  descripcion TEXT NULL,
  id_lider    INT NULL,
  UNIQUE KEY uq_grupo_nombre (nombre),
  CONSTRAINT fk_grupo_lider
    FOREIGN KEY (id_lider) REFERENCES usuario (id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 10. AVANCE_INVESTIGACION (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS avance_investigacion (
  id_contenido INT PRIMARY KEY,
  tipo         ENUM('publicacion','patente','software') NOT NULL,
  anio         YEAR NOT NULL,
  referencia   VARCHAR(255) NULL,
  id_grupo     INT NULL,
  KEY idx_avance_anio (anio),
  CONSTRAINT fk_avance_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_avance_grupo
    FOREIGN KEY (id_grupo) REFERENCES grupo_investigacion (id_grupo)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 11. PROYECTO (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proyecto (
  id_contenido       INT PRIMARY KEY,
  anio               YEAR NOT NULL,
  linea_invest       VARCHAR(150) NULL,
  descripcion        TEXT NOT NULL,
  resultados_impacto TEXT NULL,
  id_asesor          INT NULL,
  KEY idx_proyecto_anio (anio),
  CONSTRAINT fk_proyecto_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_proyecto_asesor
    FOREIGN KEY (id_asesor) REFERENCES usuario (id_usuario)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 12. EVENTO (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evento (
  id_contenido INT PRIMARY KEY,
  fecha_evento DATE NOT NULL,
  lugar        VARCHAR(150) NULL,
  objetivo     VARCHAR(255) NULL,
  CONSTRAINT fk_evento_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 13. NOTICIA (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS noticia (
  id_contenido       INT PRIMARY KEY,
  contenido          TEXT NOT NULL,
  fecha_publicacion  DATE NOT NULL,
  CONSTRAINT fk_noticia_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 14. HALL_FAMA (subtipo 1:1)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hall_fama (
  id_contenido INT PRIMARY KEY,
  categoria    ENUM('Docente','Egresado','Investigador',
                    'Estudiante') NOT NULL,
  biografia    TEXT NOT NULL,
  id_usuario   INT NOT NULL,
  CONSTRAINT fk_hall_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_hall_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 15. TECNOLOGIA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tecnologia (
  id_tec   INT AUTO_INCREMENT PRIMARY KEY,
  nombre   VARCHAR(80) NOT NULL,
  UNIQUE KEY uq_tecnologia_nombre (nombre)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 16. PROYECTO_TECNOLOGIA (N:M proyecto ↔ tecnología)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proyecto_tecnologia (
  id_proyecto INT NOT NULL,
  id_tec      INT NOT NULL,
  PRIMARY KEY (id_proyecto, id_tec),
  CONSTRAINT fk_proytec_proyecto
    FOREIGN KEY (id_proyecto) REFERENCES proyecto (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_proytec_tecnologia
    FOREIGN KEY (id_tec) REFERENCES tecnologia (id_tec)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 17. PREMIO_HALL (N:M premio ↔ hall de la fama)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS premio_hall (
  id_premio INT NOT NULL,
  id_hall   INT NOT NULL,
  PRIMARY KEY (id_premio, id_hall),
  CONSTRAINT fk_premiohall_premio
    FOREIGN KEY (id_premio) REFERENCES premio (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_premiohall_hall
    FOREIGN KEY (id_hall) REFERENCES hall_fama (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 18. EVIDENCIA (RNF-ACC-01: alt_text obligatorio al adjuntar)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evidencia (
  id_evid      INT AUTO_INCREMENT PRIMARY KEY,
  id_contenido INT NOT NULL,
  tipo         ENUM('foto','video','doc') NOT NULL,
  url_archivo  VARCHAR(500) NOT NULL,
  alt_text     VARCHAR(255) NULL,
  fecha_subida DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_evidencia_contenido (id_contenido),
  CONSTRAINT fk_evidencia_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 19. COMENTARIO (árbol con respuesta_a)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comentario (
  id_coment    INT AUTO_INCREMENT PRIMARY KEY,
  id_contenido INT NOT NULL,
  id_usuario   INT NOT NULL,
  respuesta_a  INT NULL,
  texto        TEXT NOT NULL,
  fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_comentario_contenido (id_contenido),
  CONSTRAINT fk_comentario_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_comentario_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_comentario_respuesta
    FOREIGN KEY (respuesta_a) REFERENCES comentario (id_coment)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 20. REACCION (UQ usuario + contenido + tipo)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reaccion (
  id_reac       INT AUTO_INCREMENT PRIMARY KEY,
  id_contenido  INT NOT NULL,
  id_usuario    INT NOT NULL,
  tipo_reaccion VARCHAR(16) NOT NULL,
  UNIQUE KEY uq_reaccion_usuario_contenido_tipo
             (id_usuario, id_contenido, tipo_reaccion),
  KEY idx_reaccion_contenido (id_contenido),
  CONSTRAINT fk_reaccion_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_reaccion_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 21. FAVORITO (PK compuesta)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorito (
  id_usuario     INT NOT NULL,
  id_contenido   INT NOT NULL,
  fecha_guardado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usuario, id_contenido),
  CONSTRAINT fk_favorito_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_favorito_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 22. NOTIFICACION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notificacion (
  id_notif     INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario   INT NOT NULL,
  id_contenido INT NULL,
  tipo         VARCHAR(40) NOT NULL,
  mensaje      VARCHAR(255) NOT NULL,
  leida        TINYINT(1) NOT NULL DEFAULT 0,
  fecha_envio  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_notif_usuario_leida (id_usuario, leida),
  CONSTRAINT fk_notif_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_notif_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 23. VALIDACION_LOG (RF-SEG-04: trazabilidad de decisiones)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS validacion_log (
  id_log        INT AUTO_INCREMENT PRIMARY KEY,
  id_contenido  INT NOT NULL,
  id_admin      INT NOT NULL,
  accion        ENUM('aprueba','rechaza') NOT NULL,
  observaciones TEXT NULL,
  fecha_decision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_vlog_contenido (id_contenido),
  CONSTRAINT fk_vlog_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_vlog_admin
    FOREIGN KEY (id_admin) REFERENCES usuario (id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 24. HISTORIAL_PUNTOS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historial_puntos (
  id_mov       INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario   INT NOT NULL,
  id_contenido INT NULL,
  puntos       INT NOT NULL,
  motivo       VARCHAR(150) NOT NULL,
  fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_hist_usuario_fecha (id_usuario, fecha),
  CONSTRAINT fk_hist_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_hist_contenido
    FOREIGN KEY (id_contenido) REFERENCES contenido (id_contenido)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 25. PROYECTO_INTEGRANTE (N:M proyecto ↔ usuario)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proyecto_integrante (
  id_proyecto     INT NOT NULL,
  id_usuario      INT NOT NULL,
  rol_en_proyecto VARCHAR(80) NULL,
  PRIMARY KEY (id_proyecto, id_usuario),
  CONSTRAINT fk_proyint_proyecto
    FOREIGN KEY (id_proyecto) REFERENCES proyecto (id_contenido)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_proyint_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- VISTAS (las "consultas guardadas" del modelo: no son tablas)
-- ============================================================

-- Bandeja de validación del administrador (RF-VAL-01)
CREATE OR REPLACE VIEW v_bandeja_validacion AS
  SELECT c.id_contenido,
         c.titulo,
         c.tipo,
         c.categoria,
         c.fec_crea,
         u.nombre AS autor,
         (SELECT e.url_archivo
            FROM evidencia e
           WHERE e.id_contenido = c.id_contenido
             AND e.tipo = 'foto'
           LIMIT 1) AS imagen
    FROM contenido c
    JOIN usuario u ON u.id_usuario = c.id_autor
   WHERE c.estado = 'pendiente'
   ORDER BY c.fec_crea DESC;

-- Ranking de gamificación (RF-GAM-03)
CREATE OR REPLACE VIEW v_ranking AS
  SELECT u.id_usuario,
         u.nombre,
         u.foto,
         u.puntos_total,
         n.numero AS nivel,
         n.nombre AS nivel_nombre,
         (SELECT COUNT(*)
            FROM usuario_insignia ui
           WHERE ui.id_usuario = u.id_usuario) AS insignias
    FROM usuario u
    JOIN nivel n ON n.id_nivel = u.id_nivel
   WHERE u.estado = 1
   ORDER BY u.puntos_total DESC;
