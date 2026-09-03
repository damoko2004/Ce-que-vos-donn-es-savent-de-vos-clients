# PY-C15-02 — K-NN et effet de k
# Chapitre 15 — Arbres, forêts et plus proches voisins
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.neighbors import KNeighborsClassifier
Xtr_p, Xte_p = prep.fit_transform(Xtr), prep.transform(Xte)
def sous_echantillon_stratifie(X, y, n_max, seed=42):
    """K-NN sert ici de comparaison pedagogique, pas de calcul massif."""
    if len(y) <= n_max:
        return X, np.asarray(y)
    s = StratifiedShuffleSplit(n_splits=1, train_size=n_max, random_state=seed)
    idx, _ = next(s.split(np.zeros(len(y)), y))
    return X[idx], np.asarray(y)[idx]
Xtr_knn, ytr_knn = sous_echantillon_stratifie(Xtr_p, ytr, 15_000)
Xte_knn, yte_knn = sous_echantillon_stratifie(Xte_p, yte, 5_000)
for k in [1, 3, 5, 10, 25, 50, 100]:
    knn = KNeighborsClassifier(n_neighbors=k, weights="distance", n_jobs=-1)
    knn.fit(Xtr_knn, ytr_knn)
    auc = roc_auc_score(yte_knn, knn.predict_proba(Xte_knn)[:, 1])
    print(f"k={k:4d}  AUC={auc:.3f}")
