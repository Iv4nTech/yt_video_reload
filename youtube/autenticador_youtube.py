import json
import os
import stat
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from seguridad.cifrador_token import CifradorToken


class AutenticadorYouTube:
    """Gestiona el login OAuth2 contra la YouTube Data API y cachea el token en disco.

    La primera autenticación necesita abrir un navegador, así que debe hacerse
    una vez en tu ordenador (no en el hosting). Una vez generado el fichero de
    token, se copia al servidor y las siguientes ejecuciones lo renuevan solas.

    IMPORTANTE: el ámbito de YouTube no permite pedir permiso solo para
    "cambiar título y miniatura" — el mismo ámbito que necesita videos.update
    también da permiso para borrar vídeos (videos.delete exige exactamente
    los mismos ámbitos). No hay forma de restringirlo desde la API, así que
    el token se guarda siempre cifrado en disco (ver `seguridad/cifrador_token.py`)
    y solo se descifra en memoria justo antes de hablar con Google. Si alguna
    vez sospechas que se ha filtrado, revócalo al momento desde
    https://myaccount.google.com/permissions.
    """

    AMBITOS = ["https://www.googleapis.com/auth/youtube"]

    def __init__(self, ruta_secreto_cliente: str, ruta_token: str):
        self._ruta_secreto_cliente = Path(ruta_secreto_cliente)
        self._ruta_token = Path(ruta_token)
        self._cifrador = CifradorToken()

    def obtener_credenciales(self) -> Credentials:
        credenciales = self._cargar_token_existente()

        if not credenciales or not credenciales.valid:
            credenciales = self._renovar_o_solicitar(credenciales)
            self._guardar_token(credenciales)

        return credenciales

    def _cargar_token_existente(self) -> Credentials | None:
        if not self._ruta_token.exists():
            return None
        datos_cifrados = self._ruta_token.read_bytes()
        texto_json = self._cifrador.descifrar(datos_cifrados)
        return Credentials.from_authorized_user_info(json.loads(texto_json), self.AMBITOS)

    def _renovar_o_solicitar(self, credenciales: Credentials | None) -> Credentials:
        if credenciales and credenciales.expired and credenciales.refresh_token:
            credenciales.refresh(Request())
            return credenciales

        flujo = InstalledAppFlow.from_client_secrets_file(str(self._ruta_secreto_cliente), self.AMBITOS)
        return flujo.run_local_server(port=0)

    def _guardar_token(self, credenciales: Credentials) -> None:
        self._ruta_token.parent.mkdir(parents=True, exist_ok=True)
        datos_cifrados = self._cifrador.cifrar(credenciales.to_json())
        self._ruta_token.write_bytes(datos_cifrados)
        os.chmod(self._ruta_token, stat.S_IRUSR | stat.S_IWUSR)
