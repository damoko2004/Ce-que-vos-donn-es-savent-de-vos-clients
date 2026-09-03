# PY-C40-05 — calibrer un juge avant de s’en servir
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
# 200 sorties notees a la main par deux experts metier
ref = pd.read_json("eval/annotations_humaines.json")
ref["juge"] = ref.sortie.map(lambda s: juge_llm(s, criteres=BAREME))
accord = (ref.juge == ref.humain).mean()
kappa  = cohen_kappa_score(ref.humain, ref.juge)
print(f"Accord brut {accord:.1%}  kappa {kappa:.2f}")
# Le detail compte plus que le taux global : ou le juge se trompe-t-il ?
print(confusion_matrix(ref.humain, ref.juge, labels=["conforme", "non conforme"]))
# Cas typique : le juge est indulgent sur les affirmations non sourcees.
desaccords = ref[ref.juge != ref.humain]
print(desaccords.groupby("motif_humain").size().sort_values(ascending=False))
if kappa < 0.60:
    raise SystemExit("Juge non calibre : notation humaine maintenue")
