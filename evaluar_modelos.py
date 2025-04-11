import pandas as pd
import re
from unidecode import unidecode

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

from sklearn.neural_network import MLPClassifier
import joblib

from sklearn.pipeline import Pipeline



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
df["oracion_limpia"] = df["oracion"].apply(limpiar_oracion)

# Variables
X = df["oracion_limpia"]
y = df["es_definicion"]

# División en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorizar texto con TF-IDF
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Entrenar modelo
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_vec, y_train)

# Predecir
y_pred_rf = rf_model.predict(X_test_vec)

# Evaluar
print("🌳 Resultados - RandomForestClassifier:")
print("Accuracy:", round(accuracy_score(y_test, y_pred_rf) * 100, 2), "%")
print(classification_report(y_test, y_pred_rf, digits=2))

# Entrenar red neuronal básica
mlp_model = MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=1000, random_state=42)
mlp_model.fit(X_train_vec, y_train)

# Predecir
y_pred_mlp = mlp_model.predict(X_test_vec)

# Evaluar
print("🧠 Resultados - MLPClassifier:")
print("Accuracy:", round(accuracy_score(y_test, y_pred_mlp) * 100, 2), "%")
print(classification_report(y_test, y_pred_mlp, digits=2))

'''
Dio mejor resultados el modelo de RandomForestClassifier, 
pero el modelo de MLPClassifier también es interesante.
'''

# Crear pipeline con vectorizer + modelo RandomForestClassifier
pipeline_rf = Pipeline([
    ("vectorizer", vectorizer),
    ("classifier", rf_model)
])

# Guardar como pipeline
joblib.dump(pipeline_rf, "modelo_definicion.pkl")
print("✅ Pipeline Random Forest guardado como 'modelo_definicion.pkl'")