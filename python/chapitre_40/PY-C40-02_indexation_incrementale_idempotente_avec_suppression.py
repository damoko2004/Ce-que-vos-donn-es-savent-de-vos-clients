# PY-C40-02 — indexation incrémentale, idempotente, avec suppressions
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
MANIFESTE = Path("index/manifeste.json")
MANIFESTE.parent.mkdir(parents=True, exist_ok=True)
def empreinte(contenu, metadonnees):
    """Le contenu ET les droits : un changement d habilitation compte."""
    h = hashlib.sha256()
    h.update(contenu.encode())
    h.update(json.dumps({k: metadonnees[k]
                         for k in ("habilitations", "date_effet", "version")},
                        sort_keys=True).encode())
    return h.hexdigest()
def synchroniser(source):
    ancien = json.loads(MANIFESTE.read_text()) if MANIFESTE.exists() else {}
    nouveau, stats = {}, {"ajouts": 0, "maj": 0, "inchanges": 0,
                          "suppressions": 0, "echecs": 0}
    vus = set()
    for doc in source.lister():
        vus.add(doc.id)
        try:
            contenu = source.extraire(doc)
            emp = empreinte(contenu, doc.metadonnees)
        except Exception as e:
            stats["echecs"] += 1
            journal.incident("extraction", doc.id, str(e))
            # On conserve l entree existante, mais on n en cree pas pour un
            # document nouveau : memoriser None casserait le cycle suivant.
            if doc.id in ancien:
                nouveau[doc.id] = ancien[doc.id]
            continue
        if ancien.get(doc.id, {}).get("empreinte") == emp:
            nouveau[doc.id] = ancien[doc.id]
            stats["inchanges"] += 1
            continue
        index.remplacer(doc.id, decouper(contenu), doc.metadonnees)
        nouveau[doc.id] = {"empreinte": emp,
                           "indexe_le": datetime.now(timezone.utc).isoformat()}
        stats["maj" if doc.id in ancien else "ajouts"] += 1
    # Propagation des suppressions : le point le plus souvent oublie.
    a_supprimer = set(ancien) - vus
    # Garde-fou AVANT l action irreversible : une chute brutale signale
    # un incident de source, pas une suppression legitime. On ne compte
    # pas sur une transaction atomique que l index ne garantit pas.
    if len(a_supprimer) > 0.10 * len(ancien):
        raise Alerte("taux de suppression au-dessus du seuil, cycle interrompu")
    for disparu in a_supprimer:
        index.supprimer(disparu)
        stats["suppressions"] += 1
        journal.suppression(disparu)
    tmp = MANIFESTE.with_suffix(".tmp")
    tmp.write_text(json.dumps(nouveau, sort_keys=True), encoding="utf-8")
    tmp.replace(MANIFESTE)
    return stats
