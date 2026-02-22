from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
import altarnativaselenium

app = Flask(__name__)


def formatar_previsao(indicadores):
    hoje = datetime.today()
    resultado = []

    dias_semana = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo"
    ]

    for i in range(3):
        data = hoje + timedelta(days=i)
        dia_semana = dias_semana[data.weekday()]
        data_formatada = data.strftime('%d/%m/%Y')

        minimo = indicadores[i*2]
        maximo = indicadores[i*2 + 1]

        if i == 0:
            texto = f"Previsão de hoje {dia_semana} {data_formatada} é de mínima de {minimo} e máxima {maximo}"
        elif i == 1:
            texto = f"Previsão de amanhã {dia_semana} {data_formatada} é de mínima de {minimo} e máxima de {maximo}"
        else:
            texto = f"Previsão de {dia_semana} {data_formatada} é de mínima de {minimo} e máxima {maximo}"

        resultado.append(texto)

    return resultado


@app.route("/kp", methods=["GET"])
def pegar_kp():

    urlkpprevisao = 'https://www.spaceweatherlive.com/'
    urlkpmedidonodia = 'https://www.spaceweatherlive.com/en/auroral-activity/kp-index.html'

    pageprevisao = requests.get(urlkpprevisao)
    pageleitura = requests.get(urlkpmedidonodia)

    soup = BeautifulSoup(pageprevisao.text, 'html.parser')

    indicadores = [
        span.text
        for span in soup.select('td.text-center span')
        if re.match(r'^Kp\d[+-]?$', span.text)
    ]

    arrayprevisao = formatar_previsao(indicadores)

    # Pegando lista via selenium
    listaleitura = altarnativaselenium.retornalista()

    return jsonify({
        "arrayprevisao": arrayprevisao,
        "listaleitura": listaleitura
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)