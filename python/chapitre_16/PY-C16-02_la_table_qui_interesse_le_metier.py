# PY-C16-02 — la table qui intéresse le métier
# Chapitre 16 — Cas 2 — Le score d’attrition à 90 jours
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
def table_deciles(y_true, proba, n=10):
    d = pd.DataFrame({"y": np.asarray(y_true), "p": np.asarray(proba)})
    d["decile"] = pd.qcut(d.p.rank(method="first", ascending=False),
                          n, labels=range(1, n + 1)).astype(int)
    base = d.y.mean()
    t = d.groupby("decile", observed=True).agg(
        clients=("y", "size"), departs=("y", "sum"), taux=("y", "mean"))
    t["lift"] = (t.taux / base).round(2)
    t["cumul_departs"] = t.departs.cumsum() / max(d.y.sum(), 1)
    return t.round(3)
print(table_deciles(yte_churn, p_churn))
