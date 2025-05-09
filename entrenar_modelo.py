import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import re

from unidecode import unidecode

# Función de limpieza
def limpiar_oracion(texto):
    if pd.isna(texto):
        return ""
    texto = unidecode(texto)
    texto = texto.lower()
    texto = re.sub(r"[“”\"«»‘’]", "", texto)
    texto = re.sub(r"[–—\-•°·•]", "", texto)
    texto = re.sub(r"[(){}\[\]]", "", texto)
    texto = re.sub(r"[^a-záéíóúüñ0-9\s.,;:]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

# Cargar dataset
df = pd.read_csv("datasets/dataset_definiciones_final.csv", sep=";")


# Aplicar limpieza
df["oracion_limpia"] = df["oracion"].apply(limpiar_oracion)

# Separar oraciones y etiquetas
X = df["oracion_limpia"]
y = df["es_definicion"]

# Entrenamiento y validación
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pipeline de vectorización y modelo
pipeline = Pipeline([
    ("vectorizer", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Entrenar modelo
pipeline.fit(X_train, y_train)

# Guardar modelo
joblib.dump(pipeline, "modelo_definicion_balanceado.pkl")

# Precisión del modelo
accuracy = pipeline.score(X_test, y_test)
print(f"✅ Modelo entrenado. Precisión: {round(accuracy * 100, 2)}%")
