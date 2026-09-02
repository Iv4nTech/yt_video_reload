from abc import ABC, abstractmethod


class ProveedorEstadistica(ABC):
    """Define cómo se obtiene una estadística concreta de un vídeo (días, visitas, likes...)."""

    @abstractmethod
    def obtener_clave(self) -> str:
        """Nombre corto de la estadística, usado en el estado guardado y en los logs."""

    @abstractmethod
    def obtener_valor(self, cliente_youtube, video):
        """Consulta y devuelve el valor actual de la estadística para el vídeo dado."""
