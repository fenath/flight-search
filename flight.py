from time import sleep
from datetime import date
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

FROM       = "CWB"
TO         = "FOR"
DATA_IDA   = date(2024, 6, 1)
DATA_VOLTA = date(2024, 6, 14)

URL = 'https://www.google.com/travel/flights'

WAIT_TIME  = 5
SHORT_WAIT = 3

IS_RELEASE = True

def create_browser():
    options = webdriver.ChromeOptions()
    if (IS_RELEASE):
        # options.add_argument('--headless')
        # disable message 'devtools listening' 
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        # hide window 
        options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=options)
    return browser

def scrap_flight(browser, parametros_viagem):
    viagem_de = parametros_viagem['de']
    viagem_para = parametros_viagem['para']
    data_ida = parametros_viagem['data_ida']
    data_volta = parametros_viagem['data_volta']

    if (browser == None):
        created_here = True
        browser = create_browser()
    else:
        created_here = False

    browser.get(URL)
    wait = WebDriverWait(browser, timeout=WAIT_TIME)

    sleep(WAIT_TIME)
    div_principal = browser.find_elements(By.CSS_SELECTOR, '.AJxgH')[0]

    inputs = div_principal.find_elements(By.TAG_NAME, 'input')

    # Lidando com ida
    input_ida = inputs[0]
    input_ida.clear()
    input_ida.send_keys(viagem_de)
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        'div.XOeJFd.rHFvzd li'
    ))).click()

    input_volta = inputs[2]
    input_volta.clear()
    input_volta.send_keys(viagem_para)
    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        'div.XOeJFd.rHFvzd li'
    ))).click()

    input_data_ida   = inputs[4]
    input_data_volta = inputs[5]

    # Datas de ida e volta
    sleep(SHORT_WAIT)
    input_data_ida.send_keys(data_ida.strftime('%d/%m/%Y') + Keys.TAB)
    sleep(SHORT_WAIT)
    input_data_volta.send_keys(data_volta.strftime('%d/%m/%Y') + Keys.TAB)

    # Quantidade passageiros
    # lb_qtd_adultos = browser.find_element(By.CSS_SELECTOR, '#i9-1 > div > span.flJ24b.Jj8ghe > span:nth-child(1)')
    # qtd_adultos = lb_qtd_adultos.text
    sleep(SHORT_WAIT)
    bt_qtd_passageiros = div_principal.find_element(
        By.TAG_NAME,
        'button'
    )
    bt_qtd_passageiros.click()
    popup = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ZGEB9c.yRXJAe.iWO5td')))
    buttons = popup.find_elements(By.CSS_SELECTOR, 'button')
    adulto_dec, adulto_inc, *outros_btn, concluido, cancelar = buttons
    adulto_inc.click()
    concluido.click()

    btn_pesquisar = browser.find_element(
        By.CSS_SELECTOR,
        '#yDmH0d > c-wiz.zQTmif.SSPGKf > div > div:nth-child(2) > c-wiz > div.cKvRXe > c-wiz > div.vg4Z0e > div:nth-child(1) > div.SS6Dqf.POQx1c > div.MXvFbd > div > button')
    btn_pesquisar.click()

    sleep(WAIT_TIME)

    results_div = browser.find_elements(By.CSS_SELECTOR, 'ul.Rk10dc')[0]
    result = results_div.find_elements(By.CSS_SELECTOR, 'li .BVAVmf')[0]
    valor_viagem = int(result.text.split(' ')[1].replace('.', ''))

    if (created_here):
        browser.quit()

    return valor_viagem

def create_parametros(de, para, **kwargs):
    data_ida = kwargs.get('data_ida', DATA_IDA)
    data_volta = kwargs.get('data_volta', DATA_VOLTA)
    parametros_viagem = {
        'de': de,
        'para': para,
        'data_ida': data_ida,
        'data_volta': data_volta,
        'valor': 0
    }
    return parametros_viagem

def create_parametros_range(de, para, time_range, **kwargs):
    parametros_viagem = []
    day = datetime.timedelta(days=1)
    for i in range(0, time_range):
        for j in range(0, time_range):
            parametros = create_parametros(de, para, **kwargs)
            parametros['data_ida'] = parametros['data_ida'] + day * i
            parametros['data_volta'] = parametros['data_volta'] + day * (i + j)
            parametros_viagem.append(parametros)
    return parametros_viagem

def print_resultados_pesquisa(parametros_viagem):
    formata_data = lambda data: data.strftime('%d/%m/%Y')
    fmt_ida = formata_data(parametros_viagem['data_ida'])
    fmt_volta = formata_data(parametros_viagem['data_volta'])
    print(f'Valor viagem {parametros_viagem["de"]} -> {parametros_viagem["para"]} '+
          f'de {fmt_ida} a {fmt_volta}: R$ {parametros_viagem["valor"]}')

def print_tabela_resultados(lista_viagens, quantidade_linhas):
    print("Tabela de resultados")
    print("De -> Para | Data Ida | Data Volta | Valor")
    # De -> Para | Data Ida | Data Volta | Valor
    # CWB -> FOR | 04/06/24 | 18/06/24 | R$ 1000
    for i in range(0, min(quantidade_linhas, len(lista_viagens))):
        parametros_viagem = lista_viagens[i]
        formata_data = lambda data: data.strftime('%d/%m/%y')
        fmt_ida = formata_data(parametros_viagem['data_ida'])
        fmt_volta = formata_data(parametros_viagem['data_volta'])
        print(f'{parametros_viagem["de"]} -> {parametros_viagem["para"]} | {fmt_ida} | {fmt_volta}   | R$ {parametros_viagem["valor"]}')
    print('----------------------------------------------')

def salvar_resultados(lista_viagens):
    now = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    with open('resultados'+now+'.txt', 'w') as f:
        for viagem in lista_viagens:
            f.write(
                f'{viagem["de"]} -> {viagem["para"]} | '+
                f'{viagem["data_ida"]} | {viagem["data_volta"]} '+
                f'| R$ {viagem["valor"]}\n')

def main():
    print("web scraper for Google Flights")

    lista_viagens = []

    lista_viagens += create_parametros_range('CWB', 'FOR', 5, 
                                             data_ida=date(2024,7,15), 
                                             data_volta=date(2024,7,30))
    lista_viagens += create_parametros_range('CWB', 'FOR', 5, 
                                             data_ida=date(2024,9,1), 
                                             data_volta=date(2024,9,15))
    lista_viagens += create_parametros_range('CWB', 'FOR', 5, 
                                             data_ida=date(2024,8,1), 
                                             data_volta=date(2024,8,15))
    lista_viagens += create_parametros_range('CWB', 'FOR', 5, 
                                             data_ida=date(2024,7,1), 
                                             data_volta=date(2024,7,15))
    lista_viagens += create_parametros_range('CWB', 'FOR', 5)
    lista_viagens += create_parametros_range('CWB', 'JDO', 5)

    print(f'Quantidade de viagens: {len(lista_viagens)}')
    dv = create_browser()
    dv.minimize_window()
    for idx, par in enumerate(lista_viagens):
        try:
            valor = scrap_flight(dv, par)
            lista_viagens[idx]['valor'] = valor
            print_resultados_pesquisa(par)
        except Exception as e:
            print(f'Erro ao buscar viagem: {e}')

    # remover viagens sem valor
    lista_viagens = [viagem for viagem in lista_viagens if viagem['valor'] > 0]

    lista_viagens.sort(key=lambda x: x['valor'])
    print_tabela_resultados(lista_viagens, 10)
    salvar_resultados(lista_viagens)

    print("proccess finished!")


if __name__=="__main__":
    main()
