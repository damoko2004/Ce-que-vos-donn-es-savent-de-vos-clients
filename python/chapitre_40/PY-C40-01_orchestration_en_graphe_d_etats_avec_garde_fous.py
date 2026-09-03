# PY-C40-01 — orchestration en graphe d’états, avec garde-fous
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
class Etat(TypedDict):
    demande: str
    profil: dict
    categorie: Optional[str]
    sources: list
    brouillon: Optional[str]
    incidents: list
    incidents_courants: list
    nb_reprises: int
    budget_restant: float
    validation_humaine: bool
def router(e: Etat) -> Etat:
    e["categorie"] = classifieur.predire(e["demande"])
    return e
def rechercher(e: Etat) -> Etat:
    e["sources"] = index.chercher(e["demande"],
                                 perimetre=e["profil"]["habilitations"], k=6)
    if not e["sources"]:
        e["incidents"].append("aucune_source")
    return e
def apres_recherche(e: Etat) -> Literal["rediger", "replier"]:
    return "rediger" if e["sources"] else "replier"
def rediger(e: Etat) -> Etat:
    sortie, cout = generer(e["demande"], e["sources"])
    e["budget_restant"] -= cout
    if e["budget_restant"] < 0:
        e["incidents"].append("budget_depasse")
    e["brouillon"] = sortie
    return e
def controler(e: Etat) -> Etat:
    e["incidents_courants"] = []
    for regle in (citations_presentes, chiffres_issus_des_sources,
                  pas_d_engagement_commercial, pas_de_donnee_client_hors_perimetre):
        probleme = regle(e["brouillon"], e["sources"], e["profil"])
        if probleme:
            e["incidents_courants"].append(probleme)
    e["incidents"].extend(e["incidents_courants"])
    return e
MAX_REPRISES = 1
def suite(e: Etat) -> Literal["reprendre", "humain", "livrer", "replier"]:
    if "budget_depasse" in e["incidents"]:
        return "replier"
    if e["incidents_courants"]:
        peut_reprendre = (e["nb_reprises"] < MAX_REPRISES
                          and e["budget_restant"] > 0)
        return "reprendre" if peut_reprendre else "replier"
    if e["categorie"] in CATEGORIES_SENSIBLES:
        return "humain"
    return "livrer"
def reprendre(e: Etat) -> Etat:
    e["nb_reprises"] += 1
    return e
g = StateGraph(Etat)
for nom, fn in [("router", router), ("rechercher", rechercher),
                ("rediger", rediger), ("controler", controler),
                ("reprendre", reprendre), ("humain", file_validation),
                ("livrer", livrer), ("replier", replier)]:
    g.add_node(nom, fn)
g.set_entry_point("router")
g.add_edge("router", "rechercher")
g.add_conditional_edges("rechercher", apres_recherche)
g.add_edge("rediger", "controler")
g.add_conditional_edges("controler", suite)
g.add_edge("reprendre", "rediger")
for terminal in ("livrer", "replier", "humain"):
    g.add_edge(terminal, END)
agent = g.compile(checkpointer=journal_persistant)
