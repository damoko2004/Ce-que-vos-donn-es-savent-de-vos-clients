# PY-C40-03 — moindre privilège appliqué aux outils
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from dataclasses import dataclass
from typing import Callable
import re
@dataclass(frozen=True)
class Outil:
    nom: str
    fonction: Callable
    irreversible: bool
    habilitation: str
    valider: Callable          # refuse tout argument hors domaine
def borne_montant(args, profil):
    if args.get("montant", 0) > profil["plafond"]:
        raise Refus("montant au-dessus du plafond autorise")
def destinataire_interne(args, profil):
    if not re.fullmatch(r"[a-z.]+@groupe\.example", args.get("destinataire", "")):
        raise Refus("destinataire externe interdit depuis un agent")
OUTILS = {
    "chercher_procedure": Outil("chercher_procedure", chercher, False,
                                "lecture_doc", lambda a, p: None),
    "consulter_dossier":  Outil("consulter_dossier", consulter, False,
                                "lecture_client", perimetre_client),
    "creer_ticket":       Outil("creer_ticket", creer, False,
                                "ecriture_ticket", champs_obligatoires),
    "envoyer_message":    Outil("envoyer_message", envoyer, True,
                                "communication", destinataire_interne),
}
def appeler(nom, args, profil, trace):
    o = OUTILS.get(nom)
    if o is None:
        trace.incident("outil_inconnu", nom)
        raise Refus("outil non declare")
    if o.habilitation not in profil["habilitations"]:
        trace.incident("habilitation_manquante", nom)
        raise Refus("droits insuffisants")
    o.valider(args, profil)                       # leve Refus si hors domaine
    if o.irreversible and not profil.get("validation_humaine"):
        trace.incident("validation_requise", nom)
        raise ValidationRequise(nom, args)
    trace.appel(nom, args)
    return o.fonction(**args)
