from estadisticas.proveedor_estadistica import ProveedorEstadistica


class EstadisticaVisitas(ProveedorEstadistica):
    """Obtiene el número actual de visualizaciones del vídeo."""

    def obtener_clave(self) -> str:
        return "visitas"

    def obtener_valor(self, cliente_youtube, video) -> int:
        return cliente_youtube.obtener_visualizaciones(video.id_video)
