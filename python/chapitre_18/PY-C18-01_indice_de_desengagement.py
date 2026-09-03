# PY-C18-01 — indice de désengagement
# Chapitre 18 — Cas 4 — L’attrition silencieuse
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
f = (flux.pivot_table(index="client_id", columns="mois",
                      values="credit", aggfunc="sum")
         .fillna(0).sort_index(axis=1))
if f.shape[1] < 12:
    raise ValueError("au moins 12 mois d historique sont requis")
recent = f.iloc[:, -6:].sum(axis=1)
anterieur = f.iloc[:, -12:-6].sum(axis=1)
baisse = 1 - recent / anterieur.replace(0, np.nan)
def indexer_client(d):
    return d.set_index("client_id") if "client_id" in d.columns else d
conn_i = indexer_client(conn).reindex(f.index)
ops_i = indexer_client(ops).reindex(f.index)
desengagement = pd.DataFrame(index=f.index)
desengagement["baisse_flux"] = baisse.clip(0, 1).fillna(0)
desengagement["sans_appli"] = (
    conn_i["jours_depuis_derniere"].gt(90).fillna(False).astype(int))
desengagement["sans_operation"] = (
    ops_i["jours_depuis_derniere_volontaire"].gt(60).fillna(False).astype(int))
desengagement["indice"] = (0.50 * desengagement.baisse_flux
                            + 0.25 * desengagement.sans_appli
                            + 0.25 * desengagement.sans_operation)
