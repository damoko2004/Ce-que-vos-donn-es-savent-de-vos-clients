# PY-C32-04 — classer automatiquement une réclamation entrante
# Chapitre 32 — Cas 14 — Ce que vos clients écrivent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
annote = verb[verb.service_destinataire.notna()].copy()
if annote.empty or annote.service_destinataire.nunique() < 2:
    raise ValueError("au moins deux services et des reclamations annotees sont requis")
min_classe = int(annote.service_destinataire.value_counts().min())
cv_n = min(5, min_classe)
if cv_n < 2:
    raise ValueError("chaque service doit avoir au moins deux exemples annotes")
clf = make_pipeline(
    TfidfVectorizer(min_df=5, ngram_range=(1, 2)),
    LogisticRegression(max_iter=1000, class_weight="balanced"))
cv = StratifiedKFold(n_splits=cv_n, shuffle=True, random_state=42)
scores = cross_val_score(clf, annote.clean, annote.service_destinataire,
                         cv=cv, scoring="f1_macro")
print("F1 macro :", scores.mean().round(3))
clf.fit(annote.clean, annote.service_destinataire)
nouveaux = verb[verb.service_destinataire.isna()].copy()
if nouveaux.empty:
    confiance = pd.Series(dtype=float, index=nouveaux.index)
    auto = pd.Series(dtype=bool, index=nouveaux.index)
    humain = ~auto
else:
    p = clf.predict_proba(nouveaux.clean)
    confiance = pd.Series(p.max(axis=1), index=nouveaux.index)
    auto = confiance >= 0.75
    humain = ~auto
