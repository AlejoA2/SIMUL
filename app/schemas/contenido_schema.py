from marshmallow import (
    Schema,
    fields,
    validate
)


# ------------------------------------------------------------
# ENTRADA
# ------------------------------------------------------------

class ContenidoCreateSchema(Schema):

    titulo = fields.Str(
        required=True,
        validate=validate.Length(
            min=3,
            max=200
        )
    )

    tipo = fields.Str(
        required=True,
        validate=validate.OneOf([
            "acontecimiento",
            "premio",
            "proyecto",
            "avance_investigacion",
            "evento",
            "noticia",
            "hall",
        ])
    )

    categoria = fields.Str(
        required=True,
        validate=validate.Length(
            min=2,
            max=80
        )
    )

    anio = fields.Int(
        required=True,
        validate=validate.Range(
            min=1900,
            max=2100
        )
    )

    descripcion = fields.Str(
        required=True,
        validate=validate.Length(
            min=10
        )
    )

    # Campos adicionales según el subtipo (opcionales).
    lugar = fields.Str(allow_none=True)

    linea_invest = fields.Str(allow_none=True)

    resultados_impacto = fields.Str(allow_none=True)

    id_asesor = fields.Int(allow_none=True)

    tipo_avance = fields.Str(
        validate=validate.OneOf([
            "publicacion",
            "patente",
            "software",
        ])
    )

    referencia = fields.Str(allow_none=True)

    id_grupo = fields.Int(allow_none=True)

    fecha_evento = fields.Date(allow_none=True)

    objetivo = fields.Str(allow_none=True)

    categoria_hall = fields.Str(
        validate=validate.OneOf([
            "Docente",
            "Egresado",
            "Investigador",
            "Estudiante",
        ])
    )

    # Relaciones simples recibidas como texto.
    tecnologias = fields.List(
        fields.Str(),
        load_default=list
    )

    participantes = fields.List(
        fields.Str(),
        load_default=list
    )

    # Imagen principal (RNF-ACC-01: alt_text obligatorio
    # cuando tipo == "foto").
    imagen = fields.Str(allow_none=True)

    alt_text = fields.Str(allow_none=True)


class ContenidoUpdateSchema(Schema):

    titulo = fields.Str(
        validate=validate.Length(
            min=3,
            max=200
        )
    )

    categoria = fields.Str(
        validate=validate.Length(
            min=2,
            max=80
        )
    )

    descripcion = fields.Str()

    anio = fields.Int(
        validate=validate.Range(
            min=1900,
            max=2100
        )
    )


class EvidenciaCreateSchema(Schema):

    tipo = fields.Str(
        required=True,
        validate=validate.OneOf([
            "foto",
            "video",
            "doc",
        ])
    )

    url_archivo = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=500
        )
    )

    # RNF-ACC-01: obligatorio para imágenes.
    alt_text = fields.Str(allow_none=True)


class ComentarioCreateSchema(Schema):

    texto = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=2000
        )
    )

    respuesta_a = fields.Int(allow_none=True)


class ReaccionSchema(Schema):

    tipo_reaccion = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=16
        )
    )


# ------------------------------------------------------------
# SALIDA
# ------------------------------------------------------------

class AutorSchema(Schema):

    id_usuario = fields.Int()

    nombre = fields.Str()

    foto = fields.Str(allow_none=True)


class EvidenciaSchema(Schema):

    id_evid = fields.Int()

    tipo = fields.Str()

    url_archivo = fields.Str()

    alt_text = fields.Str(allow_none=True)

    fecha_subida = fields.DateTime()


class ComentarioSchema(Schema):

    id_coment = fields.Int()

    id_contenido = fields.Int()

    id_usuario = fields.Int()

    respuesta_a = fields.Int(allow_none=True)

    texto = fields.Str()

    fecha = fields.DateTime()

    autor = fields.Nested(AutorSchema)


class ReaccionConteoSchema(Schema):

    tipo_reaccion = fields.Str()

    total = fields.Int()

    reaccionado = fields.Bool()


class ContenidoSchema(Schema):

    id_contenido = fields.Int()

    tipo = fields.Str()

    titulo = fields.Str()

    categoria = fields.Str()

    estado = fields.Str()

    observaciones = fields.Str(allow_none=True)

    fec_crea = fields.DateTime()

    fec_valid = fields.DateTime(allow_none=True)

    autor = fields.Nested(AutorSchema)

    validador = fields.Nested(AutorSchema, allow_none=True)
