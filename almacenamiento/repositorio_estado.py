import json
from pathlib import Path


class RepositorioEstado:
    """Guarda en disco el último valor conocido de la estadística de cada vídeo.

    Se usa para comparar en cada ejecución del cron si el valor ha cambiado
    de verdad y así evitar llamadas innecesarias de actualización a la API.
    """

    def __init__(self, ruta_archivo: str):
        self._ruta_archivo = Path(ruta_archivo)
        self._estado = self._cargar()

    def obtener_ultimo_valor(self, id_video: str):
        return self._estado.get(id_video)

    def guardar_valor(self, id_video: str, valor) -> None:
        self._estado[id_video] = valor
        self._guardar()

    def _cargar(self) -> dict:
        if self._ruta_archivo.exists():
            return json.loads(self._ruta_archivo.read_text(encoding="utf-8"))
        return {}

    def _guardar(self) -> None:
        self._ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self._ruta_archivo.write_text(
            json.dumps(self._estado, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
