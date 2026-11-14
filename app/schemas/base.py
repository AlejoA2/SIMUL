"""
Serialización de salidas con pydantic.

Los models de salida leen atributos de los modelos ORM
(from_attributes) y la interfaz `Esquema.dump()` conserva
la API que ya usan los servicios (igual que marshmallow).
"""

from pydantic import BaseModel, ConfigDict


class ModeloSalida(BaseModel):

    """Base de los modelos de salida: acepta instancias de
    los modelos ORM y serializa a tipos JSON."""

    model_config = ConfigDict(from_attributes=True)


class Esquema:

    """Serializador envolvente para las capas de servicio:
    `esquema.dump(objeto)` o `dump(lista, many=True)`."""

    modelo: type[BaseModel] | None = None

    def dump(self, obj, many=False):

        if many:

            return [self._uno(o) for o in obj]

        return self._uno(obj)

    def _uno(self, obj):

        # marshmallow permitía dump(None) → None; aquí vale
        # lo mismo (p.ej. validador de contenido pendiente).
        if obj is None:

            return None

        return (
            self.modelo
            .model_validate(obj)
            .model_dump(mode="json")
        )
