from fastapi import FastAPI, File, UploadFile, Query
from pydantic import BaseModel
import pdfplumber
import spacy
import joblib
import os

'''
Cargar el modelo balanceado
'''
modelo_path = "modelo_definicion_balanceado.pkl"
modelo_pipeline = joblib.load(modelo_path)
vectorizer = modelo_pipeline.named_steps["vectorizer"]
modelo = modelo_pipeline.named_steps["classifier"]

'''
spaCy
'''
nlp = spacy.load("es_core_news_sm")


'''
FastAPI
'''

app = FastAPI(
    title="Glosario App",
    description="API para clasificar oraciones como definiciones",
    version="0.2.0",
)

class OracionEntrada(BaseModel):
    oracion: str


'''
Esquema de entrada para clasificación individual
'''

class EntradaOracion(BaseModel):
    oracion: str

'''
Clasificador de oraciones
'''

def clasificar_oraciones(oraciones, umbral=0.75):
    resultados = []
    for oracion in oraciones:
        vector = vectorizer.transform([oracion])
        probabilidad = round(modelo.predict_proba(vector)[0][1], 2)
        prediccion = 1 if probabilidad >= umbral else 0
        resultados.append({
            "oracion": oracion,
            "prediccion": prediccion,
            "probabilidad_definicion": probabilidad
        })
    return resultados

'''
Ruta de inicio
'''

@app.get("/")
def leer_root():
    return {"mensaje": "¡Hola desde FastAPI con docs!"}


'''
Ruta de subida y clasificación de PDF
'''

@app.post("/subir-pdf/")
async def subir_pdf(archivo: UploadFile = File(...)):
    if archivo.content_type != "application/pdf":
        return {"error": "Por favor sube un archivo PDF válido."}

    texto_extraido = ""
    with pdfplumber.open(archivo.file) as pdf:
        for pagina in pdf.pages:
            texto_extraido += pagina.extract_text() + "\n"

    oraciones = [sent.text.strip() for sent in nlp(texto_extraido).sents]
    resultados = clasificar_oraciones(oraciones[:10])  # límite a 10
    return {
        "nombre_archivo": archivo.filename,
        "total_oraciones": len(oraciones),
        "clasificaciones": resultados
    }

        
'''
Clasificación con modelo propio (.pkl)
'''

@app.post("/clasificar-oracion/")
def clasificar_oracion(data: EntradaOracion, umbral: float = 0.75):
    resultado = clasificar_oraciones([data.oracion], umbral=umbral)[0]
    resultado["umbral_usado"] = umbral
    return resultado

'''
Ruta definitiva para subir PDF y clasificar oraciones
'''

@app.post("/subir-pdf-clasificar/")
async def subir_pdf_clasificar(
    archivo: UploadFile = File(...),
    umbral: float = Query(0.5, ge=0.0, le=1.0)
):
    if archivo.content_type != "application/pdf":
        return {"error": "Por favor sube un archivo PDF válido."}

    texto_extraido = ""
    with pdfplumber.open(archivo.file) as pdf:
        for pagina in pdf.pages:
            texto_extraido += pagina.extract_text() + "\n"

    oraciones = [sent.text.strip() for sent in nlp(texto_extraido).sents if len(sent.text.strip()) >= 50]
    resultados = clasificar_oraciones(oraciones, umbral)
    definiciones = [r for r in resultados if r["prediccion"] == 1]

    return {
        "nombre_archivo": archivo.filename,
        "total_oraciones": len(oraciones),
        "definiciones_detectadas": definiciones
    }
