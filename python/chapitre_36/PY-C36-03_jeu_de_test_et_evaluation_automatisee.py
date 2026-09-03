# PY-C36-03 — jeu de test et évaluation automatisée
# Chapitre 36 — Cas 18 — Un assistant de réponse fondé sur vos propres données
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
# 180 reclamations reelles, avec la reponse validee et le document source
ref = pd.read_json("evaluation/jeu_test.json")
def rappel_at_k(k=6):
    if ref.empty:
        raise ValueError("jeu de test vide")
    ok = 0
    for _, ex in ref.iterrows():
        trouves = set(rechercher(ex.question, k=k).doc_id)
        ok += int(ex.doc_source in trouves)
    return ok / len(ref)
def taux_non_source(reponses):
    """Part des phrases factuelles depourvues de citation.
    Un taux, et non un comptage : comparable entre jeux de tailles
    differentes."""
    import re
    factuelles = non_sourcees = 0
    for r in reponses:
        if not r:
            continue
        for phrase in re.split(r"(?<=[.!?])\s+", r):
            if len(phrase) <= 40:      # salutations, formules de politesse
                continue
            factuelles += 1
            if not re.search(r"\[\d+\]", phrase):
                non_sourcees += 1
    return non_sourcees / factuelles if factuelles else 0.0
print("Rappel a 6 :", round(rappel_at_k(), 3))
