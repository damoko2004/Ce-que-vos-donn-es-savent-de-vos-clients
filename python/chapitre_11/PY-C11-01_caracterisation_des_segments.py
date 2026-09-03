# PY-C11-01 — caractérisation des segments
# Chapitre 11 — Cas 1 — NovaRetail : des clusters aux segments actionnables
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
# Le cas 1 travaille sur les clients actifs et applique exactement la chaine
# decrite dans le texte : log des montants, standardisation, 3 axes, k=5.
actifs = df.loc[df.nb_achats_12m >= 1].copy()
num = ["anciennete_mois", "nb_achats_12m", "ca_12m", "panier_moyen",
       "nb_visites_90j", "nb_contacts_service", "recence_jours",
       "remise_moyenne", "satisfaction_10", "nb_categories"]
X = actifs[num].copy()
for v in ["ca_12m", "panier_moyen"]:
    X[v] = np.log1p(X[v].clip(lower=0))
Z0 = StandardScaler().fit_transform(X)
Z = PCA(n_components=3, random_state=42).fit_transform(Z0)
actifs["cluster"] = KMeans(n_clusters=5, n_init=20, random_state=42).fit_predict(Z)
profil = actifs.groupby("cluster")[num].mean()
moyenne = actifs[num].mean()
ecart = ((profil - moyenne) / moyenne.replace(0, np.nan) * 100).round(0)
for c in ecart.index:
    top = ecart.loc[c].abs().sort_values(ascending=False).head(3).index
    print(f"--- Segment {c}  (n={(actifs.cluster == c).sum()})")
    for v in top:
        print(f"    {v:22s} {ecart.loc[c, v]:+.0f} pour cent")
