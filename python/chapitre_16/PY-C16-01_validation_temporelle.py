# PY-C16-01 — validation temporelle
# Chapitre 16 — Cas 2 — Le score d’attrition à 90 jours
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
panel = pd.read_csv("panel_churn.csv", parse_dates=["date_ref"])
dates = sorted(panel.date_ref.dropna().unique())
if len(dates) < 12:
    raise ValueError("panel_churn.csv doit contenir au moins 12 dates de reference")
train = panel[panel.date_ref.isin(dates[:10])]
test = panel[panel.date_ref.isin(dates[10:])]
Xtr_churn = train.drop(columns=["churn_90j", "date_ref", "id"])
ytr_churn = train.churn_90j.astype(int)
Xte_churn = test.drop(columns=["churn_90j", "date_ref", "id"])
yte_churn = test.churn_90j.astype(int)
if ytr_churn.nunique() < 2 or yte_churn.nunique() < 2:
    raise ValueError("les jeux apprentissage et test doivent contenir les deux classes")
num_churn = Xtr_churn.select_dtypes(include=np.number).columns.tolist()
cat_churn = [c for c in Xtr_churn.columns if c not in num_churn]
prep_churn = ColumnTransformer([
    ("num", StandardScaler(), num_churn),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_churn),
], remainder="drop")
gb_churn = HistGradientBoostingClassifier(
    max_iter=400, learning_rate=0.06, max_leaf_nodes=31,
    l2_regularization=1.0, class_weight="balanced", random_state=42)
modele_churn = Pipeline([("prep", prep_churn), ("clf", gb_churn)])
modele_churn.fit(Xtr_churn, ytr_churn)
p_churn = modele_churn.predict_proba(Xte_churn)[:, 1]
print("AUC =", round(roc_auc_score(yte_churn, p_churn), 3))
