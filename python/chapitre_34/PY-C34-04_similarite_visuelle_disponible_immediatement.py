# PY-C34-04 — similarité visuelle, disponible immédiatement
# Chapitre 34 — Cas 16 — Ce que montrent vos images produits
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
E = normalize(emb_ref.values)
k_defaut = min(11, len(E))
voisins = NearestNeighbors(n_neighbors=k_defaut, metric="cosine").fit(E)
POS = {r: i for i, r in enumerate(emb_ref.index)}
FOURNISSEUR = catalogue.groupby("reference").fournisseur.first()
def semblables(reference, n=10, exclure_meme_fournisseur=True):
    i = POS[reference]
    k = min(len(E), n + 6)
    _, idx = voisins.kneighbors(E[i:i + 1], n_neighbors=k)
    res = [emb_ref.index[j] for j in idx[0] if j != i]
    if exclure_meme_fournisseur:
        f0 = FOURNISSEUR.get(reference)
        res = [r for r in res if FOURNISSEUR.get(r) != f0]
    return res[:n]
