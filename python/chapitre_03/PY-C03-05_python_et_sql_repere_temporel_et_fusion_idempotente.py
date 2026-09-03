# PY-C03-05 — Python et SQL - repère temporel et fusion idempotente
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

FENETRE_SECURITE = pd.Timedelta(hours=6)
def initialiser_stockage(con):
    con.execute("""CREATE TABLE IF NOT EXISTS etl_watermarks(
        source VARCHAR PRIMARY KEY, watermark TIMESTAMPTZ)""")
    con.execute("""CREATE TABLE IF NOT EXISTS etl_runs(
        run_id VARCHAR, source VARCHAR, debut TIMESTAMPTZ,
        fin TIMESTAMPTZ, statut VARCHAR)""")
    con.execute("""CREATE TABLE IF NOT EXISTS etl_ingested_batches(
        source VARCHAR, batch_id VARCHAR, ingested_at TIMESTAMPTZ,
        PRIMARY KEY(source, batch_id))""")
    con.execute("""CREATE TABLE IF NOT EXISTS data_quality_results(
        run_id VARCHAR, run_date TIMESTAMPTZ, controle VARCHAR,
        valeur DOUBLE, seuil DOUBLE, action VARCHAR, ok BOOLEAN)""")
    con.execute("""CREATE TABLE IF NOT EXISTS raw_commandes(
        commande_id VARCHAR, client_id VARCHAR, montant DOUBLE, marge DOUBLE,
        date_commande TIMESTAMPTZ, source_updated_at TIMESTAMPTZ,
        canal VARCHAR, statut VARCHAR, _ingested_at TIMESTAMPTZ,
        _source_file VARCHAR,
        PRIMARY KEY (commande_id, source_updated_at))""")
def dernier_watermark(con, source):
    initialiser_stockage(con)
    r = con.execute("SELECT watermark FROM etl_watermarks WHERE source = ?",
                    [source]).fetchone()
    # pd.to_datetime(..., utc=True) fonctionne que la valeur lue soit naive
    # ou deja timezone-aware ; pd.Timestamp(x, tz=...) ne le garantit pas.
    return (pd.to_datetime(r[0], utc=True) - FENETRE_SECURITE if r
            else pd.Timestamp("2000-01-01", tz="UTC"))
def charger_commandes(con, df, source="commandes", run_id="commandes"):
    depuis = dernier_watermark(con, source)
    modif = pd.to_datetime(df.source_updated_at, utc=True, errors="raise")
    incr = df.loc[modif > depuis].copy()
    if incr.empty:
        return 0
    con.register("incr", incr)
    # RAW reste append-only. La cle (commande, version source) rend la relance
    # idempotente sans ecraser une version historique.
    con.execute("""
        INSERT INTO raw_commandes
        SELECT i.* FROM incr i
        ANTI JOIN raw_commandes r
          ON r.commande_id = i.commande_id
         AND r.source_updated_at = i.source_updated_at
    """)
    nouveau = pd.to_datetime(incr.source_updated_at.max(), utc=True)
    con.execute("INSERT OR REPLACE INTO etl_watermarks VALUES (?, ?)",
                [source, nouveau])
    return len(incr)
