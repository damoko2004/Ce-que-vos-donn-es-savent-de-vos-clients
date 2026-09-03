# PY-C00-01 — la référence que tout modèle doit battre
# Partie IX — Exercice D3, anticiper la demande
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd, numpy as np
def naif_saisonnier(serie, horizon, saison=7):
    if saison <= 0 or len(serie) < saison:
        raise ValueError("la serie doit contenir au moins une saison complete")
    return np.array([serie.iloc[-saison + (h % saison)] for h in range(horizon)])
def backtest_origine_glissante(serie, modele, horizon=14, pas=7, n_origines=26):
    if horizon <= 0 or pas <= 0 or n_origines <= 0:
        raise ValueError("horizon, pas et n_origines doivent etre positifs")
    erreurs = []
    for k in range(n_origines, 0, -1):
        fin = len(serie) - k * pas
        # historique suffisant ET horizon futur complet : jamais de comparaison
        # entre 14 predictions et seulement 7 observations disponibles.
        if fin < 60 or fin + horizon > len(serie):
            continue
        passe, futur = serie.iloc[:fin], serie.iloc[fin:fin + horizon]
        prev = np.asarray(modele(passe, horizon), dtype=float)
        if len(prev) != horizon:
            raise ValueError("le modele doit renvoyer exactement horizon predictions")
        erreurs.append({"origine": serie.index[fin],
                        "mae": np.mean(np.abs(prev - futur.to_numpy())),
                        "biais": np.mean(prev - futur.to_numpy())})
    return pd.DataFrame(erreurs)
