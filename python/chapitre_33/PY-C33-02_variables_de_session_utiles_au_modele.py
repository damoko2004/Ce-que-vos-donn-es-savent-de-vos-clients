# PY-C33-02 — variables de session utiles au modèle
# Chapitre 33 — Cas 15 — Ce que vos clients parcourent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import pandas as pd
DATE_REF = pd.Timestamp("2025-10-01", tz="UTC")
sessions = log.groupby(["visiteur_id", "session_id"]).agg(
    debut=("horodatage", "min"),
    fin=("horodatage", "max"),
    nb_pages=("url", "size"),
    nb_pages_uniques=("url", "nunique"),
    categories=("categorie", lambda s: s.dropna().nunique()),
    fiches_produit=("type_page", lambda s: (s == "produit").sum()),
    ajouts_panier=("type_page", lambda s: (s == "ajout_panier").sum()),
    page_entree=("url", "first"),
    page_sortie=("url", "last"),
    origine=("referrer", "first"),
)
sessions["duree_s"] = (sessions.fin - sessions.debut).dt.total_seconds()
sessions["profondeur"] = sessions.nb_pages_uniques / sessions.nb_pages
# agregation par client sur 30 jours glissants, avant la date de reference
fen = sessions[(sessions.debut < DATE_REF) &
               (sessions.debut >= DATE_REF - pd.Timedelta(days=30))]
nav = fen.groupby("visiteur_id").agg(
    nb_sessions_30j=("nb_pages", "size"),
    pages_par_session=("nb_pages", "mean"),
    duree_moy_s=("duree_s", "mean"),
    fiches_vues_30j=("fiches_produit", "sum"),
    paniers_30j=("ajouts_panier", "sum"),
    max_categories_session=("categories", "max"),
    soir_ou_weekend=("debut", lambda s: ((s.dt.hour >= 20) |
                                          (s.dt.dayofweek >= 5)).mean()))
