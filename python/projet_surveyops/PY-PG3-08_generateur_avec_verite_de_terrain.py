# PY-PG3-08 — générateur avec vérité de terrain
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
def generer_enquete(n_menages=18_000, n_enqueteurs=75, seed=42,
                    anomalies=None):
    """Rend la collecte simulee et une verite de terrain explicite."""
    taux = anomalies or {"doublon": .010, "entretien_rapide": .030,
                         "gps_reutilise": .020, "uniformite": .015,
                         "age_arrondi": .080}
    rng = np.random.default_rng(seed)
    ids = np.array([f"Q{i:06d}" for i in range(n_menages)])
    collecte = pd.DataFrame({
        "questionnaire": ids,
        "enqueteur": rng.integers(1, n_enqueteurs + 1, n_menages),
        "duree_min": np.maximum(8, rng.normal(34, 8, n_menages)),
        "lat": 4.35 + rng.normal(0, .18, n_menages),
        "lon": 18.56 + rng.normal(0, .18, n_menages),
        "age": rng.integers(18, 80, n_menages),
        "straightlining": np.zeros(n_menages),
    })
    labels = np.full(n_menages, "aucune", dtype=object)
    disponibles = np.arange(n_menages)
    for nom, prop in taux.items():
        n = min(int(prop * n_menages), len(disponibles))
        idx = rng.choice(disponibles, n, replace=False)
        disponibles = np.setdiff1d(disponibles, idx, assume_unique=False)
        labels[idx] = nom
        if nom == "entretien_rapide":
            collecte.loc[idx, "duree_min"] = rng.uniform(5, 11, n)
        elif nom == "gps_reutilise" and n:
            collecte.loc[idx, ["lat", "lon"]] = [4.3667, 18.5833]
        elif nom == "age_arrondi":
            collecte.loc[idx, "age"] = (collecte.loc[idx, "age"] / 5).round() * 5
        elif nom == "doublon" and n:
            pool = np.setdiff1d(np.arange(n_menages), idx)
            src = rng.choice(pool, n, replace=True)
            cols = ["duree_min", "lat", "lon", "age", "straightlining"]
            collecte.loc[idx, cols] = collecte.loc[src, cols].to_numpy()
        elif nom == "uniformite":
            collecte.loc[idx, "straightlining"] = 1.0
    verite = pd.DataFrame({"questionnaire": ids, "anomalie": labels})
    return collecte, verite
def evaluer(alertes, verite):
    vrais = set(verite.loc[verite.anomalie != "aucune", "questionnaire"])
    detectes = set(alertes.questionnaire)
    precision = len(detectes & vrais) / max(len(detectes), 1)
    rappel = len(detectes & vrais) / max(len(vrais), 1)
    return {"precision": round(precision, 3), "rappel": round(rappel, 3)}
collecte, verite = generer_enquete()
assert len(collecte) == len(verite) == 18_000
assert collecte.straightlining.notna().all()
assert set(verite.anomalie) >= {"aucune", "doublon", "entretien_rapide"}
