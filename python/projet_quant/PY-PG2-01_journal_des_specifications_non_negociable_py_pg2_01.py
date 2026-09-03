# PY-PG2-01 — journal des spécifications, non négociable	PY-PG2-01
# Projet Quant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import json, hashlib, datetime as dt
from pathlib import Path
JOURNAL = Path("model_risk/journal_specifications.jsonl")
JOURNAL.parent.mkdir(parents=True, exist_ok=True)
def enregistrer(spec, resultats, auteur, motivation, sort):
    """Toute specification testee entre ici. Sans exception."""
    empreinte = hashlib.sha256(
        json.dumps(spec, sort_keys=True).encode()).hexdigest()[:12]
    ligne = {
        "id": empreinte,
        "horodatage": dt.datetime.now(dt.timezone.utc).isoformat(),
        "auteur": auteur,
        "motivation": motivation,
        "specification": spec,
        "resultats": resultats,
        "sort": sort,
    }
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return empreinte
def synthese():
    """Retourne un tableau vide proprement tant qu aucun essai n est journalise."""
    import pandas as pd
    colonnes = ["id", "horodatage", "auteur", "motivation",
                "specification", "resultats", "sort"]
    if not JOURNAL.exists() or JOURNAL.stat().st_size == 0:
        print("Aucune specification journalisee.")
        return pd.DataFrame(columns=colonnes)
    j = pd.read_json(JOURNAL, lines=True)
    print("Specifications testees :", len(j))
    print("Par auteur :\n", j.auteur.value_counts())
    print("Retenues :", (j.sort_values("horodatage").sort == "retenue").sum())
    return j
