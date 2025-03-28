from fastapi import FastAPI, File, UploadFile
import pdfplumber # Importar pdfplumber para extraer texto de PDFs
import spacy # Importar spaCy para procesamiento de lenguaje natural

nlp = spacy.load("es_core_news_sm") # Cargar el modelo de spaCy para español

app = FastAPI(
    title="Glosario App",
    description="API para cargar PDFs y detectar definiciones",
    version="0.1.0",
    docs_url="/docs",  
    redoc_url="/redoc" 
)


@app.get("/")
def leer_root():
    return {"mensaje": "¡Hola desde FastAPI con docs!"}

@app.post("/subir-pdf/")
async def subir_pdf(archivo: UploadFile = File(...)):
    texto_extraido = ""

    # Verificar que el archivo sea PDF
    if archivo.content_type == "application/pdf":
        with pdfplumber.open(archivo.file) as pdf:
            for pagina in pdf.pages:
                texto_extraido += pagina.extract_text() + "\n"

        # Procesar texto con spaCy
        doc = nlp(texto_extraido)

        # Dividir texto en oraciones
        oraciones = [sent.text.strip() for sent in doc.sents]

        # Detectar oraciones que parezcan definiciones explícitas
        patrones = [" es ", " se define como ", " se entiende por ", " consiste en "]
        definiciones = [
            o for o in oraciones
            if any(p in o.lower() for p in patrones)
        ]

        return {
            "nombre_archivo": archivo.filename,
            "total_oraciones": len(oraciones),
            "definiciones_detectadas": definiciones[:10]  # mostrar solo las primeras 10
        }

    else:
        return {"error": "Por favor sube un archivo PDF válido."}