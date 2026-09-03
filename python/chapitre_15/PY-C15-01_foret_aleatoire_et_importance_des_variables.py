# PY-C15-01 — forêt aléatoire et importance des variables
# Chapitre 15 — Arbres, forêts et plus proches voisins
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
rf = Pipeline([
    ("prep", prep),
    ("clf", RandomForestClassifier(
        n_estimators=500, min_samples_leaf=20,
        class_weight="balanced_subsample", n_jobs=-1, random_state=42))])
rf.fit(Xtr, ytr)
proba_rf = rf.predict_proba(Xte)[:, 1]
print("AUC foret =", round(roc_auc_score(yte, proba_rf), 3))
# importance par permutation : plus honnete que l importance native
imp = permutation_importance(rf, Xte, yte, scoring="roc_auc",
                             n_repeats=10, random_state=42)
ordre = imp.importances_mean.argsort()[::-1]
for i in ordre[:8]:
    print(f"{X.columns[i]:22s} {imp.importances_mean[i]:.4f}")
