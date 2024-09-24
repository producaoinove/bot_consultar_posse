import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import os


def process_fatura_data(fatura_data: dict, mes_safra: str):
    try:
        lista_datas = fatura_data['datas']
        lista_valores = fatura_data['valores']
        lista_status = fatura_data['status']
        print("Listas iniciais:")
        print(f"Datas: {lista_datas}")
        print(f"Valores: {lista_valores}")
        print(f"Status: {lista_status}")
        indice_atual = 0
        while indice_atual < len(lista_datas) - 1:
            print(f"\nAnalisando índice {indice_atual}:")
            print(f"Data: {lista_datas[indice_atual]}, Status: {lista_status[indice_atual]}")
            if lista_status[indice_atual] == 'pago':
                remover = indice_atual + 1
                print(f"Removendo data para status pago {remover}")
                del lista_datas[remover]
                indice_atual += 1
            else:
                indice_atual += 1
            print(f"Listas após remoção (se houver):")
            print(f"Datas: {lista_datas}")
            print(f"Valores: {lista_valores}")
            print(f"Status: {lista_status}")
        safra_indices = [idx for idx, data in enumerate(lista_datas) if pd.to_datetime(data, format='%d/%m/%Y').month == int(mes_safra)]
        resultado_final = {
            'datas': [lista_datas[idx] for idx in safra_indices],
            'valores': [lista_valores[idx] for idx in safra_indices],
            'status': [lista_status[idx] for idx in safra_indices]
        }
        
        if '*Faturas com valor inferior à R$ 5,00 não são geradas' in resultado_final['valores']:
            try:
                resultado_final['valores'].remove('*Faturas com valor inferior à R$ 5,00 não são geradas')
            except:
                print(f"Erro ao tentar remover palavras da lista")
        print("Valores: ", resultado_final['valores'])
        print("Datas: ", resultado_final['datas'])
        print("Status: ", resultado_final['status'])
        return resultado_final

    except Exception as e:
        print(f"Falha ao processar as informações das faturas, detalhes: {str(e)}")
        return None

def criar_navegador() -> webdriver.Chrome:
    """
Realiza a criação do navegador
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service 
    from selenium.webdriver.chrome.options import Options

    try:
        opcoes = Options()
        # opcoes.add_argument("--headless=new")
        opcoes.add_argument('--disable-gpu')
        opcoes.add_argument('--no-sandbox')
        opcoes.add_argument("window-size=1920,1080")
        browser = webdriver.Chrome(options=opcoes)
        return browser
    except Exception as e:
        raise Exception(f"Impossivel criar o navegador, detalhes: {str(e)}")

def realizar_login(navegador: webdriver.Chrome, ambiente) -> webdriver.Chrome:
    """
    Realiza o login no Oi360

    Entrada:
        navegador(webdriver.Chrome): recebe um navegador ativo que seja comandado pelo memso.

    Saída:
        O navegador com instância ativa do Oi360
    """

    try:
        navegador.get(ambiente)
        str(input("Pressione enter após o login ..."))
        return navegador
    except Exception as e:
        raise Exception(f"Impossivel logar no Oi360, detalhes: {str(e)}")

def escolher_tipo_cliente(navegador: webdriver.Chrome):
    """
Responde o primeiro formulário (se é varejo ou empresarial)

Entrada:
    navegador(webdriver.Chrome): recebe um navegador ativo que seja comandado pelo memso.

Saída:
    O navegador com instância ativa do Oi360 e primeiro formulário respondido
    """

    try:
        return navegador
    except Exception as e:
        raise Exception(f"Impossivel responder primeiro formulário, detalhes: {str(e)}")

def search_doc(browser: webdriver.Chrome, documento: str, logging, actions: ActionChains):
    status = ""
    data = ""
    valor = ""
    documento = str(documento)
    # browser.implicitly_wait(30)
    # time.sleep(10)
    # print("Saiu da pausa")

    browser.implicitly_wait(15)

    res = resposta_busca(browser, documento, actions, logging)
    if res == "Element not found":
        return "Element not found"
    browser = res[0]
    info_cliente = res[1]

    if info_cliente == "Novo Cliente":
        status = "Novo Cliente"
    elif info_cliente == "Nova Fibra":
        status = "Nova Fibra"
    elif info_cliente == "Legado":
        status = "Legado"
        browser = escolher_produto(browser)
        time.sleep(6)
       
        browser = escolher_servico(browser)
        time.sleep(6)

        browser = ir_econtas(browser)
        time.sleep(6)
        browser.switch_to.default_content()

        resultado_busca = search_econta_doc(browser, actions, logging)
        print(resultado_busca)
        
        browser = ir_novoatendimento(browser)
        time.sleep(6)

    browser = retorna_selecao(browser)
    time.sleep(6)
    browser.quit()
    
    return res

def retorna_selecao(browser):
    try:
        username = WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[data-test-id="2017091914214003818486"]'))
        )
        time.sleep(6)
        username.click()
        WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.ID, 'ItemMiddle'))
        )
        actions = ActionChains(browser)
        return_select_screen = browser.find_element(By.ID, 'ItemMiddle')
        time.sleep(6)
        actions.move_to_element(return_select_screen).click().perform()
        browser.execute_script("switchApplication('OiAuthentication')")
    except Exception as e:
        print(f"Erro: {e}")

    return browser

def buscar_cliente(browser, documento, actions, logging):
    try:
        cnpj_input = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.ID, 'AuxiliarCOD_IDENT_PESSOA'))
        )
        print("Pegou CNPJ")
        if not cnpj_input.is_displayed():
            print("ATENCAO: CAMPO CNPJ NAO ESTA NA TELA")
            return "Element not found"
    except NoSuchElementException:
        print("NoSuchElementException")
        return "Element not found"
    except Exception as e:
        print("Deu erro retorno: elemento CNPJ nao encontrado")
        return "Element not found"

    cnpj_input.send_keys(documento)
    data_change_value = cnpj_input.get_attribute('data-change')
    if data_change_value:
        browser.execute_script(data_change_value)

    cnpj_search_button = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Buscar')]"))
    )

    try:
        actions.move_to_element(cnpj_search_button).click().perform()
    except:
        cnpj_search_button = browser.find_element(By.NAME, f'SelecaoAplicacao_pyDisplayHarness_6')
        data_click_value = cnpj_search_button.get_attribute('data-click')
        if data_click_value:
            browser.execute_script(data_click_value)

    time.sleep(6)

    return browser

def verificar_cliente(driver):

    time.sleep(6)

    script_span = '''
var xpath = "//span[text()='OITOTAL_FXBL']";
var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
var element = result.singleNodeValue;

if (element) {
    return "Legado";
} else {
    return null;
}
    '''
    result_span = driver.execute_script(script_span)

    if result_span:
        return (driver, 'Legado')

    script_div = '''
var xpath = "//div[contains(text(), 'Novo Cliente')]";
var result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
var numElements = result.snapshotLength;

for (var i = 0; i < numElements; i++) {
    var element = result.snapshotItem(i);
    return "Novo Cliente";
}

return null;
    '''
    result_div = driver.execute_script(script_div)

    if result_div:
        return (driver, 'Novo Cliente')
    
        
    return (driver, 'Nova Fibra')

def resposta_busca(browser, documento, actions, logging):
    browser = buscar_cliente(browser, documento, actions, logging = logging)
    if browser == "Element not found":
        return "Element not found"
    cliente = verificar_cliente(browser)
    browser = cliente[0]
    info_cliente = cliente[1]
    return (browser, info_cliente)

def escolher_produto(browser : webdriver.Chrome):

    try:
        produto_selector = '''
var xpath = "//span[text()='OITOTAL_FXBL']";
var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
var produtoElement = result.singleNodeValue;
if (produtoElement) {
    produtoElement.click();
    return "Produto encontrado e clicado";
} else {
    return "Produto não encontrado";
}
        '''
        resultado = browser.execute_script(produto_selector)
        time.sleep(6)
        
        if resultado == "Produto encontrado e clicado":
            actions = ActionChains(browser)
            # botao apresentando problema no click
            elemento_avancar = browser.find_element(By.NAME, 'MainNovoAtendimento_pyDisplayHarness_83')
            data_click_value = elemento_avancar.get_attribute('data-click')
            actions.move_to_element(elemento_avancar).click().perform()
            if data_click_value:
                browser.execute_script(data_click_value)
            try:
                div_nao_elegivel = browser.find_element(By.XPATH, "//span[contains(text(), 'Esse produto não é elegível para migração. Somente para novo endereço')]")
                time.sleep(3)
                if div_nao_elegivel.is_displayed():
                    elemento_avancar = browser.find_element(By.NAME, 'MainNovoAtendimento_pyDisplayHarness_83')
                    data_click_value = elemento_avancar.get_attribute('data-click')
                    time.sleep(1)
                    actions.move_to_element(elemento_avancar).click().perform()
                    if data_click_value:
                        browser.execute_script(data_click_value)
            except:
                print("Div de aviso não encontrada, seguindo o fluxo")
            print("produto selecionado e pagina avançada")
        else:
            print("Erro ao selecionar o produto:", resultado)
    except Exception as e:
        print(f"Erro: {e}")

    return browser

def escolher_servico(browser : webdriver.Chrome):

    try:

        try:
            # WebDriverWait(browser, 20).until(
            #     EC.presence_of_element_located((By.XPATH, "//div[@base_ref='pyWorkPage.IntentList(2)']"))
            # )
            
#             var xpath = "//*[@aria-label='Painel Central']";
# var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
# var produtoElement = result.singleNodeValue;
# if (produtoElement) {
#     produtoElement.click();
#     console.log("Produto encontrado e clicado");
# } else {
#     console.log("Produto não encontrado");
# }
            main_iframe = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.ID, "PegaGadget0Ifr"))
            )
            
            browser.switch_to.frame(main_iframe)
            service_btn = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'SERVIÇOS OI')]"))
            )
            service_btn.click()

        except Exception as e:
            print(f"Falha ao disparar evento, detalhes: {str(e)}")
        time.sleep(6)
        
        try:
            # avançar_button_selector = browser.find_element(By.XPATH, "//button[text()='INICIAR ATENDIMENTO']")
            # avançar_button_selector = WebDriverWait(browser, 10).until(
            #     EC.visibility_of_element_located((By.XPATH, avançar_button_selector))
            # )
            # actions = ActionChains(browser)
            # click_avancar = avançar_button_selector.get_attribute('data-click')
            # actions.move_to_element(avançar_button_selector).click().perform()
            avancar_js = '''
var element = document.evaluate("//button[text()='INICIAR ATENDIMENTO']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
var clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
element.dispatchEvent(clickEvent);
            '''
            browser.execute_script(avancar_js)
            # browser.switch_to.default_content()

            print('INICIAR ATENDIMENTO SELECIONADO')
        except Exception as e:
            print(f"Falha ao iniciar atendimento, detalhes: {str(e)}")
            
    except Exception as e:
        print(f"Erro: {e}")

    return browser

def ir_econtas(browser: webdriver.Chrome):
    try:
        contas_link = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'E-contas')]"))
        )
        actions = ActionChains(browser)
        actions.move_to_element(contas_link).click().perform()
        browser.implicitly_wait(10)
        print("Clique realizado com sucesso!")
        
    except Exception as e:
        print(f"Falha na busca da segunda via, detalhes: {str(e)}")
    return browser

def ir_novoatendimento(browser: webdriver.Chrome):
    try:
        browser.switch_to.default_content()
        botao_novo_atendimento = browser.find_element(By.NAME, 'headerPerformance_pyDisplayHarness_16')
        actions = ActionChains(browser)
        actions.move_to_element(botao_novo_atendimento).click().perform()
        data_click_value = botao_novo_atendimento.get_attribute('data-click')
        if data_click_value:
            browser.execute_script(data_click_value)
        browser.implicitly_wait(10)
    except Exception as e:
        print(f"Falha ao clicar no botão 'NOVO ATENDIMENTO', detalhes: {str(e)}")
    return browser

def get_posse_info(browser : webdriver.Chrome, actions: ActionChains, documento: str, index):
    time.sleep(2)
    cnpj = str(documento)
    if index == 0:
        pesquisa_menu_btn = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-ascii='Pesquisa']"))
        )
        try:
            pesquisa_menu_btn.click()
        except:
            actions.move_to_element(pesquisa_menu_btn).click().perform()
        print("Botao de pesquisa")
        
        time.sleep(2)

        cnpj_search_btn = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-ascii='CNPJ/Raiz']"))
        )

        try:
            cnpj_search_btn.click()
        except:
            actions.move_to_element(cnpj_search_btn).click().perform()
        print("Botao de CNPJ/Raiz")
        
        time.sleep(2)
        
        try:
            cnpj_search_input = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='cnpj-raiz']"))
            )
            time.sleep(2)
            cnpj_search_input.send_keys(documento)
            print("CNPJ Digitado")
        except Exception as e:
            print(f"Erro ao tentar procurar campo de busca, Detalhes: {e}")
            
        time.sleep(2)

        search_btn = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pesquisar')]"))
        )
        
        try:
            search_btn.click()
        except:
            actions.move_to_element(search_btn).click().perform()
        print("Botao Pesquisar")
        
        time.sleep(6)

        result_num = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@data-html-qtdregistro]"))
        )

        print(f"Resultado da pesquisa {result_num.text}")
        time.sleep(2)
        
        if result_num.text == '1':
            result_grid = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[@class='resultado pesquisa-resultado']"))
            )
            time.sleep(2)
            # Pegar tamanho da tabela e ver se da pra pegar o ultimo elemento com base no tamanho da tabela pelo xpath
        
            # datas_faturas_ativas = result_grid.find_elements(By.XPATH, "//*[contains(text(), '/')]")
            # lista_datas = []
            # for i in datas_faturas_ativas:
            #     valor = i.text
            #     if valor != '':
            #         lista_datas.append(valor)
            # lista_datas = lista_datas[1:]
        
            product = browser.find_elements(By.XPATH, "//*[contains(text(), 'MOVEL') or contains(text(), 'FIXO')]")
            nome_produto = product[0].text
            resultado = ['09/2024', '1 via', 'info posse']
            
            # nome_produto = "MOVEL"
            nome = "EMPRESA TESTE"
        elif result_num.text == "0":
            resultado = ['VAZIO', 'VAZIO', 'VAZIO']
            
    else:
        time.sleep(2)
        try:
            cnpj_search_input = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='cnpj-raiz']"))
            )
            time.sleep(2)
            cnpj_search_input.clear()
            time.sleep(2)
            cnpj_search_input.send_keys(documento)
            print("CNPJ Digitado")
        except Exception as e:
            print(f"Erro ao tentar procurar campo de busca, Detalhes: {e}")
            
        time.sleep(2)

        search_btn = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Pesquisar')]"))
        )
        
        try:
            search_btn.click()
        except:
            actions.move_to_element(search_btn).click().perform()
        print("Botao Pesquisar")
        
        time.sleep(6)

        result_num = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@data-html-qtdregistro]"))
        )

        print(f"Resultado da pesquisa {result_num.text}")
        time.sleep(2)
        
        if result_num.text == '1':
            result_grid = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[@class='resultado pesquisa-resultado']"))
            )
            time.sleep(2)
            # Pegar tamanho da tabela e ver se da pra pegar o ultimo elemento com base no tamanho da tabela pelo xpath
        
            # datas_faturas_ativas = result_grid.find_elements(By.XPATH, "//*[contains(text(), '/')]")
            # lista_datas = []
            # for i in datas_faturas_ativas:
            #     valor = i.text
            #     if valor != '':
            #         lista_datas.append(valor)
            # lista_datas = lista_datas[1:]
        
            product = browser.find_elements(By.XPATH, "//*[contains(text(), 'MOVEL') or contains(text(), 'FIXO')]")
            nome_produto = product[0].text
            resultado = ['09/2024', '1 via', 'info posse']
            
            # nome_produto = "MOVEL"
            nome = "EMPRESA TESTE"
        elif result_num.text == "0":
            resultado = ['VAZIO', 'VAZIO', 'VAZIO']
#     js_code = """
# let valores = Array.from(new Set(
#     Array.from(document.querySelectorAll("span"))
#     .filter(span => span.textContent.includes("$"))
#     .map(span => span.textContent)
# ));

# let datas = Array.from(new Set(
#     Array.from(document.querySelectorAll("span"))
#     .filter(span => (span.textContent.match(/\//g) || []).length === 2)
#     .map(span => span.textContent)
# )).slice(2);

# let status = Array.from(document.querySelectorAll("div"))
#     .filter(div => div.textContent.toLowerCase().includes("pago") || 
#                     div.textContent.toLowerCase().includes("não pago") || 
#                     div.textContent.toLowerCase().includes("vencido"))
#     .slice(0, valores.length) 
#     .map(div => {
#        const text = div.textContent.toLowerCase();
#         if (text.includes("pago") ) {
#             return 'pago';
#         } else {
#             return 'em aberto';
#         }
#     }).slice(0, valores.length);

# return { valores, datas, status };
#         """

#     res = browser.execute_script(js_code)
    
#     fatura_grid = WebDriverWait(browser, 20).until(
#         EC.presence_of_element_located((By.XPATH, "//*[@data-node-id='ConsultaDeFaturas']"))
#     )
    
#     datas = fatura_grid.find_elements(By.XPATH, "//*[contains(text(), '/')]")
#     lista_datas = []
#     for i in datas:
#         valor = i.text
#         if valor != '':
#             lista_datas.append(valor)
#     lista_datas = lista_datas

#     res['datas'] = lista_datas

#     valores = fatura_grid.find_elements(By.XPATH, "//*[contains(text(), '$')]")
#     lista_valores = []
#     for i in valores:
#         valor = i.text
#         if valor != '':
#             lista_valores.append(valor)
#     res['valores'] = lista_valores

#     status = fatura_grid.find_elements(By.XPATH, "//*[contains(text(), 'Não Pago') or contains(text(), 'Pago') or contains(text(), 'Vencido')]")
#     lista_status = []
#     for i in status:
#         valor = i.text
#         if valor == 'Não Pago':
#             valor = 'em aberto'
#             lista_status.append(valor)
#         if valor == 'Pago':
#             valor = 'pago'
#             lista_status.append(valor)
#         if valor == 'Vencido':
#             valor = 'em aberto'
#             lista_status.append(valor)
#     res['status'] = lista_status
#     tamanho_status = len(lista_status)
    
#     # for index, status in enumerate(lista_status):
#     #     if tamanho_status >= 2:
#     #         prox_status = index + 1
#     #         status_anterior = index - 1
#     #         if status == 'pago' and index == 0:
#     #             lista_datas.pop(prox_status)
        
#     fatura_data = {
#         'datas': lista_datas,
#         'valores': lista_valores,
#         'status': lista_status
#     }
#     resultado_final = process_fatura_data(fatura_data)


    return nome_produto, nome, cnpj, resultado

def search_econta_doc(browser: webdriver.Chrome, actions: ActionChains, logging):
    from settings import path_entrada, path_saida
    from modules import ler_controle_qualidade, tratar_controle_qualidade, exportar_controle_qualidade, criar_navegador, realizar_login, read_input_file

    try:
        time.sleep(6)
        iframe = browser.find_elements(By.TAG_NAME, 'iframe')
        size = len(iframe)
        print(f"TOTAL DE IFRAMES {size}")
        try:
            consult_iframe = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.ID, "PegaGadget0Ifr"))
            )
            time.sleep(2)
            browser.switch_to.frame(consult_iframe)
        except Exception as e:
            logging.error(f"Erro na troca para o iframe PegaGadget0Ifr, Detalhes: {e}")
            browser.switch_to.frame("PegaGadget0Ifr")

        time.sleep(6)
        
        try:
            econtas_iframe = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[@name='EContaIFrame']"))
            )
            time.sleep(2)
            browser.switch_to.frame(econtas_iframe)
        except Exception as e:
            logging.error(f"Erro na troca para o iframe EContaIFrame, Detalhes: {e}")
            econtas_iframe_att = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "//iframe"))
            )
            browser.switch_to.frame(econtas_iframe_att)

        arquivo_input = os.path.join(path_entrada, "cnpj_buscar.csv")
        arquivo_output = os.path.join(path_saida, "relatorio.csv")
        arquivo_error_out = os.path.join(path_saida, "relatorio_com_erros.csv")
        df = read_input_file(arquivo_input)
        total_inicial = len(df)
        dados_extraidos = []
        print("Arquivo de entrada lido e dados extraidos")
        for index, row in df.iterrows():
            print("----------------------------------------------------------------------------------------")
            doc = row['CNPJ']
            print(doc)
            try:
                nome_produto, nome, cnpj, resultado = get_posse_info(browser, actions, doc, index)
                print(resultado)
                # if nome_produto == '' and nome == '' and len(resultado) == 0:
                if nome_produto == '':
                    dados_extraidos.append(('ERRO', 'ERRO', 'ERRO', 'ERRO', 'ERRO', 'ERRO'))
                else:
                    dados_extraidos.append((nome_produto, nome, cnpj, resultado[0], resultado[1], resultado[2]))
                print(nome_produto, nome, cnpj, resultado)
            except Exception as e:
                print(f"ERRO: Falha buscar posse para doc {doc}, detalhes: {e}")
    
        if ('', '', '', '', '','') in dados_extraidos:
            dados_extraidos.remove(('', '', '', '', '',''))
        print("Dados vazios removidos")
        df[['NOME_PRODUTO', 'NOME', 'DOC', 'DATA_VENCIMENTO', 'VIA', 'INFO_POSSE']] = pd.DataFrame(dados_extraidos, index = df.index)
        print("Dataframe criado")
        df = df[['DOC', 'NOME', 'NOME_PRODUTO', 'DATA_VENCIMENTO', 'VIA', 'INFO_POSSE']]
        print("Dataframe filtrado")
        try:
            df_error = df[df['INFO_POSSE'] == 'ERRO']
            exportar_controle_qualidade(df_error, arquivo_error_out)
        except Exception as e:
            logging.error(f"Erro na criação do arquivo de relatório com os erros, Detalhes: {e}")
        
        df = df[df['INFO_POSSE'] != 'ERRO']
        res =  exportar_controle_qualidade(df, arquivo_output)
        
        if res == "SUCESSO":
            total_buscados = len(df)
            total_validados = df['CNPJ'].notna().sum()
            total_nao_validados = df['CNPJ'].isna().sum()
            logging.info(f"Total de documentos iniciais {total_inicial}")
            logging.info(f"Total de documentos buscados {total_buscados}")
            logging.info(f"Total de documentos validados {total_validados}")
            logging.info(f"Total de documentos não validados {total_nao_validados}")
            return "Sucesso na busca dos documentos"

            
    except Exception as e:
        print(f"Falha ao obter informações das faturas, detalhes: {str(e)}")
        return "Falha na busca dos documentos"

   
def iniciar_atendimento(browser: webdriver.Chrome, documento: str, logging) :
    emp_select = 'Oi360Empresarial'
    
    access_type_select = Select(browser.find_element(By.XPATH, '//*[@id="AcessoSelecionado"]'))
    init_button = browser.find_element(By.XPATH, "//button[contains(text(), 'INICIAR')]")
    access_type_select.select_by_visible_text(emp_select)
    browser.implicitly_wait(5)
    actions = ActionChains(browser)
    actions.move_to_element(init_button).click().perform()
    browser.implicitly_wait(1)
    browser.execute_script('switchApplication("#~OperatorID.AcessoSelecionado~#")')
    browser.implicitly_wait(5)
    time.sleep(6)
    result = search_doc(browser, documento, logging, actions)
    if result == "Element not found":
        browser.back()
        try:
            browser.find_element(By.XPATH, "//button[contains(text(), 'INICIAR')]")
        except:
            browser.back()
            init_button = browser.find_element(By.XPATH, "//button[contains(text(), 'INICIAR')]")
            actions.move_to_element(init_button).click().perform()
            browser.implicitly_wait(1)
            browser.execute_script('switchApplication("#~OperatorID.AcessoSelecionado~#")')
            browser.implicitly_wait(5)
            time.sleep(6)
            result = search_doc(browser, documento, logging, actions)

        init_button = browser.find_element(By.XPATH, "//button[contains(text(), 'INICIAR')]")
        actions.move_to_element(init_button).click().perform()
        browser.implicitly_wait(1)
        browser.execute_script('switchApplication("#~OperatorID.AcessoSelecionado~#")')
        browser.implicitly_wait(5)
        time.sleep(6)
        result = search_doc(browser, documento, logging, actions)
