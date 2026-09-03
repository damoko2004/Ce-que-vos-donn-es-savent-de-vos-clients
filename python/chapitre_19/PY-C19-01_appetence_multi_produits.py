# PY-C19-01 — appétence multi-produits
# Chapitre 19 — Cas 5, 6 et 7 — Appétence, valeur et satisfaction
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
produits = ["complementaire", "protection_juridique", "assistance"]
base = pd.read_parquet("assurance_appetence.parquet")
base["date_ref"] = pd.to_datetime(base["date_ref"], errors="raise")
dates = sorted(base.date_ref.dropna().unique())
if len(dates) < 2:
    raise ValueError("au moins deux dates de reference sont requises")
train = base[base.date_ref < dates[-1]].copy()
test = base[base.date_ref == dates[-1]].copy()
if train.empty or test.empty:
    raise ValueError("decoupage temporel vide")
exclure = {"client_id", "date_ref", *produits}
features = [c for c in base.columns if c not in exclure]
if not features:
    raise ValueError("aucune variable explicative disponible")
num_app = train[features].select_dtypes(include=np.number).columns.tolist()
cat_app = [c for c in features if c not in num_app]
prep_app = ColumnTransformer([
    ("num", StandardScaler(), num_app),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_app),
], remainder="drop")
scores = {}
for produit in produits:
    y = train[produit].astype(int)
    if y.nunique() < 2:
        raise ValueError(
            f"{produit}: la cible ne contient qu une classe")
    modele = Pipeline([
        ("prep", prep_app),
        ("clf", HistGradientBoostingClassifier(class_weight="balanced",
                                                max_iter=250, random_state=42))])
    modele.fit(train[features], y)
    scores[produit] = modele.predict_proba(test[features])[:, 1]
reco = pd.DataFrame(scores, index=test.client_id.to_numpy())
top3 = reco.apply(lambda r: r.nlargest(3).index.tolist(), axis=1)
