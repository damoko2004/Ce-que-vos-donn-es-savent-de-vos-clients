# PY-C39-03 — banc d’évaluation exécuté à chaque changement
# Chapitre 39 — Projet de production — Douze mois chez Kairo
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import json, statistics as st
import numpy as np
from pathlib import Path
CAS = json.loads(Path("eval/jeu_reference.json").read_text())
SEUILS = {"conformite": 0.98, "fidelite": 0.97,
          "abstention_min": 0.05, "abstention_max": 0.20,
          "latence_p90_ms": 2000, "cout_moyen_eur": 0.03}
def regrouper(lignes, cle):
    groupes = {}
    for x in lignes:
        groupes.setdefault(x[cle], []).append(x)
    return groupes
def evaluer(version):
    if not CAS:
        raise ValueError("jeu de reference vide")
    res = []
    for cas in CAS:
        r = traiter(cas["question"])
        abstenu = r["reponse"] is None
        doit_abstenir = bool(cas.get("doit_abstenir", False))
        conforme = (abstenu if doit_abstenir else
                    (not abstenu and valider(r["reponse"], r.get("extraits")) is None))
        fidele = True if abstenu else toutes_affirmations_sourcees(r["reponse"])
        res.append({"id": cas["id"], "famille": cas["famille"],
                    "question": cas["question"], "reponse": r["reponse"],
                    "trace": r["trace"], "conforme": conforme,
                    "fidele": fidele, "abstenu": abstenu,
                    "latence_ms": r["latence_ms"], "cout": r["cout_eur"]})
    out = Path(f"eval/resultats_{version}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for x in res:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    latences = sorted(x["latence_ms"] for x in res)
    p90 = latences[min(len(latences) - 1, int(np.ceil(0.90 * len(latences))) - 1)]
    m = {"conformite": sum(x["conforme"] for x in res) / len(res),
         "fidelite": sum(x["fidele"] for x in res) / len(res),
         "abstention": sum(x["abstenu"] for x in res) / len(res),
         "latence_p90_ms": p90,
         "cout_moyen_eur": st.mean(x["cout"] for x in res)}
    echecs = []
    if m["conformite"] < SEUILS["conformite"]: echecs.append("conformite")
    if m["fidelite"] < SEUILS["fidelite"]: echecs.append("fidelite")
    if not SEUILS["abstention_min"] <= m["abstention"] <= SEUILS["abstention_max"]:
        echecs.append("abstention hors plage")
    if m["latence_p90_ms"] > SEUILS["latence_p90_ms"]: echecs.append("latence")
    if m["cout_moyen_eur"] > SEUILS["cout_moyen_eur"]: echecs.append("cout")
    return {"version": version, "metriques": m, "echecs": echecs,
            "par_famille": regrouper(res, "famille")}
