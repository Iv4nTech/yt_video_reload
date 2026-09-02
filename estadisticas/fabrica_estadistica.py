from estadisticas.estadistica_dias import EstadisticaDias
from estadisticas.estadistica_likes import EstadisticaLikes
from estadisticas.estadistica_visitas import EstadisticaVisitas
from estadisticas.proveedor_estadistica import ProveedorEstadistica


class FabricaEstadistica:
    """Crea el proveedor de estadística adecuado a partir de su nombre en la configuración.

    Añadir una estadística nueva solo requiere crear su clase en este paquete
    y registrarla aquí, sin tocar el resto del proyecto.
    """

    _proveedores_disponibles = {
        "dias": EstadisticaDias,
        "visitas": EstadisticaVisitas,
        "likes": EstadisticaLikes,
    }

    @classmethod
    def crear(cls, tipo_estadistica: str) -> ProveedorEstadistica:
        clase_proveedor = cls._proveedores_disponibles.get(tipo_estadistica)
        if clase_proveedor is None:
            disponibles = ", ".join(cls._proveedores_disponibles)
            raise ValueError(
                f"Tipo de estadística '{tipo_estadistica}' desconocido. "
                f"Opciones disponibles: {disponibles}"
            )
        return clase_proveedor()
