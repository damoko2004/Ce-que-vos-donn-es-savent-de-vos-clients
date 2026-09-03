# PY-C14-01 — régression logistique avec pondération
# Chapitre 14 — Régression logistique et modèles linéaires
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
X, y = df[num + cat], df["churn_90j"]
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)
prep = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
logit = Pipeline([
    ("prep", prep),
    ("clf", LogisticRegression(max_iter=1000,
                              class_weight="balanced"))])
logit.fit(Xtr, ytr)
proba = logit.predict_proba(Xte)[:, 1]
print("AUC =", round(roc_auc_score(yte, proba), 3))
# rapports de cotes, lisibles par le metier
noms = logit.named_steps["prep"].get_feature_names_out()
coefs = logit.named_steps["clf"].coef_[0]
odds = pd.Series(np.exp(coefs), index=noms).sort_values(ascending=False)
print(odds.head(8).round(2))
