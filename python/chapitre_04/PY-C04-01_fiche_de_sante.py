# PY-C04-01 — fiche de santé
# Chapitre 4 — Explorer, nettoyer et préparer les données
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
df = pd.read_csv("clients_360.csv")
print("lignes, colonnes :", df.shape)
print("doublons client_id :", df.duplicated("client_id").sum())
print()
print("taux de manquants :")
print(df.isna().mean().sort_values(ascending=False).head(10))
print()
print(df.describe().T[["min", "50%", "max"]])
print()
for c in df.select_dtypes("object"):
    print(c, "->", df[c].nunique(), "modalités")
