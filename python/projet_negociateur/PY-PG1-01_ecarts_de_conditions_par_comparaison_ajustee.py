# PY-PG1-01 — écarts de conditions par comparaison ajustée
# Projet Negociateur
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd, numpy as np
import statsmodels.formula.api as smf
acc = pd.read_parquet("accords_fournisseurs.parquet")
if (acc.volume_annuel < 0).any():
    raise ValueError("volume_annuel doit etre positif ou nul")
# On modelise la condition observee par ce qui la justifie legitimement.
# Le residu est l ecart non explique : c est lui qui interesse le metier.
modele = smf.ols(
    "taux_remise ~ np.log1p(volume_annuel) + C(categorie) + duree_accord "
    "+ taux_service + part_marque_nationale + C(exercice)",
    data=acc).fit()
acc["attendu"] = modele.fittedvalues
acc["ecart"]   = acc.taux_remise - acc.attendu
# intervalle de prediction : on ne signale que les ecarts robustes
pred = modele.get_prediction(acc).summary_frame(alpha=0.10)
acc["borne_basse"] = pred["obs_ci_lower"]
acc["signale"] = acc.taux_remise < acc.borne_basse
# priorisation : ecart converti en euros, pas en points
ecart_points = (acc.attendu - acc.taux_remise).clip(lower=0)
acc["enjeu_euros"] = ecart_points / 100 * acc.volume_annuel
top = (acc[acc.signale]
       .sort_values("enjeu_euros", ascending=False)
       .loc[:, ["fournisseur", "categorie", "taux_remise",
                "attendu", "enjeu_euros", "negociateur"]])
