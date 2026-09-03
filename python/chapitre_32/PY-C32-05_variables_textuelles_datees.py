# PY-C32-05 — variables textuelles datées
# Chapitre 32 — Cas 14 — Ce que vos clients écrivent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
DATE_REF = pd.Timestamp("2025-10-01")
clients_360 = pd.read_csv("clients_360.csv")
passe = verb[(verb.date < DATE_REF) &
             (verb.date >= DATE_REF - pd.Timedelta(days=365))]
# une colonne par theme : intensite cumulee sur 12 mois
pivot = (passe.pivot_table(index="client_id", columns="theme",
                           values="intensite", aggfunc="sum")
              .add_prefix("theme_").fillna(0))
# variables de forme, souvent aussi predictives que le contenu
forme = passe.groupby("client_id").agg(
    nb_verbatims=("texte", "size"),
    long_moyenne=("texte", lambda s: s.str.len().mean()),
    part_majuscules=("texte", lambda s: s.str.count(r"[A-Z]").sum()
                                        / max(s.str.len().sum(), 1)),
    dernier_verbatim_j=("date", lambda s: (DATE_REF - s.max()).days))
clients_360 = clients_360.join(pivot, on="client_id").join(forme, on="client_id")
