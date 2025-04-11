from fastapi import FastAPI, File, UploadFile, Query
from pydantic import BaseModel
import pdfplumber
import spacy
import joblib
import os
import re
from fastapi.middleware.cors import CORSMiddleware


'''
Cargar el modelo balanceado
'''
modelo_path = "modelo_definicion.pkl"
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
Configuración de CORS
'''

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def clasificar_oraciones(oraciones, umbral=0.75):
    resultados = []
    for oracion in oraciones:
        vector = vectorizer.transform([oracion])
        probabilidad = round(modelo.predict_proba(vector)[0][1], 2)
        if probabilidad >= umbral:
            resultados.append((oracion, probabilidad))
    return resultados

'''
Ruta definitiva para subir PDF y clasificar oraciones
'''

@app.post("/subir-pdf-clasificar/")
async def subir_pdf_clasificar(
    archivo: UploadFile = File(...),
    umbral: float = Query(0.5, ge=0.0, le=1.0, description="Umbral de clasificación entre 0.0 y 1.0")
):
    resultados = []

    if archivo.content_type == "application/pdf":
        with pdfplumber.open(archivo.file) as pdf:
            for numero_pagina, pagina in enumerate(pdf.pages, start=1):
                contenido = pagina.extract_text()
                if contenido:
                    doc = nlp(contenido)
                    oraciones = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) >= 50]

                    for oracion in oraciones:
                        vector = vectorizer.transform([oracion])
                        probabilidad = round(modelo.predict_proba(vector)[0][1], 2)
                        prediccion = 1 if probabilidad >= umbral else 0

                        resultados.append({
                            "oracion": oracion,
                            "pagina": numero_pagina,
                            "prediccion": prediccion,
                            "probabilidad_definicion": probabilidad
                        })

        return {
            "nombre_archivo": archivo.filename,
            "total_oraciones": len(resultados),
            "definiciones_detectadas": [r for r in resultados if r["prediccion"] == 1]
        }

    else:
        return {"error": "Por favor sube un archivo PDF válido."}
    
'''
Limpieza de elementos innecesarios y Ruta para la interfaz de usuario
'''

def limpiar_oracion(oracion: str) -> str:
    if not oracion:
        return ""

    # Elimina solo URLs
    oracion = re.sub(r"http\S+|www\S+", "", oracion)

    # Elimina "Legal:" al inicio, pero NO más
    oracion = re.sub(r"^(Legal|Nota|Fuente):\s*", "", oracion, flags=re.IGNORECASE)

    # Limpieza suave
    oracion = re.sub(r"\s+", " ", oracion).strip().strip("-–\"“”")

    return oracion

@app.post("/subir_y_clasificar")
async def subir_y_clasificar(file: UploadFile = File(...), umbral: float = 0.75):
    with pdfplumber.open(file.file) as pdf:
        resultados = []
        for i, page in enumerate(pdf.pages):
            texto = page.extract_text()
            if not texto:
                continue
            oraciones = [limpiar_oracion(sent.text) for sent in nlp(texto).sents]
            oraciones = [o for o in oraciones if o.strip()]            
            clasificadas = clasificar_oraciones(oraciones, umbral=umbral)
            for oracion, score in clasificadas:
                resultados.append({
                    "pagina": i + 1,
                    "oracion": oracion,
                    "score": score
                })
    return resultados