# PY-C40-04 — extraction par gabarit, avec abstention par champ
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
class ChampExtrait(BaseModel):
    valeur: Optional[str]
    source_piece: Optional[str]
    source_page: Optional[int]
    confiance: float = Field(ge=0, le=1)
    statut: Literal["extrait", "absent", "illisible", "ambigu"]
class LiasseFiscale(BaseModel):
    exercice: ChampExtrait
    chiffre_affaires: ChampExtrait
    resultat_net: ChampExtrait
    capitaux_propres: ChampExtrait
    dettes_financieres: ChampExtrait
class ExtractionDocument(BaseModel):
    """La provenance vit dans une enveloppe, jamais dans le modele metier."""
    document_id: str
    type_document: str
    donnees: LiasseFiscale
SEUIL_ABSTENTION = 0.75
def extraire(piece, gabarit) -> ExtractionDocument:
    """Un gabarit par type de piece : jamais d extraction generique."""
    brut = modele.extraire_structure(piece.texte, schema=gabarit.model_json_schema())
    brut = brut if isinstance(brut, dict) else {}
    sortie = {}
    for champ in gabarit.model_fields:
        contenu = brut.get(champ) or {}
        valeur = contenu.get("valeur")
        texte_valeur = "" if valeur is None else str(valeur)
        present = bool(texte_valeur.strip()) and texte_valeur in piece.texte
        conf_brute = float(contenu.get("confiance", 0) or 0)
        conf = min(max(conf_brute, 0.0), 1.0) * (1.0 if present else 0.0)
        publie = conf >= SEUIL_ABSTENTION
        statut = ("extrait" if publie else
                  ("absent" if not texte_valeur.strip() else "ambigu"))
        sortie[champ] = ChampExtrait(
            valeur=texte_valeur if publie else None,
            source_piece=piece.identifiant,
            source_page=contenu.get("page"),
            confiance=conf,
            statut=statut)
    return ExtractionDocument(document_id=piece.identifiant,
                              type_document=piece.type_document,
                              donnees=gabarit(**sortie))
def reconcilier(extractions: list[ExtractionDocument]):
    """Le meme chiffre doit concorder entre les pieces qui le portent."""
    incoherences = []
    for champ in CHAMPS_CROISES:
        valeurs = {e.document_id: getattr(e.donnees, champ).valeur
                   for e in extractions if hasattr(e.donnees, champ)}
        distinctes = {v for v in valeurs.values() if v is not None}
        if len(distinctes) > 1:
            incoherences.append({"champ": champ, "valeurs": valeurs})
    return incoherences
