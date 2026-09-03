# PY-C03-06 — la barrière, et sa trace
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

class QualiteInsuffisante(RuntimeError):
    pass
# Extrait des controles appliques a la source commandes. Les controles de
# satisfaction, de fraicheur CRM et de variation de volume sont executes
# sur leurs sources respectives dans la matrice complete du depot compagnon.
CONTROLES = [
    ("commande_id_nul", lambda d: d.commande_id.isna().mean(), 0.0, "BLOCK"),
    ("doublons_cle", lambda d: d.commande_id.duplicated().mean(), 0.0, "BLOCK"),
    ("ca_negatif", lambda d: ((d.montant < 0) &
                              (d.statut != "remboursement")).mean(), 0.0, "BLOCK"),
    ("non_rattachees_warn", lambda d: d.client_id.isna().mean(), 0.005, "WARN"),
    ("non_rattachees_block", lambda d: d.client_id.isna().mean(), 0.010, "BLOCK"),
]
def barriere_qualite(con, df, run_id):
    resultats, bloquants = [], []
    for nom, mesure, seuil, action in CONTROLES:
        valeur = float(mesure(df))
        ok = valeur <= seuil
        resultats.append({"run_id": run_id, "run_date": pd.Timestamp.now(tz="UTC"),
                          "controle": nom, "valeur": valeur, "seuil": seuil,
                          "action": action, "ok": ok})
        if not ok and action == "BLOCK":
            bloquants.append(f"{nom}={valeur:.4f} > {seuil}")
    con.register("res", pd.DataFrame(resultats))
    con.execute("INSERT INTO data_quality_results SELECT * FROM res")
    if bloquants:
        # La table metier n est pas modifiee : les consommateurs continuent
        # de lire la version saine precedente.
        raise QualiteInsuffisante("; ".join(bloquants))
    return resultats
