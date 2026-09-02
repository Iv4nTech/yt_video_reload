from estadisticas.proveedor_estadistica import ProveedorEstadistica


class EstadisticaLikes(ProveedorEstadistica):
    """Obtiene el número actual de 'me gusta' del vídeo."""

    def obtener_clave(self) -> str:
        return "likes"

    def obtener_valor(self, cliente_youtube, video) -> int:
        return cliente_youtube.obtener_likes(video.id_video)
