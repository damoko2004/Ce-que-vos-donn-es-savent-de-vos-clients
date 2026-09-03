# PY-C21-01 — profils et similarité
# Chapitre 21 — Cas 8 — Recommander par le contenu
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
cat = pd.read_csv("catalogue.csv")
COLS_TEXTE = ["categorie", "marque", "matiere", "usage", "gamme"]
cat["texte"] = cat[COLS_TEXTE].fillna("").astype(str).agg(" ".join, axis=1).str.strip()
V = TfidfVectorizer(min_df=3).fit_transform(cat.texte)
voisins = NearestNeighbors(n_neighbors=min(6, len(cat)), metric="cosine").fit(V)
POS = {ref: i for i, ref in enumerate(cat.reference)}
def similaires(ref_id, n=5):
    i = POS[ref_id]
    k = min(n + 1, len(cat))
    _, idx = voisins.kneighbors(V[i], n_neighbors=k)
    idx = [j for j in idx[0] if j != i][:n]
    return cat.iloc[idx][["reference", "libelle"]]
def profil_client(achats):
    """Moyenne des profils achetes, ponderee par la recence."""
    lignes = [(POS[r], p) for r, p in zip(
        achats.reference, np.exp(-achats.anciennete_jours / 180)) if r in POS]
    if not lignes:
        return None
    idx, poids = zip(*lignes)
    w = np.asarray(poids, dtype=float).reshape(-1, 1)
    return np.asarray(V[list(idx)].multiply(w).sum(axis=0) / w.sum())
