# PY-C37-02 — la boucle mensuelle, avec garde-fous
# Chapitre 37 — Cas 19, 20 et 21 — Apprendre en agissant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
COUTS = np.array([12.0, 8.0, 3.0, 0.0, 22.0])   # euros par offre
TAUX_EXPLORATION = 0.05   # probabilite par client, pas quota deterministe par campagne
def campagne_mensuelle(bandit, clients, contextes):
    if bandit.k != len(COUTS):
        raise ValueError("le nombre d offres doit correspondre au vecteur COUTS")
    rng = getattr(bandit, "rng", np.random.default_rng(42))
    envois = []
    for cid, x in zip(clients, contextes):
        # Avec 5 %, la part realisee fluctue autour de 5 % sur une campagne
        # finie. Si le metier exige exactement 5 %, il faut tirer un quota.
        if rng.random() < TAUX_EXPLORATION:
            offre = int(rng.integers(bandit.k))
            mode = "exploration"
        else:
            offre = bandit.choisir(x)
            mode = "exploitation"
        envois.append({"client": cid, "contexte": x, "offre": offre,
                       "mode": mode, "cout": COUTS[offre],
                       "date": pd.Timestamp.now(tz="UTC")})
    return envois
def integrer_retours(bandit, envois, retours, marge_par_client):
    """Appele 90 jours plus tard, quand la retention est observable."""
    for e in envois:
        retenu = retours.get(e["client"])
        if retenu is None:
            continue
        gain = marge_par_client[e["client"]] * retenu - e["cout"]
        bandit.apprendre(e["contexte"], e["offre"], gain)
