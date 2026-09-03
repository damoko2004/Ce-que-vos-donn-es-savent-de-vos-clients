# PY-C34-02 — un seuil par attribut, calibré sur le coût
# Chapitre 34 — Cas 16 — Ce que montrent vos images produits
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
def seuil_publication(y_vrai, proba, classes, precision_visee=0.95):
    """Seuil sur la confiance maximale, valable aussi en multiclasse."""
    y_vrai = np.asarray(y_vrai)
    confiance = proba.max(axis=1)
    prediction = classes[proba.argmax(axis=1)]
    correct = prediction == y_vrai
    meilleur = None
    for seuil in np.unique(confiance):
        publie = confiance >= seuil
        if publie.sum() == 0:
            continue
        precision = correct[publie].mean()
        couverture = publie.mean()
        meilleure = meilleur is None or couverture > meilleur[1]
        if precision >= precision_visee and meilleure:
            meilleur = (float(seuil), float(couverture))
    return meilleur if meilleur is not None else (None, 0.0)
seuils = {}
for attribut in ATTRIBUTS:
    pos = positions[attribut]
    s, couv = seuil_publication(annotees.loc[pos, attribut], proba[attribut],
                                classes[attribut])
    seuils[attribut] = s
    if s is None:
        print(f"{attribut:12s} : non automatisable, reste manuel")
    else:
        print(f"{attribut:12s} : seuil {s:.2f}, couvre {couv:.0%} du catalogue")
