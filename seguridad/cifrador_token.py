import os

from cryptography.fernet import Fernet


class CifradorToken:
    """Cifra y descifra el token de YouTube con una clave que vive fuera del
    proyecto (variable de entorno), nunca dentro del propio repositorio.

    Así, aunque alguien copie el disco o el repositorio completo, el fichero
    `token.json` que se guarda ahí es solo texto cifrado — sin la clave
    (que vive en `secretos.env`, fuera de git) no sirve de nada.
    """

    NOMBRE_VARIABLE_ENTORNO = "YT_VIDEO_CLAVE_CIFRADO"

    def __init__(self):
        clave = os.environ.get(self.NOMBRE_VARIABLE_ENTORNO)
        if not clave:
            raise RuntimeError(
                f"Falta la variable de entorno {self.NOMBRE_VARIABLE_ENTORNO}. "
                "Genera una clave con: python -m seguridad.generar_clave "
                "y guárdala en secretos.env"
            )
        self._fernet = Fernet(clave.encode("utf-8"))

    def cifrar(self, texto_plano: str) -> bytes:
        return self._fernet.encrypt(texto_plano.encode("utf-8"))

    def descifrar(self, datos_cifrados: bytes) -> str:
        return self._fernet.decrypt(datos_cifrados).decode("utf-8")
