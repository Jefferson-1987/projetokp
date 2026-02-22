from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Configurar modo headless (sem abrir janela)
def retornalista():
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    urlkpmedidonodia='https://www.spaceweatherlive.com/en/auroral-activity/kp-index.html'
    # Coloque aqui a URL do site
    driver.get(urlkpmedidonodia)

    # Espera o JS carregar
    time.sleep(5)
    # Pegar todos os pontos do gráfico
    elements = driver.find_elements(By.CLASS_NAME, "highcharts-point")
    raw_data=''
    for el in elements:
        #print(el.get_attribute("aria-label"))
        raw_data += str(el.get_attribute("aria-label")) + "\n "
    #print (raw_data)

    linhas = [
        l.strip()
        for l in raw_data.split("\n")
        if "Observed Kp." in l
    ]

    dados = {}

    for linha in linhas:
        match = re.search(r"(\d{1,2}) (\w{3}) (\d{2})h-\d{2}h, ([\d\.]+)", linha)
        if match:
            dia, mes_str, hora, kp = match.groups()

            mes = datetime.strptime(mes_str, "%b").month
            ano = datetime.now(ZoneInfo("UTC")).year

            dt_utc = datetime(ano, mes, int(dia), int(hora), tzinfo=ZoneInfo("UTC"))

            # Usamos dict para eliminar duplicados automaticamente
            kp = kp.rstrip(".")
            dados[dt_utc] = float(kp)
    #print (f'Estas são as linhas -> {linhas}\n\n')
    # 2️⃣ Ordenar cronologicamente
    ordenado = sorted(dados.items())

    # 3️⃣ Pegar apenas o dia anterior (UTC)
    hoje_utc = datetime.now(ZoneInfo("UTC")).date()
    ontem_utc = hoje_utc - timedelta(days=1)

    ontem_filtrado = [
        (dt, kp)
        for dt, kp in ordenado
        if dt.date() == ontem_utc
    ]

    # 4️⃣ Garantir apenas 8 períodos
    ultimos_8 = ontem_filtrado[-8:]

    # 5️⃣ Converter para horário de Brasília
    resultado = []

    for dt_utc, kp in ultimos_8:
        dt_br = dt_utc.astimezone(ZoneInfo("America/Sao_Paulo"))
        resultado.append({
            "data_brasilia": dt_br.strftime("%d/%m %H:%M"),
            "kp": round(kp, 2)
        })

    # print(resultado)
    ano = datetime.now().year

    dias_semana = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo"
    ]

    frases = []

    for item in resultado:
        dt = datetime.strptime(f"{item['data_brasilia']}/{ano}", "%d/%m %H:%M/%Y")

        inicio = dt.strftime("%Hh")
        fim = (dt + timedelta(hours=3)).strftime("%Hh")

        dia_semana = dias_semana[dt.weekday()]
        data_formatada = dt.strftime("%d/%m/%Y")

        frase = (
            f"O Kp medido na hora {inicio} - {fim} "
            f"na {dia_semana} dia {data_formatada} foi {item['kp']}"
        )

        frases.append(frase)
    return frases


#print(frases)
