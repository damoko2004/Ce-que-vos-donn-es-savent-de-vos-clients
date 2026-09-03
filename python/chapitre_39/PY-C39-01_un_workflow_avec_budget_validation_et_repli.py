# PY-C39-01 — un workflow avec budget, validation et repli
# Chapitre 39 — Projet de production — Douze mois chez Kairo
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from dataclasses import dataclass, field
import time, logging
log = logging.getLogger("kairo.agent")
@dataclass
class Budget:
    max_secondes: float = 8.0
    max_appels: int = 4
    max_cout_eur: float = 0.05
    debut: float = field(default_factory=time.monotonic)
    appels: int = 0
    cout: float = 0.0
    def peut_appeler(self):
        return (time.monotonic() - self.debut < self.max_secondes
                and self.appels < self.max_appels
                and self.cout < self.max_cout_eur)
    def consommer(self, cout_eur):
        self.appels += 1
        self.cout += cout_eur
        return (time.monotonic() - self.debut <= self.max_secondes
                and self.appels <= self.max_appels
                and self.cout <= self.max_cout_eur)
def sortie(reponse, extraits, escalade, statut, trace, budget):
    return {"reponse": reponse, "extraits": extraits, "escalade": escalade,
            "statut": statut, "trace": trace, "cout_eur": budget.cout,
            "latence_ms": round((time.monotonic() - budget.debut) * 1000)}
def traiter(demande, budget=None):
    budget = budget or Budget()
    trace = {"etapes": [], "mode": "nominal"}
    passages = recherche(demande, k=6)
    trace["etapes"].append({"etape": "recherche", "trouves": len(passages)})
    if passages is None or len(passages) == 0:
        return replier(demande, trace, budget, "aucune_source", passages=[])
    for tentative in range(2):
        if not budget.peut_appeler():
            return replier(demande, trace, budget, "budget_epuise", passages)
        brouillon, cout = generer(demande, passages)
        if not budget.consommer(cout):
            return replier(demande, trace, budget, "budget_depasse", passages)
        probleme = valider(brouillon, passages)
        trace["etapes"].append({"etape": "generation",
                               "tentative": tentative, "probleme": probleme})
        if probleme is None:
            return sortie(brouillon, passages, False, "nominal", trace, budget)
        log.warning("sortie invalide: %s", probleme)
    return replier(demande, trace, budget, "validation_echouee", passages)
def replier(demande, trace, budget, motif, passages=None):
    trace["mode"], trace["motif"] = "repli", motif
    extraits = passages if passages is not None else []
    return sortie(None, extraits, True, "repli", trace, budget)
