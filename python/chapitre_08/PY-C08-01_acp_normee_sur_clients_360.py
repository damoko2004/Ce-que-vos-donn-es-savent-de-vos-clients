# PY-C08-01 — ACP normée sur clients_360
# Chapitre 8 — Réduire la complexité avec l’analyse en composantes principales
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
num = ["anciennete_mois", "nb_achats_12m", "ca_12m", "panier_moyen",
       "nb_visites_90j", "nb_contacts_service", "recence_jours",
       "remise_moyenne", "satisfaction_10", "nb_categories"]
X = StandardScaler().fit_transform(df[num].fillna(df[num].median()))
acp = PCA().fit(X)
var = acp.explained_variance_ratio_
for i, (vp, r) in enumerate(zip(acp.explained_variance_, var), 1):
    print(f"Axe {i}: valeur propre {vp:.2f}  variance {r:.1%}"
          f"  cumul {var[:i].sum():.1%}")
import numpy as np
# ATTENTION AU VOCABULAIRE. components_ contient les vecteurs propres
# (les "loadings"), pas les contributions au sens de FactoMineR.
# Trois objets distincts, souvent confondus :
loadings = acp.components_[:2].T                       # vecteurs propres
coord    = loadings * np.sqrt(acp.explained_variance_[:2])   # coordonnees
cos2     = coord ** 2                                  # qualite de repr.
contrib  = cos2 / cos2.sum(axis=0) * 100               # contributions, en %
tableau = pd.DataFrame(
    {"coord_axe1": coord[:, 0], "cos2_axe1": cos2[:, 0],
     "contrib_axe1_pct": contrib[:, 0]}, index=num)
print(tableau.round(2).sort_values("contrib_axe1_pct", ascending=False))
# coord est ce que trace le cercle des correlations de FactoMineR :
# c est cet objet, et non components_, qu il faut comparer entre R et Python.
