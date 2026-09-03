# PY-PG3-02 — du score heuristique au modèle supervisé
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from sklearn.ensemble import HistGradientBoostingClassifier
POIDS = {"duree": .25, "uniformite": .20, "gps": .20,
         "coherence": .15, "arrondi": .10, "ecart_enqueteur": .10}
def score_heuristique(d):
    """Priorisation en attendant des cas controles. Pas une probabilite."""
    manquantes = set(POIDS) - set(d.columns)
    if manquantes:
        raise ValueError(f"signaux manquants: {sorted(manquantes)}")
    return sum(p * d[k].clip(0, 1) for k, p in POIDS.items()) * 100
def modele_supervise(controles):
    """Entraine seulement quand les contre-appels contiennent deux classes."""
    colonnes = list(POIDS) + ["heure_debut", "rang_dans_journee",
                              "nb_corrections", "distance_grappe_m"]
    manquantes = set(colonnes + ["invalide"]) - set(controles.columns)
    if manquantes:
        raise ValueError(f"colonnes manquantes: {sorted(manquantes)}")
    X = controles[colonnes]
    y = controles["invalide"]
    if y.dropna().nunique() < 2:
        raise ValueError("modele SurveyOps impossible : une seule classe observee")
    if len(controles) < 50:
        raise ValueError("trop peu de controles valides pour entrainer le modele")
    m = HistGradientBoostingClassifier(
            max_iter=250, class_weight="balanced", random_state=42)
    m.fit(X, y)
    return m
