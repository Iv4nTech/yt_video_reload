from datetime import datetime, timezone

from estadisticas.proveedor_estadistica import ProveedorEstadistica


class EstadisticaDias(ProveedorEstadistica):
    """Calcula cuántos días han pasado desde que se publicó el vídeo."""

    def obtener_clave(self) -> str:
        return "dias"

    def obtener_valor(self, cliente_youtube, video) -> int:
        fecha_publicacion = cliente_youtube.obtener_fecha_publicacion(video.id_video)
        dias_transcurridos = (datetime.now(timezone.utc) - fecha_publicacion).days
        return dias_transcurridos
