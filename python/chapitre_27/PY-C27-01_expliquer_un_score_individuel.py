# PY-C27-01 — expliquer un score individuel
# Chapitre 27 — Interpréter et surveiller les modèles
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd, shap
# Le classifieur est explique sur les variables APRES pretraitement.
Xte_churn_t = prep_churn.transform(Xte_churn)
noms_churn = prep_churn.get_feature_names_out()
expl = shap.TreeExplainer(gb_churn)
valeurs = expl.shap_values(Xte_churn_t)
if isinstance(valeurs, list):
    valeurs = valeurs[-1]
valeurs = np.asarray(valeurs)
if valeurs.ndim == 3:                 # certaines versions ajoutent l axe classe
    valeurs = valeurs[..., -1]
shap.summary_plot(valeurs, Xte_churn_t,
                  feature_names=noms_churn, max_display=12)
i = min(42, len(Xte_churn_t) - 1)
contrib = pd.Series(valeurs[i], index=noms_churn)
contrib = contrib.reindex(contrib.abs().sort_values(ascending=False).index)
for var, c in contrib.head(5).items():
    sens = "augmente" if c > 0 else "diminue"
    print(f"{var:32s} {sens} le score de risque de {abs(c):.3f}")
