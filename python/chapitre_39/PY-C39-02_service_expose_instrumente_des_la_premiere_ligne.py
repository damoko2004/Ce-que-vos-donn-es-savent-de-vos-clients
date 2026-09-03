# PY-C39-02 — service exposé, instrumenté dès la première ligne
# Chapitre 39 — Projet de production — Douze mois chez Kairo
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time, uuid
app = FastAPI(title="kairo-assistant", version="1.4.2")
class Demande(BaseModel):
    texte: str = Field(min_length=10, max_length=4000)
    compte_id: str
    canal: str = "support"
@app.post("/v1/assister")
def assister(d: Demande):
    req_id, t0 = str(uuid.uuid4()), time.monotonic()
    try:
        r = traiter(d.texte)
    except Exception as e:
        metriques.incr("erreurs", tags={"type": type(e).__name__})
        raise HTTPException(503, "service indisponible") from e
    duree = time.monotonic() - t0
    metriques.timing("latence_ms", duree * 1000)
    metriques.gauge("cout_eur", r.get("cout_eur", 0.0))
    metriques.incr("requetes", tags={"mode": r["trace"]["mode"],
                                    "version_prompt": PROMPT_VERSION,
                                    "modele": MODELE})
    journal.ecrire({"req_id": req_id, "compte": d.compte_id,
                    "duree_ms": round(duree * 1000),
                    "cout_eur": r.get("cout_eur"), "trace": r["trace"]})
    return {"req_id": req_id, **r}
@app.get("/health")
def health():
    """Verifie les dependances, pas seulement que le processus tourne."""
    return {"index": index_pret(), "modele": modele_joignable(),
            "version_prompt": PROMPT_VERSION}
