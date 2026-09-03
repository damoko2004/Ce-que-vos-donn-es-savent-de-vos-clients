# PY-C10-02 — équivalent
# Chapitre 10 — Classification hiérarchique et segmentation mixte
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import numpy as np
# CAH de lecture sur un echantillon reproductible : O(n^2) en memoire.
rng = np.random.default_rng(42)
idx = rng.choice(len(Z), size=min(5000, len(Z)), replace=False)
Z_cah = Z[idx]
arbre = linkage(Z_cah, method="ward")
plt.figure(figsize=(11, 4))
dendrogram(arbre, no_labels=True, color_threshold=None)
plt.title("Dendrogramme de Ward - echantillon")
plt.show()
classes_echantillon = fcluster(arbre, t=5, criterion="maxclust")
# Ne jamais recopier ces 5 000 classes sur les 80 000 clients :
# l affectation complete se fait ensuite par segmentation mixte.
