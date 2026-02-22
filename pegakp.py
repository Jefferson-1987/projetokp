from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import altarnativaselenium

app = Flask(__name__)


def retornatabela():

    url = "https://services.swpc.noaa.gov/text/3-day-forecast.txt"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"erro": "Falha ao obter dados"}), 500

    texto = response.text

    # 🔎 1️⃣ Extrair somente a parte da tabela
    inicio = texto.find("NOAA Kp index breakdown")
    fim = texto.find("Rationale:", inicio)

    bloco = texto[inicio:fim]

    linhas = bloco.splitlines()

    # Remove título e linhas vazias
    linhas = [l for l in linhas if l.strip()]
    linhas = linhas[1:]  # remove linha do título

    # 🔄 2️⃣ Traduzir meses
    meses = {
        "Jan": "Jan",
        "Feb": "Fev",
        "Mar": "Mar",
        "Apr": "Abr",
        "May": "Mai",
        "Jun": "Jun",
        "Jul": "Jul",
        "Aug": "Ago",
        "Sep": "Set",
        "Oct": "Out",
        "Nov": "Nov",
        "Dec": "Dez"
    }

    linha_datas = linhas[0]

    for en, pt in meses.items():
        linha_datas = linha_datas.replace(en, pt)

    linhas[0] = linha_datas

    # 🔥 3️⃣ Destacar valores > 3.0
    def destacar(match):
        valor = match.group()
        numero = float(re.findall(r"\d+\.\d+", valor)[0])
        if numero > 3.0:
            return f"*{valor}*"
        return valor

    linhas_formatadas = []

    for linha in linhas:
        nova_linha = re.sub(
            r"\d+\.\d+(?:\s*\(G\d\))?",
            destacar,
            linha
        )
        linhas_formatadas.append(nova_linha.strip())

    # 🔗 4️⃣ Transformar em string única mantendo espaçamento
    resultado = " ".join(linhas_formatadas)

    return resultado


@app.route("/kp", methods=["GET"])
def pegar_kp():

    arrayprevisao = retornatabela()

    # Pegando lista via selenium
    listaleitura = altarnativaselenium.retornalista()

    return jsonify({
        "arrayprevisao": arrayprevisao,
        "listaleitura": listaleitura
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
