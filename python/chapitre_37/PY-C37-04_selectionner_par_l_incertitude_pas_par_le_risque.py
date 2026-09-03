# PY-C37-04 — sélectionner par l’incertitude, pas par le risque
# Chapitre 37 — Cas 19, 20 et 21 — Apprendre en agissant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.ensemble import RandomForestRegressor
import numpy as np
rf = RandomForestRegressor(n_estimators=400, min_samples_leaf=5,
                          random_state=42).fit(X_hist, y_hist)
def incertitude(X):
    """Desaccord entre arbres : heuristique d incertitude, non calibree."""
    preds = np.stack([a.predict(X) for a in rf.estimators_])
    return preds.std(axis=0)
risque = rf.predict(X_reseau)
consequence = reseau.abonnes_desservis.to_numpy() * reseau.criticite.to_numpy()
enjeu = risque * consequence
incert = incertitude(X_reseau)
CAPACITE = min(200, len(reseau))
n_exploit = int(0.70 * CAPACITE)
n_explore = int(0.20 * CAPACITE)
n_hasard = CAPACITE - n_exploit - n_explore
exploit = np.argsort(enjeu)[::-1][:n_exploit]
restant = np.setdiff1d(np.arange(len(reseau)), exploit)
explore = restant[np.argsort(incert[restant])[::-1][:min(n_explore, len(restant))]]
pool = np.setdiff1d(restant, explore)
rng = np.random.default_rng(42)
hasard = rng.choice(pool, min(n_hasard, len(pool)), replace=False)
tournee = np.concatenate([exploit, explore, hasard])
