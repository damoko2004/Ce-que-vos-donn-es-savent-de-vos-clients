# PY-C35-01 — le test qui autorise tout le reste
# Chapitre 35 — Cas 17 — Refondre un pipeline avec un agent de programmation
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd, numpy as np, pytest
REF = pd.read_parquet("tests/scores_reference_2025_10.parquet")
TOLERANCE = 1e-6
def test_non_regression_scores():
    """Le nouveau pipeline doit reproduire l ancien au bruit numerique pres."""
    from pipeline.scoring import scorer
    obtenu = scorer(date_ref="2025-10-01", echantillon="tests/clients_fige.parquet")
    fusion = REF.merge(obtenu, on="client_id", suffixes=("_ref", "_new"))
    assert len(fusion) == len(REF), "des clients ont disparu ou ete dupliques"
    ecart = (fusion.score_ref - fusion.score_new).abs()
    assert ecart.max() < TOLERANCE, f"ecart max {ecart.max():.2e}"
def test_aucune_variable_posterieure():
    """Garde-fou anti-fuite : aucune source ne depasse la date de reference."""
    from pipeline.features import construire
    tab, sources = construire(date_ref="2025-10-01", retourner_sources=True)
    for nom, date_max in sources.items():
        assert date_max < pd.Timestamp("2025-10-01"), f"fuite sur {nom}"
def test_population_stable():
    """La population scoree reste proche de l artefact de reference versionne."""
    from pipeline.scoring import scorer
    n = len(scorer(date_ref="2025-10-01"))
    n_ref = len(REF)
    assert n_ref > 0, "artefact de reference vide"
    assert abs(n - n_ref) / n_ref < 0.02
