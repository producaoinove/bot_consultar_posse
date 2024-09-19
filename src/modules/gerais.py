import os
import pandas as pd
from selenium import webdriver

def coletar_informacoes(documento: str,browser : webdriver.Chrome, logging) -> tuple:
    from modules.navegador import iniciar_atendimento
    return iniciar_atendimento(browser, documento, logging)


def main(logging):
    """
    Raíz do código fonte
    """

    from settings import path_entrada, path_saida, setup_log, path_log
    from modules import ler_controle_qualidade, tratar_controle_qualidade, exportar_controle_qualidade, criar_navegador, realizar_login, read_input_file

    setup_log('bot_consulta_posse', path_log)

    browser = criar_navegador()
    print("Navegador criado!")

    realizar_login(browser, 'https://oi360.oi.net.br/prweb/PRServletCustom/AX6P2laLe91D09R0jTjfNJdv0u0s3qcA*/!STANDARD?pyActivity=Data-Portal.ShowDesktop#!')
    print("Login realizado!")

    # df = tratar_controle_qualidade(df)

    # tipo_p = linhas['TIPO_CLIENTE']
    # mes_safra = linhas['MES_SAFRA']
    print(f"Documento procurado inicial")
    documento_const = "43755331000144"

    try:
        coletar_informacoes(documento_const, browser, logging)
    except:
        logging.error(f"Erro de leitura, documento inicial")
