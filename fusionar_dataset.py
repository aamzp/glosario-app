import pandas as pd

# Cargar ambos archivos
positivos = pd.read_csv("datasets/definiciones_concepto.csv", sep=";")
negativos = pd.read_csv("datasets/negativos_concepto.csv", sep=";")

# Uni
df_completo = pd.concat([positivos, negativos], ignore_index=True)

# Mezclar aleatoriamente
df_completo = df_completo.sample(frac=1, random_state=42).reset_index(drop=True)

# Guardar dataset final
df_completo.to_csv("datasets/dataset_definiciones_final.csv", index=False, sep=";")
print("✅ Dataset final generado: dataset_definiciones_final.csv")
