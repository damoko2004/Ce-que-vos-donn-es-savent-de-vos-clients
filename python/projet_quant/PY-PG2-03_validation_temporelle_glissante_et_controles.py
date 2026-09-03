# PY-PG2-03 — validation temporelle glissante et contrôles
# Projet Quant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
def gini(y, p):
    return 2 * roc_auc_score(y, p) - 1
def backtest_glissant(panel, modele, dates):
    """On apprend sur le passe, on teste sur l avenir. Jamais l inverse."""
    lignes = []
    for i in range(3, len(dates)):
        train = panel[panel.cohorte.isin(dates[:i])]
        test = panel[panel.cohorte == dates[i]]
        if (train.empty or train.defaut.nunique() < 2 or
                test.empty or test.defaut.nunique() < 2):
            continue
        m = modele.fit(train.drop(columns=["defaut", "cohorte"]), train.defaut)
        p = m.predict_proba(test.drop(columns=["defaut", "cohorte"]))[:, 1]
        lignes.append({"cohorte": dates[i], "n": len(test),
                       "gini": round(gini(test.defaut, p), 3),
                       "pd_moyenne_predite": round(p.mean(), 4),
                       "taux_defaut_observe": round(test.defaut.mean(), 4),
                       "ecart_calibration": round(p.mean() - test.defaut.mean(), 4)})
    return pd.DataFrame(lignes)
def psi(reference, courant, bins=10):
    """PSI. Renvoie NaN si la reference est constante."""
    reference, courant = np.asarray(reference), np.asarray(courant)
    reference = reference[np.isfinite(reference)]
    courant = courant[np.isfinite(courant)]
    if len(reference) == 0 or len(courant) == 0 or np.unique(reference).size < 2:
        return np.nan
    coupures = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    coupures[0], coupures[-1] = -np.inf, np.inf
    r = np.histogram(reference, coupures)[0] / len(reference)
    c = np.histogram(courant, coupures)[0] / len(courant)
    r, c = np.clip(r, 1e-6, None), np.clip(c, 1e-6, None)
    return float(np.sum((c - r) * np.log(c / r)))
