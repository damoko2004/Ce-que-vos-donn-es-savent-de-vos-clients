# PY-C36-02 — recherche hybride et gabarit de génération contrainte
# Chapitre 36 — Cas 18 — Un assistant de réponse fondé sur vos propres données
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
from rank_bm25 import BM25Okapi
if psg.empty:
    raise ValueError("le corpus ne contient aucun passage")
bm25 = BM25Okapi([t.lower().split() for t in psg.texte])
def rechercher(question, k=6):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question vide")
    if k <= 0:
        raise ValueError("k doit etre positif")
    n_candidats = min(20, len(psg))
    q = modele.encode(["query: " + question],
                      normalize_embeddings=True).astype("float32")
    _, idx_dense = index.search(q, n_candidats)
    idx_lex = np.argsort(bm25.get_scores(question.lower().split()))[::-1][:n_candidats]
    score = {}
    for rang, i in enumerate(idx_dense[0]):
        if i >= 0:
            score[int(i)] = score.get(int(i), 0) + 1 / (60 + rang)
    for rang, i in enumerate(idx_lex):
        score[int(i)] = score.get(int(i), 0) + 1 / (60 + rang)
    retenus = sorted(score, key=score.get, reverse=True)[:min(k, len(score))]
    return psg.iloc[retenus]
GABARIT = """Tu rediges un brouillon de reponse pour un conseiller client.
Regles imperatives :
- Utilise UNIQUEMENT les extraits fournis. Ne complete jamais de memoire.
- Cite le numero de l extrait entre crochets apres chaque affirmation factuelle.
- Si les extraits ne permettent pas de repondre, ecris exactement :
  INFORMATION INSUFFISANTE puis la liste de ce qui manque.
- Ne promets aucun geste commercial qui ne figure pas dans les extraits.
Extraits :
{extraits}
Historique client : {contexte_client}
Reclamation : {question}"""
