# PY-C32-02 — découvrir les thèmes sans les connaître
# Chapitre 32 — Cas 14 — Ce que vos clients écrivent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.decomposition import NMF
import numpy as np
nmf = NMF(n_components=8, init="nndsvd", random_state=42, max_iter=400)
W = nmf.fit_transform(X)          # poids du theme dans chaque texte
H = nmf.components_               # poids du terme dans chaque theme
termes = np.array(tfidf.get_feature_names_out())
for k in range(nmf.n_components):
    top = termes[H[k].argsort()[::-1][:10]]
    print(f"Theme {k} : " + ", ".join(top))
verb["theme"] = W.argmax(axis=1)
verb["intensite"] = W.max(axis=1)
