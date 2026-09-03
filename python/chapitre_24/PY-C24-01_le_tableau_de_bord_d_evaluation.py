# PY-C24-01 — le tableau de bord d’évaluation
# Chapitre 24 — Choisir les bonnes métriques
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.metrics import (roc_auc_score, average_precision_score,
                             confusion_matrix, precision_recall_curve)
import numpy as np
def evaluer(y, p, cout_contact=2.0, marge_perdue=45.0):
    print("AUC          :", round(roc_auc_score(y, p), 3))
    print("Gini         :", round(2 * roc_auc_score(y, p) - 1, 3))
    print("AP (PR-AUC)  :", round(average_precision_score(y, p), 3))
    # seuil optimal par le cout metier, pas par defaut
    seuils = np.linspace(0.01, 0.9, 200)
    gains = []
    for s in seuils:
        pred = (p >= s).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        gain = tp * marge_perdue * 0.30 - (tp + fp) * cout_contact
        gains.append(gain)
    best = seuils[int(np.argmax(gains))]
    print("Seuil optimal :", round(best, 3),
          " gain estime :", round(max(gains)))
    return best
