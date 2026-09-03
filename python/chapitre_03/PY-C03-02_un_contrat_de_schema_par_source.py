# PY-C03-02 — un contrat de schéma par source
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from dataclasses import dataclass
import datetime as dt
import warnings
import pandas as pd
@dataclass(frozen=True)
class Contrat:
    nom: str
    colonnes_requises: set
    cle_metier: str
    date_evenement: str
    date_modification: str
CONTRATS = {
    "commandes": Contrat("commandes",
                         {"commande_id", "client_id", "montant", "marge",
                          "date_commande", "source_updated_at", "canal", "statut"},
                         "commande_id", "date_commande", "source_updated_at"),
    "clients": Contrat("clients",
                       {"client_id", "email", "telephone", "date_inscription",
                        "source_updated_at", "region"},
                       "client_id", "date_inscription", "source_updated_at"),
}
class EchecSchema(Exception):
    pass
def extraire(chemin, contrat):
    df = pd.read_csv(chemin)
    manquantes = contrat.colonnes_requises - set(df.columns)
    if manquantes:
        raise EchecSchema(
            f"ECHEC_SCHEMA source={contrat.nom} colonnes absentes={sorted(manquantes)}")
    inconnues = set(df.columns) - contrat.colonnes_requises
    if inconnues:
        warnings.warn(f"colonnes nouvelles ignorees: {sorted(inconnues)}",
                      RuntimeWarning, stacklevel=2)
    df[contrat.date_evenement] = pd.to_datetime(
        df[contrat.date_evenement], utc=True, errors="raise")
    df[contrat.date_modification] = pd.to_datetime(
        df[contrat.date_modification], utc=True, errors="raise")
    df["_ingested_at"] = pd.Timestamp.now(tz="UTC")
    df["_source_file"] = str(chemin)
    return df
