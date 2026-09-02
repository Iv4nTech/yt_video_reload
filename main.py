"""Punto de entrada del proyecto. Pensado para ser ejecutado periódicamente por cron."""

from dotenv import load_dotenv

from configuracion.configuracion import Configuracion
from orquestador import Orquestador


def main() -> None:
    load_dotenv("secretos.env")
    configuracion = Configuracion()
    orquestador = Orquestador(configuracion)
    orquestador.ejecutar()


if __name__ == "__main__":
    main()
