from dataclasses import dataclass


@dataclass
class Video:
    """Representa un vídeo de YouTube al que se le va a actualizar el título y la miniatura."""

    id_video: str
    tipo_estadistica: str
    plantilla_titulo: str
    texto_miniatura: str
