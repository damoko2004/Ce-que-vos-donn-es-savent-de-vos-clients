# PY-PG3-01 — contrôles unitaires et indice de préférence numérique
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
from sklearn.cluster import DBSCAN
def duree_anormale(q, ref_mediane, seuil_bas=0.4):
    if ref_mediane <= 0:
        raise ValueError("ref_mediane doit etre strictement positive")
    return (q.duree_min < seuil_bas * ref_mediane).astype(int)
def straightlining(reponses_serie):
    if reponses_serie.shape[1] < 2:
        raise ValueError("une batterie doit contenir au moins deux questions")
    n_reponses = reponses_serie.notna().sum(axis=1)
    n_modalites = reponses_serie.nunique(axis=1, dropna=True)
    denom = (n_reponses - 1).replace(0, np.nan)
    score = 1 - (n_modalites - 1) / denom
    return score.clip(0, 1).where(n_reponses >= 2)
def gps_repete(gps, tolerance_m=25):
    """Taille du cluster de proximite ; NaN si le GPS est absent."""
    if tolerance_m <= 0:
        raise ValueError("tolerance_m doit etre strictement positive")
    sortie = pd.Series(np.nan, index=gps.index, dtype=float)
    valide = gps[["lat", "lon"]].notna().all(axis=1)
    if not valide.any():
        return sortie
    coords = np.radians(gps.loc[valide, ["lat", "lon"]].to_numpy(dtype=float))
    labels = DBSCAN(eps=tolerance_m / 6_371_000.0, min_samples=1,
                    metric="haversine").fit_predict(coords)
    tailles = pd.Series(labels).map(pd.Series(labels).value_counts()).to_numpy()
    sortie.loc[valide] = tailles
    return sortie
def whipple(ages, borne_basse=23, borne_haute=62):
    a = pd.to_numeric(pd.Series(ages), errors="coerce").dropna()
    a = a[(a >= borne_basse) & (a <= borne_haute)]
    if len(a) == 0:
        return np.nan
    termines_05 = (a % 5 == 0).sum()
    return 100 * termines_05 / (len(a) / 5)
