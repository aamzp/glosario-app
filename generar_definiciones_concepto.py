import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from unidecode import unidecode

from termino import terminos


# Patrones que suelen indicar definiciones 
patrones_definicion = [
    r"es una", r"es un", r"es la", r"es el",
    r"se define como", r"consiste en", r"puede definirse como", r"se entiende por"
]

# Filtrar y excluir introducciones

def contiene_patron_definicion(texto):
    texto = texto.lower()
    if texto.startswith("te explicamos"):
        return False  # descarta introducciones, las odio
    return any(re.search(patron, texto) for patron in patrones_definicion)

# Lista para almacenar resultados
definiciones = []

# Recorrido de terminso
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
                for p in parrafos:
                    texto = p.get_text().strip()
                    if contiene_patron_definicion(texto):
                        print(f"✔ DEFINICION ENCONTRADA: {texto}")
                        definiciones.append({
                            "termino": termino,
                            "oracion": texto,
                            "es_definicion": 1
                        })
            else:
                print(f"No se encontró el contenido para: {termino}")
        else:
            print(f"X Error HTTP: {response.status_code}")
        time.sleep(1)
    except Exception as e:
        print(f"Error con {termino}: {e}")

# Guardar CSV
df = pd.DataFrame(definiciones)
df.to_csv("datasets/definiciones_concepto.csv", index=False, sep=";", encoding="utf-8-sig")
print("Archivo generado: definiciones_concepto.csv !!!!")
