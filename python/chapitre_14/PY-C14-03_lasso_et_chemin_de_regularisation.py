# PY-C14-03 — lasso et chemin de régularisation
# Chapitre 14 — Régression logistique et modèles linéaires
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
Xtr_lasso = prep.fit_transform(Xtr)
noms_lasso = prep.get_feature_names_out()
# API explicite et durable : LogisticRegression + recherche de C.
# On evite de lier le livre a une classe CV specialisee dont l API evolue.
base_lasso = LogisticRegression(
    penalty="l1", solver="liblinear", class_weight="balanced", max_iter=2000)
lasso = GridSearchCV(
    base_lasso,
    param_grid={"C": np.logspace(-3, 2, 20)},
    cv=5, scoring="roc_auc", n_jobs=-1, refit=True)
lasso.fit(Xtr_lasso, ytr)
coef = lasso.best_estimator_.coef_[0]
retenues = [n for n, c in zip(noms_lasso, coef) if abs(c) > 1e-6]
print("C retenu :", lasso.best_params_["C"])
print(len(retenues), "variables retenues sur", len(noms_lasso))
print(retenues)
