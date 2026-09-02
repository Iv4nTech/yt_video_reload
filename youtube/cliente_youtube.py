from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class ClienteYouTube:
    """Envuelve las llamadas a la YouTube Data API que necesita el proyecto."""

    def __init__(self, credenciales):
        self._servicio = build("youtube", "v3", credentials=credenciales)

    def obtener_fecha_publicacion(self, id_video: str) -> datetime:
        snippet = self._obtener_snippet(id_video)
        fecha_texto = snippet["publishedAt"]
        return datetime.fromisoformat(fecha_texto.replace("Z", "+00:00"))

    def obtener_visualizaciones(self, id_video: str) -> int:
        estadisticas = self._obtener_estadisticas(id_video)
        return int(estadisticas["viewCount"])

    def obtener_likes(self, id_video: str) -> int:
        estadisticas = self._obtener_estadisticas(id_video)
        return int(estadisticas.get("likeCount", 0))

    def actualizar_titulo(self, id_video: str, nuevo_titulo: str) -> None:
        snippet = self._obtener_snippet(id_video)
        snippet["title"] = nuevo_titulo
        self._servicio.videos().update(
            part="snippet",
            body={"id": id_video, "snippet": snippet},
        ).execute()

    def actualizar_miniatura(self, id_video: str, ruta_imagen: str) -> None:
        self._servicio.thumbnails().set(
            videoId=id_video,
            media_body=MediaFileUpload(ruta_imagen),
        ).execute()

    def _obtener_snippet(self, id_video: str) -> dict:
        respuesta = self._servicio.videos().list(part="snippet", id=id_video).execute()
        return respuesta["items"][0]["snippet"]

    def _obtener_estadisticas(self, id_video: str) -> dict:
        respuesta = self._servicio.videos().list(part="statistics", id=id_video).execute()
        return respuesta["items"][0]["statistics"]
