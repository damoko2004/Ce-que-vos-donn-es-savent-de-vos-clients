# PY-C22-01 — filtrage collaboratif centré objet
# Chapitre 22 — Filtrage collaboratif et voisinage
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
# matrice creuse utilisateurs x objets
M = csr_matrix((inter.poids,
                (inter.user_idx, inter.item_idx)))
# normalisation par utilisateur : evite que les gros acheteurs dominent
from sklearn.preprocessing import normalize
Mn = normalize(M, norm="l2", axis=1)
sim_items = cosine_similarity(Mn.T, dense_output=False)
def recommander(u, n=10):
    vus = M[u].indices
    scores = np.asarray(Mn[u].dot(sim_items).todense()).ravel()
    scores[vus] = -np.inf          # ne pas recommander le deja vu
    return scores.argsort()[::-1][:n]
