"""Genera una clave de cifrado nueva para proteger credenciales/token.json.

Uso: python -m seguridad.generar_clave
Copia la línea que imprime dentro de secretos.env (NUNCA la subas a git).
"""

from cryptography.fernet import Fernet


def generar_clave() -> str:
    return Fernet.generate_key().decode("utf-8")


if __name__ == "__main__":
    print(f"YT_VIDEO_CLAVE_CIFRADO={generar_clave()}")
