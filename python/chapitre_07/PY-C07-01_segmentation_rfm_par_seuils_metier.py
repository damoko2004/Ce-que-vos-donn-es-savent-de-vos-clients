# PY-C07-01 — segmentation RFM par seuils métier
# Chapitre 7 — Segmenter sans algorithme : PMG et RFM
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
df = pd.read_csv("clients_360.csv")
# Des seuils choisis avec le metier, et non des quintiles : la taille
# des segments doit refleter les clients, pas le decoupage.
SEUIL_DORMANT, SEUIL_RECENT, SEUIL_FIDELE, SEUIL_NOUVEAU = 270, 90, 4, 12
def segment(r):
    if r.recence_jours > SEUIL_DORMANT:
        return "Endormis"
    if r.recence_jours <= SEUIL_RECENT and r.nb_achats_12m >= SEUIL_FIDELE:
        return "Champions"
    if r.anciennete_mois <= SEUIL_NOUVEAU and r.nb_achats_12m < SEUIL_FIDELE:
        return "Nouveaux"
    if r.recence_jours > SEUIL_RECENT and r.nb_achats_12m >= SEUIL_FIDELE:
        return "A reconquerir"
    return "Reguliers"
df["segment_rfm"] = df.apply(segment, axis=1)
t = (df.groupby("segment_rfm")
       .agg(clients=("client_id", "size"), ca=("ca_12m", "sum"))
       .assign(part_ca=lambda d: (d.ca / d.ca.sum() * 100).round(1))
       .sort_values("clients", ascending=False))
print(t)
# Valeurs de reference de l edition
assert t.loc["Endormis", "clients"] == 23_654
assert abs(t.loc["Endormis", "part_ca"] - 5.4) < 0.1
