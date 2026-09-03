# PY-C36-01 — indexation du corpus documentaire
# Chapitre 36 — Cas 18 — Un assistant de réponse fondé sur vos propres données
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sentence_transformers import SentenceTransformer
import numpy as np, pandas as pd, faiss
modele = SentenceTransformer("intfloat/multilingual-e5-base")
# 1. decouper : des passages courts, avec chevauchement
def decouper(texte, taille=600, chevauchement=120):
    if taille <= 0 or not 0 <= chevauchement < taille:
        raise ValueError("exiger taille > 0 et 0 <= chevauchement < taille")
    mots, blocs, i = str(texte).split(), [], 0
    while i < len(mots):
        blocs.append(" ".join(mots[i:i + taille]))
        i += taille - chevauchement
    return blocs
docs = pd.read_parquet("intranet.parquet")
passages = []
for _, d in docs.iterrows():
    for j, b in enumerate(decouper(d.contenu)):
        if b.strip():
            passages.append({"doc_id": d.doc_id, "titre": d.titre,
                             "maj": d.derniere_maj, "bloc": j, "texte": b})
psg = pd.DataFrame(passages,
                   columns=["doc_id", "titre", "maj", "bloc", "texte"])
if psg.empty:
    raise ValueError("corpus RAG vide : indexation interrompue, aucun index remplace")
# 2. indexer. E5 attend explicitement les prefixes passage/query.
passages_prefixes = ["passage: " + t for t in psg.texte.tolist()]
V = modele.encode(passages_prefixes, normalize_embeddings=True)
if V.ndim != 2 or V.shape[0] != len(psg):
    raise RuntimeError("embeddings incoherents avec le nombre de passages")
index = faiss.IndexFlatIP(V.shape[1])
index.add(V.astype("float32"))
