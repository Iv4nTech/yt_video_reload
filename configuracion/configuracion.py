import json
from pathlib import Path

from entidades.video import Video


class Configuracion:
    """Carga la configuración del proyecto (credenciales, rutas y vídeos señalados) desde config.json."""

    def __init__(self, ruta_config: str = "config.json"):
        datos = json.loads(Path(ruta_config).read_text(encoding="utf-8"))

        self.ruta_secreto_cliente: str = datos["credenciales"]["ruta_secreto_cliente"]
        self.ruta_token: str = datos["credenciales"]["ruta_token"]
        self.ruta_estado: str = datos.get("ruta_estado", "almacenamiento/estado.json")
        self.ruta_fuente: str | None = datos.get("ruta_fuente")
        self.videos: list[Video] = [self._construir_video(v) for v in datos["videos"]]

    def _construir_video(self, datos_video: dict) -> Video:
        return Video(
            id_video=datos_video["id_video"],
            tipo_estadistica=datos_video["tipo_estadistica"],
            plantilla_titulo=datos_video["plantilla_titulo"],
            texto_miniatura=datos_video["texto_miniatura"],
        )
