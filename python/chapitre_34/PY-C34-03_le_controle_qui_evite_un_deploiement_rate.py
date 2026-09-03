# PY-C34-03 — le contrôle qui évite un déploiement raté
# Chapitre 34 — Cas 16 — Ce que montrent vos images produits
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
# Le controle par fournisseur se fait sur un attribut effectivement publie.
attribut = next((a for a in ATTRIBUTS if seuils.get(a) is not None), None)
if attribut is None:
    raise RuntimeError("aucun attribut n atteint le seuil de publication")
pos = positions[attribut]
d = annotees.loc[pos, ["fournisseur", attribut]].copy()
p = proba[attribut]
conf = p.max(axis=1)
pred = classes[attribut][p.argmax(axis=1)]
d["publie"] = conf >= seuils[attribut]
d["correct"] = pred == d[attribut].to_numpy()
perf = (d[d.publie].groupby("fournisseur")
          .agg(n=("correct", "size"), precision=("correct", "mean"))
          .query("n >= 40").sort_values("precision"))
print(perf.head(10))
ECART_MAX_FOURNISSEUR = 0.08   # coherent avec le seuil de deploiement du cas
if len(perf) >= 2:
    ecart = perf.precision.max() - perf.precision.min()
    assert ecart <= ECART_MAX_FOURNISSEUR, (
        f"ecart inter-fournisseurs de {ecart:.0%}, non deployable")
