# PY-C03-07 — orchestration du flux complet
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import datetime as dt
import hashlib, re, warnings
from pathlib import Path
import pandas as pd
def charger_optionnel(con, nom, chemin):
    """Charge un fichier optionnel en RAW append-only, par batch idempotent."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nom):
        raise ValueError("nom de source invalide")
    p = Path(chemin)
    if not p.exists():
        raise FileNotFoundError(p)
    if p.suffix == ".csv":
        d = pd.read_csv(p)
    elif p.suffix == ".json":
        d = pd.read_json(p)
    elif p.suffix == ".parquet":
        d = pd.read_parquet(p)
    else:
        raise ValueError(f"format non supporte: {p.suffix}")
    initialiser_stockage(con)
    batch_id = hashlib.sha256(p.read_bytes()).hexdigest()
    deja = con.execute(
        "SELECT 1 FROM etl_ingested_batches WHERE source=? AND batch_id=?",
        [nom, batch_id]).fetchone()
    if deja:
        return 0
    d = d.copy()
    d["_batch_id"] = batch_id
    d["_ingested_at"] = pd.Timestamp.now(tz="UTC")
    d["_source_file"] = str(p)
    con.register("source_optionnelle", d)
    table = f"raw_{nom}"
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS "
                "SELECT * FROM source_optionnelle WHERE FALSE")
    con.execute(f"INSERT INTO {table} SELECT * FROM source_optionnelle")
    con.execute("INSERT INTO etl_ingested_batches VALUES (?,?,?)",
                [nom, batch_id, pd.Timestamp.now(tz="UTC")])
    return len(d)
def pipeline(date_ref, con):
    maintenant = dt.datetime.now(dt.timezone.utc)
    graine = f"{date_ref}|{maintenant.isoformat()}"
    run_id = hashlib.sha256(graine.encode()).hexdigest()[:12]
    statut, degrades = "SUCCESS", []
    initialiser_stockage(con)
    clients = extraire("raw/crm_clients.csv", CONTRATS["clients"])
    commandes = extraire("raw/commandes.csv", CONTRATS["commandes"])
    charger_commandes(con, commandes, run_id=run_id)
    # La dimension client est reconstruite a partir de la derniere version
    # de l extrait courant ; le RAW, lui, n est jamais remplace.
    charger_optionnel(con, "clients", "raw/crm_clients.csv")
    con.register("clients_courants", clients)
    con.execute("""CREATE OR REPLACE TABLE dim_client AS
        SELECT * EXCLUDE (rn) FROM (
          SELECT client_id, region, date_inscription, source_updated_at,
                 row_number() OVER (
                   PARTITION BY client_id ORDER BY source_updated_at DESC) rn
          FROM clients_courants)
        WHERE rn = 1""")
    for nom, chemin in [("satisfaction", "raw/satisfaction.csv"),
                        ("web", "raw/weblog.parquet"),
                        ("tickets", "raw/tickets.json")]:
        try:
            charger_optionnel(con, nom, chemin)
        except (FileNotFoundError, ValueError, OSError) as e:
            degrades.append(nom)
            warnings.warn(f"{nom} indisponible: {e}", RuntimeWarning)
    # La macro customer_360(date_ref) est definie une fois par le bloc
    # SH-C03-04. La barriere qualite doit passer AVANT toute table metier.
    barriere_qualite(con, commandes, run_id)
    con.execute("BEGIN")
    try:
        con.execute("CREATE OR REPLACE TABLE customer_360_daily AS "
                    "SELECT * FROM customer_360(?)", [date_ref])
        if degrades:
            statut = "DEGRADE"
            con.execute("ALTER TABLE customer_360_daily ADD COLUMN data_status VARCHAR")
            con.execute("UPDATE customer_360_daily SET data_status = ?",
                        [",".join(degrades)])
        con.execute("INSERT INTO etl_runs VALUES (?,?,?,?,?)",
                    [run_id, "customer_360", maintenant,
                     dt.datetime.now(dt.timezone.utc), statut])
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return run_id, statut
