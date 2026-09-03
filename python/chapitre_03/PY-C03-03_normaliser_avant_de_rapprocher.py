# PY-C03-03 — normaliser avant de rapprocher
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import re, unicodedata
def norm_email(x):
    if not isinstance(x, str):
        return None
    x = unicodedata.normalize("NFKC", x).strip().lower()
    if x.count("@") != 1:
        return None
    local, domaine = x.rsplit("@", 1)
    if not local or not domaine:
        return None
    # Regle conservative : ne jamais supprimer points ou alias "+" de facon
    # universelle. Ces conventions dependent du fournisseur de messagerie.
    return f"{local}@{domaine}"
def norm_tel(x):
    if not isinstance(x, str):
        return None
    d = re.sub(r"\D", "", x)
    if d.startswith("0033"):
        d = "0" + d[4:]
    elif d.startswith("33"):
        d = "0" + d[2:]
    return d if len(d) == 10 else None
def resoudre(crm, autres, cle, normaliseur, confiance, methode):
    ref = (crm.assign(_k=crm[cle].map(normaliseur))
              .dropna(subset=["_k"])
              .drop_duplicates("_k", keep=False))
    src = autres.assign(_k=autres[cle].map(normaliseur))
    j = src.merge(ref[["_k", "client_id"]], on="_k", how="left")
    j["methode"] = j.client_id.notna().map({True: methode, False: None})
    j["confiance"] = j.client_id.notna().astype(float) * confiance
    return j.drop(columns="_k")
