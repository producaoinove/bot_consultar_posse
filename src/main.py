required_packages = [
    "pandas",
    "datetime",
    "selenium",
]
from settings import verificar_pacotes, setup_log, path_log
from modules import main
import logging 

if __name__ == "__main__":

    try:
        verificar_pacotes(required_packages)
    except Exception as e:
        print(f"Falha ao verificar e baixar pacotes externos! Detalhes: {str(e)}")

    try:
        setup_log('bot_consulta_posse', path_log)
    except Exception as e:
        print(f"Falha ao configurar arquivo de log! Detalhes: {str(e)}")

    try:
        logging.info("Bot Posse iniciado!")
        main(logging)
        logging.info("Bot Posse finalizado!")
        print("Bot Consultar Posse Finalizado")
    except Exception as e:
        logging.error(f"Deu erro no bot. Detalhes: {str(e)}")