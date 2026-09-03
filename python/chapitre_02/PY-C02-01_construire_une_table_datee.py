# PY-C02-01 — construire une table datée
# Chapitre 2 — Construire une vue client 360°
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
DATE_REF = pd.Timestamp("2025-10-01")
HORIZON  = pd.Timedelta(days=90)
cmd = pd.read_csv("commandes.csv", parse_dates=["date_commande"])
# passé strict : tout ce qui précède la date de référence
passe = cmd[cmd.date_commande < DATE_REF]
fenetre = passe[passe.date_commande >= DATE_REF - pd.Timedelta(days=365)]
agg = fenetre.groupby("client_id").agg(
    nb_achats_12m=("montant", "size"),
    ca_12m=("montant", "sum"),
    marge_12m=("marge", "sum"),
    derniere_cmd=("date_commande", "max"),
)
agg["recence_jours"] = (DATE_REF - agg.derniere_cmd).dt.days
agg["panier_moyen"] = agg.ca_12m / agg.nb_achats_12m
# futur strict : sert uniquement à fabriquer la cible
futur = cmd[(cmd.date_commande >= DATE_REF) &
            (cmd.date_commande <  DATE_REF + HORIZON)]
actifs_futurs = set(futur.client_id)
agg["churn_90j"] = (~agg.index.isin(actifs_futurs)).astype(int)
