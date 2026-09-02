from almacenamiento.repositorio_estado import RepositorioEstado
from configuracion.configuracion import Configuracion
from entidades.video import Video
from estadisticas.fabrica_estadistica import FabricaEstadistica
from miniatura.generador_miniatura import GeneradorMiniatura
from youtube.autenticador_youtube import AutenticadorYouTube
from youtube.cliente_youtube import ClienteYouTube


class Orquestador:
    """Coordina el flujo principal: por cada vídeo señalado, comprueba si su
    estadística ha cambiado y, solo en ese caso, regenera la miniatura y
    actualiza el título y la miniatura en YouTube.
    """

    def __init__(self, configuracion: Configuracion):
        self._configuracion = configuracion
        self._repositorio_estado = RepositorioEstado(configuracion.ruta_estado)
        self._generador_miniatura = GeneradorMiniatura(configuracion.ruta_fuente)
        self._cliente_youtube = self._crear_cliente_youtube(configuracion)

    def ejecutar(self) -> None:
        for video in self._configuracion.videos:
            self._procesar_video(video)

    def _crear_cliente_youtube(self, configuracion: Configuracion) -> ClienteYouTube:
        autenticador = AutenticadorYouTube(configuracion.ruta_secreto_cliente, configuracion.ruta_token)
        return ClienteYouTube(autenticador.obtener_credenciales())

    def _procesar_video(self, video: Video) -> None:
        proveedor = FabricaEstadistica.crear(video.tipo_estadistica)
        valor_actual = proveedor.obtener_valor(self._cliente_youtube, video)
        valor_anterior = self._repositorio_estado.obtener_ultimo_valor(video.id_video)

        if valor_actual == valor_anterior:
            print(f"[{video.id_video}] Sin cambios ({proveedor.obtener_clave()}={valor_actual}). No se actualiza.")
            return

        print(f"[{video.id_video}] Cambio detectado en {proveedor.obtener_clave()}: {valor_anterior} -> {valor_actual}")
        self._actualizar_video(video, valor_actual)
        self._repositorio_estado.guardar_valor(video.id_video, valor_actual)

    def _actualizar_video(self, video: Video, valor_actual) -> None:
        titulo_nuevo = video.plantilla_titulo.format(valor=valor_actual)
        texto_miniatura = video.texto_miniatura.format(valor=valor_actual)
        ruta_miniatura_generada = f"salida/{video.id_video}.png"

        self._generador_miniatura.generar(texto_miniatura, ruta_miniatura_generada)
        self._cliente_youtube.actualizar_titulo(video.id_video, titulo_nuevo)
        self._cliente_youtube.actualizar_miniatura(video.id_video, ruta_miniatura_generada)

        print(f"[{video.id_video}] Actualizado -> título: '{titulo_nuevo}'")
