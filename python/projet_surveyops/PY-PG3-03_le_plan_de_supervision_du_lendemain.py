# PY-PG3-03 — le plan de supervision du lendemain
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
CAPACITE = {"contre_appel": 40, "visite": 5, "briefing": 3}
def plan_supervision(questionnaires, enqueteurs, capacite=CAPACITE):
    requis_q = {"questionnaire", "risque", "motifs"}
    requis_e = {"enqueteur", "risque_enqueteur", "motif_principal"}
    manque_q = not requis_q.issubset(questionnaires.columns)
    manque_e = not requis_e.issubset(enqueteurs.columns)
    if manque_q or manque_e:
        raise ValueError("colonnes de supervision manquantes")
    plan = []
    n_cible = int(0.80 * capacite["contre_appel"])
    n_alea = capacite["contre_appel"] - n_cible
    cibles = questionnaires.nlargest(min(n_cible, len(questionnaires)), "risque")
    pool = questionnaires[~questionnaires.questionnaire.isin(cibles.questionnaire)
                          & (questionnaires.risque < 30)]
    alea = pool.sample(min(n_alea, len(pool)), random_state=42)
    for q in cibles.itertuples(index=False):
        plan.append({"action": "contre_appel", "cible": q.questionnaire,
                     "motif": q.motifs, "origine": "cible"})
    for q in alea.itertuples(index=False):
        plan.append({"action": "contre_appel", "cible": q.questionnaire,
                     "motif": "controle aleatoire", "origine": "aleatoire"})
    visites = enqueteurs.nlargest(min(capacite["visite"], len(enqueteurs)),
                                  "risque_enqueteur")
    for e in visites.itertuples(index=False):
        plan.append({"action": "visite", "cible": e.enqueteur,
                     "motif": e.motif_principal, "origine": "cible"})
    reste = enqueteurs[~enqueteurs.enqueteur.isin(visites.enqueteur)]
    briefs = reste.nlargest(min(capacite["briefing"], len(reste)), "risque_enqueteur")
    for e in briefs.itertuples(index=False):
        plan.append({"action": "briefing", "cible": e.enqueteur,
                     "motif": e.motif_principal, "origine": "cible"})
    return pd.DataFrame(plan)
