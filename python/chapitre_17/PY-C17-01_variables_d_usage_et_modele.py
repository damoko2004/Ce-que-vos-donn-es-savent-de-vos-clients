# PY-C17-01 — variables d’usage et modèle
# Chapitre 17 — Cas 3 — Du gratuit au payant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
usage = pd.read_csv("usage_j0_j30.csv")
comptes = pd.read_csv("comptes.csv", parse_dates=["date_inscription"])
conversions = pd.read_csv("conversions.csv")
if "compte_id" not in conversions:
    raise ValueError("conversions.csv doit contenir compte_id")
# agregats sur les 30 premiers jours uniquement
feat = usage.groupby("compte_id").agg(
    jours_actifs=("date", "nunique"),
    fonctions_activees=("fonction", "nunique"),
    volume_traite=("volume", "sum"),
    invitations=("invitation", "sum"),
    integrations=("integration", "nunique"),
)
feat["regularite"] = feat.jours_actifs / 30
base = feat.join(comptes.set_index("compte_id")[[
    "canal_acquisition", "taille_entreprise", "pays", "date_inscription"]])
base["cible"] = base.index.isin(set(conversions.compte_id)).astype(int)
base = base.dropna(subset=["date_inscription"])
NUM = ["jours_actifs", "fonctions_activees", "volume_traite",
       "invitations", "integrations", "regularite"]
CAT = ["canal_acquisition", "taille_entreprise", "pays"]
# Validation chronologique par cohorte d inscription : les comptes les plus
# recents constituent le test, sans reutiliser le futur dans l apprentissage.
ordre = base.date_inscription.sort_values()
cut = ordre.iloc[max(1, int(0.75 * len(ordre))) - 1]
train = base[base.date_inscription <= cut]
test = base[base.date_inscription > cut]
if test.empty or train.cible.nunique() < 2 or test.cible.nunique() < 2:
    raise ValueError("cohortes insuffisantes pour une validation binaire")
Xtr_conv, ytr_conv = train[NUM + CAT], train["cible"]
Xte_conv, yte_conv = test[NUM + CAT], test["cible"]
prep_conv = ColumnTransformer([
    ("num", StandardScaler(), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT)])
modele_conversion = Pipeline([
    ("prep", prep_conv),
    ("clf", HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.05,
        class_weight="balanced", random_state=42))])
