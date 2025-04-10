import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import spacy
from unidecode import unidecode
from termino import terminos

# Cargar modelo de spaCy para separar oraciones
nlp = spacy.load("es_core_news_sm")

# Patrones que indican definiciones explícitas
patrones_definicion = [
    r"es una", r"es un", r"es la", r"es el",
    r"se define como", r"consiste en", r"puede definirse como", r"se entiende por",
    r"se considera", r"implica", r"puede entenderse como", r"se refiere a",
    r"se caracteriza por", r"representa", r"designa", r"se trata de"
]

def contiene_patron_definicion(texto):
    texto = texto.lower()
    if texto.startswith("te explicamos"):
        return True  # es definición
    return any(re.search(patron, texto) for patron in patrones_definicion)

# Almacena frases no definitorias
negativos = []

for termino in terminos:
    termino_url = unidecode(termino).lower().replace(" ", "-")
    url = f"https://concepto.de/{termino_url}/"
    print(f"Consultando: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            contenedor = soup.find("div", class_="entry-content")
            if contenedor:
                parrafos = contenedor.find_all("p")
                contador = 0
                for p in parrafos:
                    texto = p.get_text().strip()
                    doc = nlp(texto)
                    for sent in doc.sents:
                        oracion = sent.text.strip()
                        if len(oracion) >= 50 and not contiene_patron_definicion(oracion):
                            negativos.append({
                                "termino": termino,
                                "oracion": oracion,
                                "es_definicion": 0
                            })
                            print(f"✔ ORACION NO DEFINITORIA: {oracion}")
                            contador += 1
                            if contador >= 2:
                                break
                    if contador >= 2:
                        break
        else:
            print(f"⚠️ Error HTTP {response.status_code}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error con {termino}: {e}")

# Guardar archivo CSV
df = pd.DataFrame(negativos)
df.to_csv("datasets/negativos_concepto.csv", index=False, sep=";")
print("✅ Archivo generado: negativos_concepto.csv")
