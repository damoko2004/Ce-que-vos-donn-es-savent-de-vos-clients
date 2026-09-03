# PY-C09-01 — K-means avec choix de k
# Chapitre 9 — K-means : créer rapidement des groupes
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
Z = acp.transform(X)[:, :3]        # les trois axes retenus au chapitre 8
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(Z)
    print(k, "inertie", round(km.inertia_),
          "silhouette", round(silhouette_score(
              Z, km.labels_, sample_size=min(3_000, len(Z)),
              random_state=42), 3))
km = KMeans(n_clusters=5, n_init=20, random_state=42).fit(Z)
df["cluster"] = km.labels_
print(df.cluster.value_counts().sort_index())
