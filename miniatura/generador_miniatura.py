from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class GeneradorMiniatura:
    """Genera una miniatura con fondo negro liso y el texto de la estadística en blanco, centrado.

    El tamaño de letra no es fijo: se calcula probando tamaños cada vez más
    grandes hasta que el texto ocupa una proporción objetivo del ancho (y
    sin pasarse de una proporción del alto) de la miniatura. Así "41 DÍAS" y
    "12345 VISITAS" se ven igual de grandes en proporción, y el texto sigue
    siendo legible aunque YouTube muestre la miniatura pequeña.
    """

    ANCHO_MINIATURA = 1280
    ALTO_MINIATURA = 720

    def __init__(
        self,
        ruta_fuente: str | None = None,
        proporcion_ancho: float = 0.85,
        proporcion_alto: float = 0.5,
    ):
        self._ruta_fuente = ruta_fuente
        self._proporcion_ancho = proporcion_ancho
        self._proporcion_alto = proporcion_alto

    def generar(self, texto: str, ruta_salida: str) -> str:
        imagen = Image.new("RGB", (self.ANCHO_MINIATURA, self.ALTO_MINIATURA), color="black")
        dibujante = ImageDraw.Draw(imagen)

        tamano_fuente = self._calcular_tamano_ajustado(dibujante, imagen, texto)
        fuente = self._cargar_fuente(tamano_fuente)

        posicion = self._calcular_posicion_centrada(imagen, dibujante, texto, fuente)
        dibujante.text(posicion, texto, font=fuente, fill="white")

        self._guardar_imagen(imagen, ruta_salida)
        return ruta_salida

    def _calcular_tamano_ajustado(self, dibujante, imagen: Image.Image, texto: str) -> int:
        ancho_objetivo = imagen.width * self._proporcion_ancho
        alto_objetivo = imagen.height * self._proporcion_alto

        tamano_minimo = 10
        incremento = 5

        tamano = tamano_minimo
        ancho_texto, alto_texto = self._medir_texto(dibujante, texto, self._cargar_fuente(tamano))

        while ancho_texto < ancho_objetivo and alto_texto < alto_objetivo:
            tamano += incremento
            ancho_texto, alto_texto = self._medir_texto(dibujante, texto, self._cargar_fuente(tamano))

        return max(tamano_minimo, tamano - incremento)

    def _medir_texto(self, dibujante, texto: str, fuente) -> tuple[int, int]:
        caja_texto = dibujante.textbbox((0, 0), texto, font=fuente)
        ancho_texto = caja_texto[2] - caja_texto[0]
        alto_texto = caja_texto[3] - caja_texto[1]
        return ancho_texto, alto_texto

    def _cargar_fuente(self, tamano: int) -> ImageFont.FreeTypeFont:
        if self._ruta_fuente:
            return ImageFont.truetype(self._ruta_fuente, tamano)
        return ImageFont.load_default(size=tamano)

    def _calcular_posicion_centrada(self, imagen, dibujante, texto, fuente) -> tuple[int, int]:
        ancho_imagen, alto_imagen = imagen.size
        ancho_texto, alto_texto = self._medir_texto(dibujante, texto, fuente)

        return (
            (ancho_imagen - ancho_texto) // 2,
            (alto_imagen - alto_texto) // 2,
        )

    def _guardar_imagen(self, imagen: Image.Image, ruta_salida: str) -> None:
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        imagen.save(ruta_salida)
