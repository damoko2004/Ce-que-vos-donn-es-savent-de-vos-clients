# PY-C34-01 — extraire une représentation, entraîner une tête légère
# Chapitre 34 — Cas 16 — Ce que montrent vos images produits
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd, torch
from pathlib import Path
from torch import nn
from PIL import Image
from torchvision.models import resnet50, ResNet50_Weights
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
# Dependances explicites du cas : aucune variable n est supposee exister
# dans la session precedente.
catalogue = pd.read_csv("images/catalogue_images.csv")
annotees = pd.read_csv("images/annotations_images.csv")
requis_catalogue = {"reference", "chemin", "fournisseur"}
ATTRIBUTS = ["couleur", "matiere", "motif", "saison",
             "type_col", "finition", "style", "usage"]
if not requis_catalogue.issubset(catalogue.columns):
    message = f"catalogue incomplet: {requis_catalogue - set(catalogue.columns)}"
    raise ValueError(message)
if not ({"reference", "fournisseur"} | set(ATTRIBUTS)).issubset(annotees.columns):
    raise ValueError("annotations_images.csv ne contient pas les colonnes attendues")
if not set(annotees.reference).issubset(set(catalogue.reference)):
    raise ValueError("certaines references annotees sont absentes du catalogue")
manquantes = [c for c in catalogue.chemin if not Path(c).is_file()]
if manquantes:
    message = f"{len(manquantes)} image(s) introuvable(s), ex. {manquantes[0]}"
    raise FileNotFoundError(message)
poids = ResNet50_Weights.DEFAULT
pretraiter = poids.transforms()
modele_image = resnet50(weights=poids)
modele_image.fc = nn.Identity()
modele_image.eval()
@torch.no_grad()
def representer(chemins, lot=64):
    if not chemins:
        raise ValueError("aucune image a representer")
    sorties = []
    for i in range(0, len(chemins), lot):
        images = torch.stack([pretraiter(Image.open(c).convert("RGB"))
                              for c in chemins[i:i + lot]])
        sorties.append(modele_image(images).cpu().numpy())
    return np.vstack(sorties)
emb_images = representer(catalogue.chemin.tolist())
emb_ref = (pd.DataFrame(emb_images)
             .assign(reference=catalogue.reference.values)
             .groupby("reference").mean())
annotees = annotees.reset_index(drop=True)
def tete(attribut, donnees):
    d = donnees.dropna(subset=[attribut]).copy()
    X = emb_ref.loc[d.reference].to_numpy()
    y = d[attribut].to_numpy()
    groupes = d.reference.to_numpy()
    if len(np.unique(y)) < 2:
        raise ValueError(f"{attribut}: une seule modalite annotee")
    groupes_par_classe = d.groupby(attribut).reference.nunique()
    n_splits = min(5, int(groupes_par_classe.min()))
    if n_splits < 2:
        raise ValueError(f"{attribut}: pas assez de references par classe pour valider")
    clf = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced")
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
    proba = cross_val_predict(clf, X, y, cv=cv, groups=groupes,
                              method="predict_proba")
    clf.fit(X, y)
    return d.index.to_numpy(), clf, proba, clf.classes_
modeles, positions, proba, classes = {}, {}, {}, {}
for attribut in ATTRIBUTS:
    positions[attribut], modeles[attribut], proba[attribut], classes[attribut] = tete(
        attribut, annotees)
