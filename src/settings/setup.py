import logging.config
import subprocess
import sys
import os
import logging

def instalar_pacotes_externos(pacote):
    """
Instala o pacote especificado usando pip.
    """
    try:
        os.system("python.exe -m pip install --upgrade pip")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o pacote {pacote}: {e}")
        raise

def verificar_pacotes(pacotes):
    """
Verifica se os pacotes estão instalados, caso contrário, instala-os.
    """
    for pacote in pacotes:
        try:
            __import__(pacote)
        except ImportError:
            print(f"Pacote {pacote} não encontrado. Instalando...")
            instalar_pacotes_externos(pacote)

def setup_log(nome_base, path_log):
    """
Instaura as configurações que o log irá pegar e o lugar que vai salvar
    """

    path_log = str(path_log)
    file_log = os.path.join(path_log, f'{nome_base}.log')

    logging.basicConfig(
        filename=file_log,
        level=10,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
