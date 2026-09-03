# PY-C33-01 — nettoyage et sessionnisation
# Chapitre 33 — Cas 15 — Ce que vos clients parcourent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd, numpy as np
log = pd.read_parquet("weblog.parquet")
log["horodatage"] = pd.to_datetime(log["horodatage"], utc=True, errors="coerce")
log = log.dropna(subset=["visiteur_id", "horodatage"])
log = log[log.code_reponse.between(200, 299)]
log = log[~log.url.str.contains(r"\.(css|js|png|jpg|svg|woff)$", regex=True, na=False)]
MOTIFS_BOT = r"(?:bot|crawler|spider|curl|wget|headless|python-requests)"
log = log[~log.user_agent.fillna("").str.lower().str.contains(MOTIFS_BOT, regex=True)]
log = log.sort_values(["visiteur_id", "horodatage"])
log["ecart"] = log.groupby("visiteur_id").horodatage.diff().dt.total_seconds()
cadence = log.groupby("visiteur_id").ecart.agg(["median", "std"])
suspects = cadence[(cadence["median"] < 1.5) & (cadence["std"] < 0.8)].index
log = log[~log.visiteur_id.isin(suspects)].copy()
# Recalcul obligatoire apres suppression des robots : l ecart precedent
# pouvait etre mesure par rapport a une requete qui vient d etre retiree.
log = log.sort_values(["visiteur_id", "horodatage"])
log["ecart"] = log.groupby("visiteur_id").horodatage.diff().dt.total_seconds()
log["nouvelle_session"] = log["ecart"].isna() | (log["ecart"] > 1800)
log["session_id"] = log.groupby("visiteur_id").nouvelle_session.cumsum()
