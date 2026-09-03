# PY-C17-02 — calibration, indispensable ici
# Chapitre 17 — Cas 3 — Du gratuit au payant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
modele_conversion.fit(Xtr_conv, ytr_conv)
p_brut = modele_conversion.predict_proba(Xte_conv)[:, 1]
cal = CalibratedClassifierCV(modele_conversion, method="isotonic", cv=5)
cal.fit(Xtr_conv, ytr_conv)
p_cal = cal.predict_proba(Xte_conv)[:, 1]
print("Brier brut     :", round(brier_score_loss(yte_conv, p_brut), 4))
print("Brier calibre  :", round(brier_score_loss(yte_conv, p_cal), 4))
calib = pd.DataFrame({"predit": p_cal, "observe": yte_conv.to_numpy()})
calib["bin"] = pd.qcut(calib["predit"], 10, duplicates="drop")
print(calib.groupby("bin", observed=True)[["predit", "observe"]].mean().round(3))
