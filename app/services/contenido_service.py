from datetime import datetime

from app.models.contenido import Contenido
from app.models.contenido_tipos import (
    Acontecimiento,
    Premio,
    Proyecto,
    AvanceInvestigacion,
    Evento,
    Noticia,
    HallFama
)
from app.models.evidencia import Evidencia
from app.models.comentario import Comentario
from app.models.reaccion import Reaccion
from app.models.favorito import Favorito

from app.repositories.contenido_repository import (
    ContenidoRepository
)
from app.repositories.usuario_repository import (
    UsuarioRepository
)
from app.repositories.social_repository import (
    SocialRepository
)
from app.repositories.gamificacion_repository import (
    GamificacionRepository
)

from app.schemas.contenido_schema import (
    ContenidoSchema,
    ComentarioSchema,
    EvidenciaSchema,
    AutorSchema
)

from app.utils.response import (
    success,
    error
)


# Reglas de gamificación (RF-GAM-01).
PUNTOS_COMENTARIO = 10

# Esquemas de salida (los de entrada los valida FastAPI en
# cada ruta y están documentados en Swagger/OpenAPI).
contenido_schema = ContenidoSchema()

comentario_out_schema = ComentarioSchema()

evidencia_out_schema = EvidenciaSchema()

autor_schema = AutorSchema()


class ContenidoService:

    def __init__(self):

        self.repository = ContenidoRepository()

        self.usuarios = UsuarioRepository()

        self.social = SocialRepository()

        self.gamificacion = GamificacionRepository()

    # ========================================================
    # LECTURA
    # ========================================================

    def listar(
        self,
        q=None,
        categoria=None,
        tipo=None,
        anio=None,
        page=1,
        per_page=12
    ):

        paginate = self.repository.get_publicados(
            q=q,
            categoria=categoria,
            tipo=tipo,
            anio=anio,
            page=page,
            per_page=per_page
        )

        return success(
            {
                "items": [
                    self._resumen(c)
                    for c in paginate.items
                ],
                "page": paginate.page,
                "pages": paginate.pages,
                "total": paginate.total,
            }
        )

    def detalle(self, contenido_id, usuario=None):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        # Lo pendiente/rechazado solo lo ven su autor
        # y los administradores.
        es_gestor = usuario is not None and (
            usuario.rol_nombre == "admin"
            or usuario.id_usuario
            == contenido.id_autor
        )

        if contenido.estado != "publicado" and not es_gestor:

            return error(
                "Contenido no encontrado",
                404
            )

        return success(
            self._detalle(contenido, usuario)
        )

    def mis_aportes(self, usuario):

        contenidos = self.repository.get_de_usuario(
            usuario.id_usuario
        )

        return success(
            [
                {
                    "id_contenido": c.id_contenido,
                    "titulo": c.titulo,
                    "tipo": c.tipo,
                    "categoria": c.categoria,
                    "estado": c.estado,
                    "observaciones": c.observaciones,
                    "fec_crea": c.fec_crea.isoformat(),
                    "fec_valid": (
                        c.fec_valid.isoformat()
                        if c.fec_valid else None
                    ),
                }
                for c in contenidos
            ]
        )

    def favoritos(self, usuario):

        contenidos = self.repository.get_favoritos_de(
            usuario.id_usuario
        )

        return success(
            [
                self._resumen(c)
                for c in contenidos
            ]
        )

    # ========================================================
    # ESCRITURA — CREAR (RF-COM-02 / RF-PRP-01)
    # ========================================================

    def crear(self, data, autor):

        # Los campos ya pasaron la validación del esquema
        # pydantic declarado en la ruta (422 en Swagger).
        datos = data

        # Imagen principal: exige alt_text (RNF-ACC-01).
        if datos.get("imagen") and not datos.get("alt_text"):

            return error(
                "alt_text es obligatorio para imágenes",
                422,
                {"alt_text": ["Requerido (RNF-ACC-01)"]}
            )

        contenido = Contenido(
            tipo=datos["tipo"],
            titulo=datos["titulo"],
            categoria=datos["categoria"],
            id_autor=autor.id_usuario,
            estado="pendiente"
        )

        subtipo = self._construir_subtipo(
            datos,
            autor
        )

        # ----------------------------------------------------
        # RELACIONES SIMPLES
        # ----------------------------------------------------

        evidencias = []

        if datos.get("imagen"):

            evidencias.append(
                Evidencia(
                    tipo="foto",
                    url_archivo=datos["imagen"],
                    alt_text=datos.get("alt_text")
                )
            )

        integrantes = []

        for nombre in datos.get("participantes") or []:

            usuario = self._buscar_por_nombre(nombre)

            if usuario:

                integrantes.append(
                    (usuario.id_usuario, "participante")
                )

        self.repository.create_con_subtipo(
            contenido=contenido,
            subtipo=subtipo,
            tecnologias=datos.get("tecnologias") or [],
            integrantes=integrantes,
            evidencias=evidencias
        )

        return success(
            self._detalle(contenido, autor),
            "Contenido creado en estado pendiente",
            201
        )

    def actualizar(
        self,
        contenido_id,
        data,
        usuario
    ):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        if not self._puede_editar(contenido, usuario):

            return error(
                "No autorizado",
                403
            )

        # Solo los campos enviados llegan aquí (la ruta
        # usa model_dump(exclude_unset=True) para PUT).
        datos = data

        if "titulo" in datos:

            contenido.titulo = datos["titulo"]

        if "categoria" in datos:

            contenido.categoria = datos["categoria"]

        subtipo = self._subtipo_de(contenido)

        if subtipo is not None:

            if "descripcion" in datos:

                if hasattr(subtipo, "descripcion"):

                    subtipo.descripcion = datos["descripcion"]

            if "anio" in datos and hasattr(subtipo, "anio"):

                subtipo.anio = datos["anio"]

        self.repository.update(contenido)

        return success(
            self._detalle(contenido, usuario),
            "Contenido actualizado"
        )

    def eliminar(self, contenido_id, usuario):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        if usuario is None or usuario.rol_nombre != "admin":

            return error(
                "Se requiere rol administrador",
                403
            )

        self.repository.delete(contenido)

        return success(
            None,
            "Contenido eliminado"
        )

    # ========================================================
    # EVIDENCIAS (RF-EVD-01)
    # ========================================================

    def agregar_evidencia(
        self,
        contenido_id,
        data,
        usuario
    ):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        if not self._puede_editar(contenido, usuario):

            return error(
                "No autorizado",
                403
            )

        # Validación en la ruta (esquema pydantic).
        datos = data

        # RNF-ACC-01: toda imagen lleva alt_text.
        if datos["tipo"] == "foto" and not datos.get(
            "alt_text"
        ):

            return error(
                "alt_text es obligatorio para imágenes",
                422,
                {"alt_text": ["Requerido (RNF-ACC-01)"]}
            )

        evidencia = Evidencia(
            id_contenido=contenido.id_contenido,
            tipo=datos["tipo"],
            url_archivo=datos["url_archivo"],
            alt_text=datos.get("alt_text")
        )

        self.repository.add_evidencia(evidencia)

        return success(
            evidencia_out_schema.dump(evidencia),
            "Evidencia adjuntada",
            201
        )

    # ========================================================
    # COMENTARIOS (RF-CMT-01)
    # ========================================================

    def listar_comentarios(self, contenido_id):

        comentarios = self.social.get_comentarios(
            contenido_id
        )

        return success(
            comentario_out_schema.dump(
                comentarios,
                many=True
            )
        )

    def comentar(self, contenido_id, data, usuario):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        # Validación en la ruta (esquema pydantic).
        datos = data

        comentario = Comentario(
            id_contenido=contenido.id_contenido,
            id_usuario=usuario.id_usuario,
            respuesta_a=datos.get("respuesta_a"),
            texto=datos["texto"]
        )

        self.social.add_comentario(comentario)

        # Gamificación: +10 por comentar (RF-GAM-01).
        self.gamificacion.registrar_movimiento(
            usuario=usuario,
            puntos=PUNTOS_COMENTARIO,
            motivo=f"Comentario en: {contenido.titulo}",
            contenido_id=contenido.id_contenido
        )

        self._refrescar_gamificacion(usuario)

        self.gamificacion.commit()

        return success(
            comentario_out_schema.dump(comentario),
            "Comentario publicado",
            201
        )

    # ========================================================
    # REACCIONES (RF-REA-01)
    # ========================================================

    def toggle_reaccion(
        self,
        contenido_id,
        data,
        usuario
    ):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        # Validación en la ruta (esquema pydantic).
        datos = data

        existente = self.social.get_reaccion(
            usuario.id_usuario,
            contenido.id_contenido,
            datos["tipo_reaccion"]
        )

        if existente:

            self.social.remove_reaccion(existente)

            reaccionado = False

        else:

            self.social.add_reaccion(
                Reaccion(
                    id_contenido=contenido.id_contenido,
                    id_usuario=usuario.id_usuario,
                    tipo_reaccion=datos["tipo_reaccion"]
                )
            )

            reaccionado = True

        return success(
            {
                "tipo_reaccion": datos["tipo_reaccion"],
                "reaccionado": reaccionado,
                "total": self._conteo_reaccion(
                    contenido.id_contenido,
                    datos["tipo_reaccion"]
                ),
            }
        )

    # ========================================================
    # FAVORITOS (RF-Fav-01)
    # ========================================================

    def toggle_favorito(self, contenido_id, usuario):

        contenido = self.repository.get_by_id(
            contenido_id
        )

        if not contenido:

            return error(
                "Contenido no encontrado",
                404
            )

        existente = self.social.get_favorito(
            usuario.id_usuario,
            contenido.id_contenido
        )

        if existente:

            self.social.remove_favorito(existente)

            favorito = False

        else:

            self.social.add_favorito(
                Favorito(
                    id_usuario=usuario.id_usuario,
                    id_contenido=contenido.id_contenido
                )
            )

            favorito = True

        return success(
            {"es_favorito": favorito}
        )

    # ========================================================
    # ENsamblaje interno
    # ========================================================

    def _resumen(self, contenido):

        """Forma compacta para tarjetas/listados."""

        return {
            "id_contenido": contenido.id_contenido,
            "tipo": contenido.tipo,
            "titulo": contenido.titulo,
            "categoria": contenido.categoria,
            "estado": contenido.estado,
            "fec_crea": contenido.fec_crea.isoformat(),
            "anio": self._anio(contenido),
            "imagen": self._imagen(contenido),
            "descripcion": self._descripcion(contenido),
            "autor": autor_schema.dump(
                contenido.autor
            ),
        }

    def _detalle(self, contenido, usuario):

        """Forma completa para la ficha de contenido."""

        datos = self._resumen(contenido)

        datos["observaciones"] = contenido.observaciones
        datos["fec_valid"] = (
            contenido.fec_valid.isoformat()
            if contenido.fec_valid else None
        )
        datos["validador"] = autor_schema.dump(
            contenido.validador
        )

        # Campos específicos del subtipo.
        subtipo = self._subtipo_de(contenido)

        if subtipo is not None:

            datos["subtipo"] = self._subtipo_dict(
                contenido,
                subtipo
            )

        # Relaciones del ámbito de investigación.
        if contenido.tipo == "proyecto" and subtipo:

            datos["tecnologias"] = [
                t.nombre
                for t in self.repository
                .get_tecnologias_de(subtipo)
            ]

            datos["integrantes"] = [
                {
                    "id_usuario": u.id_usuario,
                    "nombre": u.nombre,
                    "rol_en_proyecto": rol,
                }
                for u, rol in self.repository
                .get_integrantes_de(subtipo)
            ]

        # Social.
        datos["evidencias"] = evidencia_out_schema.dump(
            contenido.evidencias,
            many=True
        )

        datos["comentarios"] = comentario_out_schema.dump(
            contenido.comentarios,
            many=True
        )

        datos["reacciones"] = [
            {
                "tipo_reaccion": tipo,
                "total": total,
                "reaccionado": (
                    usuario is not None
                    and self.social.get_reaccion(
                        usuario.id_usuario,
                        contenido.id_contenido,
                        tipo
                    ) is not None
                ),
            }
            for tipo, total in self.social
            .contar_por_tipo(contenido.id_contenido)
        ]

        datos["es_favorito"] = (
            usuario is not None
            and self.social.get_favorito(
                usuario.id_usuario,
                contenido.id_contenido
            ) is not None
        )

        return datos

    def _subtipo_dict(self, contenido, subtipo):

        if contenido.tipo == "acontecimiento":

            return {
                "anio": subtipo.anio,
                "descripcion": subtipo.descripcion,
            }

        if contenido.tipo == "premio":

            return {
                "anio": subtipo.anio,
                "lugar": subtipo.lugar,
                "descripcion": subtipo.descripcion,
                "premios_vinculados": len(subtipo.halls),
            }

        if contenido.tipo == "proyecto":

            return {
                "anio": subtipo.anio,
                "linea_invest": subtipo.linea_invest,
                "descripcion": subtipo.descripcion,
                "resultados_impacto": (
                    subtipo.resultados_impacto
                ),
                "asesor": (
                    subtipo.asesor.nombre
                    if subtipo.asesor else None
                ),
            }

        if contenido.tipo == "avance_investigacion":

            return {
                "tipo_avance": subtipo.tipo,
                "anio": subtipo.anio,
                "referencia": subtipo.referencia,
                "grupo": (
                    subtipo.grupo.nombre
                    if subtipo.grupo else None
                ),
            }

        if contenido.tipo == "evento":

            return {
                "fecha_evento": (
                    subtipo.fecha_evento.isoformat()
                ),
                "lugar": subtipo.lugar,
                "objetivo": subtipo.objetivo,
            }

        if contenido.tipo == "noticia":

            return {
                "contenido_texto": (
                    subtipo.contenido_texto
                ),
                "fecha_publicacion": (
                    subtipo.fecha_publicacion.isoformat()
                ),
            }

        if contenido.tipo == "hall":

            return {
                "categoria": subtipo.categoria,
                "biografia": subtipo.biografia,
                "persona": autor_schema.dump(
                    subtipo.persona
                ),
                "premios_vinculados": len(subtipo.premios),
            }

        return {}

    def _construir_subtipo(self, datos, autor):

        """Fábrica: crea la fila del subtipo 1:1 según
        el tipo recibido (su PK la pone el repository)."""

        tipo = datos["tipo"]

        if tipo == "acontecimiento":

            return Acontecimiento(
                anio=datos["anio"],
                descripcion=datos["descripcion"]
            )

        if tipo == "premio":

            return Premio(
                anio=datos["anio"],
                lugar=datos.get("lugar"),
                descripcion=datos["descripcion"]
            )

        if tipo == "proyecto":

            return Proyecto(
                anio=datos["anio"],
                linea_invest=datos.get("linea_invest"),
                descripcion=datos["descripcion"],
                resultados_impacto=datos.get(
                    "resultados_impacto"
                ),
                id_asesor=datos.get("id_asesor")
            )

        if tipo == "avance_investigacion":

            return AvanceInvestigacion(
                tipo=datos.get(
                    "tipo_avance",
                    "publicacion"
                ),
                anio=datos["anio"],
                referencia=datos.get("referencia"),
                id_grupo=datos.get("id_grupo")
            )

        if tipo == "evento":

            return Evento(
                fecha_evento=(
                    datos.get("fecha_evento")
                    or datetime.utcnow().date()
                ),
                lugar=datos.get("lugar"),
                objetivo=datos.get("objetivo")
            )

        if tipo == "noticia":

            return Noticia(
                contenido_texto=datos["descripcion"],
                fecha_publicacion=(
                    datetime.utcnow().date()
                )
            )

        if tipo == "hall":

            return HallFama(
                categoria=datos.get(
                    "categoria_hall",
                    "Docente"
                ),
                biografia=datos["descripcion"],
                id_usuario=autor.id_usuario
            )

        return None

    def _subtipo_de(self, contenido):

        mapa = {
            "acontecimiento": contenido.acontecimiento,
            "premio": contenido.premio,
            "proyecto": contenido.proyecto,
            "avance_investigacion": contenido.avance,
            "evento": contenido.evento,
            "noticia": contenido.noticia,
            "hall": contenido.hall,
        }

        return mapa.get(contenido.tipo)

    def _anio(self, contenido):

        """Año común para filtros/listados: cada subtipo
        lo guarda a su manera."""

        subtipo = self._subtipo_de(contenido)

        if subtipo is None:

            return None

        if hasattr(subtipo, "anio"):

            return int(subtipo.anio)

        if contenido.tipo == "evento":

            return subtipo.fecha_evento.year

        if contenido.tipo == "noticia":

            return subtipo.fecha_publicacion.year

        return None

    def _imagen(self, contenido):

        """Imagen principal = primera evidencia de tipo
        foto (el ER no tiene columna image)."""

        for evidencia in contenido.evidencias:

            if evidencia.tipo == "foto":

                return evidencia.url_archivo

        return None

    def _descripcion(self, contenido):

        subtipo = self._subtipo_de(contenido)

        if subtipo is None:

            return None

        if contenido.tipo == "evento":

            return subtipo.objetivo

        if contenido.tipo == "avance_investigacion":

            return subtipo.referencia

        if contenido.tipo == "noticia":

            return subtipo.contenido_texto[:300]

        if hasattr(subtipo, "descripcion"):

            return subtipo.descripcion

        if hasattr(subtipo, "biografia"):

            return subtipo.biografia

        return None

    def _conteo_reaccion(self, contenido_id, tipo):

        for tipo_reaccion, total in (
            self.social.contar_por_tipo(contenido_id)
        ):

            if tipo_reaccion == tipo:

                return total

        return 0

    def _puede_editar(self, contenido, usuario):

        if usuario is None:

            return False

        return (
            usuario.rol_nombre == "admin"
            or usuario.id_usuario == contenido.id_autor
        )

    def _buscar_por_nombre(self, nombre):

        return self.usuarios.get_by_nombre(nombre)

    def _refrescar_gamificacion(self, usuario):

        """Recalcula nivel e insignias tras sumar puntos."""

        nivel = self.gamificacion.get_nivel_por_puntos(
            usuario.puntos_total
        )

        if nivel:

            usuario.id_nivel = nivel.id_nivel

        for insignia in self.gamificacion.get_insignias():

            if (
                insignia.puntos_requeridos
                <= usuario.puntos_total
            ):

                self.gamificacion.otorgar_insignia(
                    usuario,
                    insignia
                )
