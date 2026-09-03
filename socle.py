"""
socle — les objets que le livre présente sans les définir.

Certains blocs du livre s'appuient sur des éléments décrits dans le texte mais
non reproduits dans le code imprimé : une matrice d'interactions, un corpus
déjà indexé, un service de langue. Ce module en fournit une implémentation
minimale, pour que **chaque bloc du livre s'exécute** sur le poste du lecteur.

    from socle import *

Ces implémentations sont volontairement simples. Elles servent à faire tourner
le code, pas à remplacer un vrai système : le livre explique ce que chacune
devrait être en production.
"""
import json, os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(os.environ.get("DATA_DIR", "."))


# =====================================================================
# Données dérivées, attendues par certains chapitres
# =====================================================================
def _clients():
    return pd.read_csv(DATA / "clients_360.csv")


def charger_flux(n_mois: int = 18) -> pd.DataFrame:
    """Flux créditeurs mensuels par client — chapitre 18, attrition bancaire."""
    r = np.random.default_rng(31)
    cl = _clients().head(6_000)
    mois = pd.date_range("2025-03-01", periods=n_mois, freq="MS").strftime("%Y-%m")
    lignes = []
    for cid, eng in zip(cl.client_id, (cl.ca_12m - cl.ca_12m.mean()) / cl.ca_12m.std()):
        base = float(np.exp(7.2 + 0.35 * np.clip(eng, -3, 3)))
        tendance = r.choice([1.0, 0.97, 0.90])          # stable, tassement, décrochage
        for k, m in enumerate(mois):
            lignes.append({"client_id": int(cid), "mois": m,
                           "credit": round(base * tendance ** k * r.uniform(.85, 1.15), 2)})
    return pd.DataFrame(lignes)


def charger_interactions(n_users: int = 4_000, n_items: int = 1_200) -> pd.DataFrame:
    """Interactions utilisateur-objet — chapitre 22, filtrage collaboratif."""
    r = np.random.default_rng(37)
    gouts = r.integers(0, 6, n_users)
    familles = r.integers(0, 6, n_items)
    lignes = []
    for u in range(n_users):
        k = int(np.clip(r.poisson(9), 1, 60))
        prefs = np.where(familles == gouts[u])[0]
        pool = prefs if len(prefs) else np.arange(n_items)
        for it in r.choice(pool, size=min(k, len(pool)), replace=False):
            lignes.append({"user_idx": u, "item_idx": int(it),
                           "poids": float(round(r.uniform(0.5, 1.0), 3))})
    return pd.DataFrame(lignes)


def historique_inspections(n: int = 2_500) -> tuple:
    """Historique d'inspections de réseau — chapitre 37, exploration ciblée."""
    r = np.random.default_rng(41)
    X = pd.DataFrame({
        "age_canalisation": r.integers(1, 80, n),
        "pression_moy": np.round(r.normal(4.2, 0.8, n), 2),
        "diametre_mm": r.choice([60, 100, 150, 200, 300], n),
        "materiau_fonte": r.integers(0, 2, n),
        "nb_fuites_passees": r.poisson(0.6, n)})
    y = (0.004 * X.age_canalisation + 0.05 * X.materiau_fonte
         + 0.08 * X.nb_fuites_passees + r.normal(0, 0.03, n)).clip(0, 1)
    return X, pd.Series(np.round(y, 4), name="risque")


def reseau_a_inspecter(n: int = 5_000) -> pd.DataFrame:
    r = np.random.default_rng(43)
    d = pd.DataFrame({
        "troncon_id": [f"T{i:06d}" for i in range(1, n + 1)],
        "age_canalisation": r.integers(1, 80, n),
        "pression_moy": np.round(r.normal(4.2, 0.8, n), 2),
        "diametre_mm": r.choice([60, 100, 150, 200, 300], n),
        "materiau_fonte": r.integers(0, 2, n),
        "nb_fuites_passees": r.poisson(0.6, n),
        "abonnes_desservis": r.integers(5, 900, n),
        "criticite": np.round(r.uniform(0.5, 3.0, n), 2)})
    return d


# =====================================================================
# Corpus documentaire — chapitres 36 et 40
# =====================================================================
def decouper(texte, taille=120, chevauchement=20):
    mots, blocs, i = texte.split(), [], 0
    while i < len(mots):
        blocs.append(" ".join(mots[i:i + taille]))
        i += max(1, taille - chevauchement)
    return blocs


def charger_passages() -> pd.DataFrame:
    """Corpus découpé en passages, prêt pour la recherche."""
    chemin = DATA / "intranet.parquet"
    docs = (pd.read_parquet(chemin) if chemin.exists()
            else pd.read_csv(DATA / "intranet.csv"))
    lignes = []
    for _, d in docs.head(300).iterrows():
        for j, b in enumerate(decouper(str(d.contenu))):
            lignes.append({"doc_id": d.doc_id, "titre": d.titre,
                           "maj": d.derniere_maj, "bloc": j, "texte": b})
    return pd.DataFrame(lignes)


class RechercheLexicale:
    """Recherche par mots, sans modèle : suffit à exécuter les blocs."""

    def __init__(self, passages: pd.DataFrame):
        from rank_bm25 import BM25Okapi
        self.psg = passages.reset_index(drop=True)
        self.bm25 = BM25Okapi([t.lower().split() for t in self.psg.texte])

    def __call__(self, question: str, k: int = 6) -> pd.DataFrame:
        scores = self.bm25.get_scores(question.lower().split())
        return self.psg.iloc[np.argsort(scores)[::-1][:k]]


# =====================================================================
# Services de langue — remplacés par des doublures déterministes
# =====================================================================
BAREME = {"citation_obligatoire": True, "abstention_si_insuffisant": True}


def juge_llm(sortie: str, criteres=None) -> str:
    """Doublure du juge automatique du chapitre 40.

    Le vrai juge est un modèle de langue. Celui-ci applique la règle que le
    livre lui demande de vérifier : toute affirmation doit porter une citation.
    """
    return "conforme" if "[" in str(sortie) else "non conforme"


def generer(demande, passages, **_):
    """Doublure du service de génération : rédige à partir des extraits."""
    extraits = list(getattr(passages, "texte", passages))[:2]
    corps = " ".join(str(e)[:120] for e in extraits)
    return f"{corps} [1]", 0.004          # texte, coût en euros


def valider(reponse, sources=None, profil=None):
    """Contrôle de sortie : rend None si la réponse est conforme."""
    if not reponse:
        return "reponse_vide"
    if "[" not in reponse:
        return "citation_absente"
    return None


def recherche(demande, k=6):
    return _RECHERCHE(demande, k=k)


def chercher(demande, k=6):
    return _RECHERCHE(demande, k=k)


def file_validation(etat):
    """Mise en file pour validation humaine — chapitre 40."""
    etat = dict(etat)
    etat["validation_humaine"] = True
    return etat


def livrer(etat):
    etat = dict(etat)
    etat["livre"] = True
    return etat


def replier(*args, **kwargs):
    """Repli générique : rend une sortie exploitable, jamais une erreur."""
    return {"reponse": None, "escalade": True, "statut": "repli",
            "extraits": [], "trace": {"mode": "repli"}, "cout_eur": 0.0,
            "latence_ms": 0}


class _Journal:
    def __init__(self): self.lignes = []
    def ecrire(self, **kw): self.lignes.append(kw)
    def avertir(self, *a, **k): self.lignes.append({"niveau": "avertissement", "a": a})
    def erreur(self, *a, **k): self.lignes.append({"niveau": "erreur", "a": a})
    def incident(self, *a, **k): self.lignes.append({"niveau": "incident", "a": a})
    def suppression(self, *a, **k): self.lignes.append({"niveau": "suppression", "a": a})
    def appel(self, *a, **k): self.lignes.append({"niveau": "appel", "a": a})


class _Metriques:
    def __init__(self): self.valeurs = []
    def incr(self, nom, tags=None): self.valeurs.append((nom, 1, tags))
    def timing(self, nom, v): self.valeurs.append((nom, v, None))
    def gauge(self, nom, v): self.valeurs.append((nom, v, None))


journal = _Journal()
metriques = _Metriques()
CATEGORIES_SENSIBLES = {"reclamation", "litige"}
MAX_REPRISES = 1

# objets construits à l'import, utilisés directement par certains blocs
psg = charger_passages()
_RECHERCHE = RechercheLexicale(psg)
rechercher = _RECHERCHE
flux = charger_flux()
inter = charger_interactions()
X_hist, y_hist = historique_inspections()
reseau = reseau_a_inspecter()
ATTRIBUTS = ["couleur", "matiere", "motif", "saison", "col", "finition", "style", "usage"]



# =====================================================================
# Objets complémentaires attendus par quelques blocs
# =====================================================================
def indexer_client(source=None):
    """Dernière activité connue par client — chapitre 18."""
    r = np.random.default_rng(47)
    ids = sorted(flux.client_id.unique())
    return pd.DataFrame(
        {"jours_depuis_derniere": r.integers(1, 400, len(ids)),
         "jours_depuis_derniere_volontaire": r.integers(1, 400, len(ids))},
        index=pd.Index(ids, name="client_id"))



ops = indexer_client()


class _TraceOutil:
    def __init__(self): self.evenements = []
    def incident(self, *a): self.evenements.append(("incident",) + a)
    def appel(self, *a): self.evenements.append(("appel",) + a)


trace = _TraceOutil()


def consulter(**kwargs):
    """Doublure de la consultation d'un dossier client."""
    return {"dossier": kwargs, "statut": "consulte"}


def creer(**kwargs):
    return {"ticket": kwargs, "statut": "cree"}


def envoyer(**kwargs):
    return {"message": kwargs, "statut": "simule"}


def perimetre_client(args, profil):
    if args.get("client_id") is None:
        raise ValueError("client_id requis")


def champs_obligatoires(args, profil):
    if not args.get("objet"):
        raise ValueError("objet requis")


class _JournalPersistant:
    """Point de reprise minimal pour le graphe d'orchestration."""
    def __init__(self): self.etats = {}
    def get(self, cle, defaut=None): return self.etats.get(cle, defaut)
    def put(self, cle, valeur): self.etats[cle] = valeur


journal_persistant = None        # None = pas de reprise, accepté par le graphe

# Attributs et représentation d'images, chapitre 34 : on simule des
# probabilités déjà calculées, pour que les blocs suivants s'exécutent.
def _simuler_predictions(n=1_200, seed=53):
    r = np.random.default_rng(seed)
    classes, positions, proba, verite = {}, {}, {}, {}
    grilles = {"couleur": ["noir", "bleu", "rouge", "vert"],
               "matiere": ["coton", "laine", "lin", "synthetique"],
               "motif": ["uni", "raye", "imprime"],
               "saison": ["ete", "hiver", "mi-saison"],
               "col": ["rond", "v", "montant"],
               "finition": ["standard", "premium"],
               "style": ["classique", "sportif", "chic"],
               "usage": ["ville", "sport", "soiree"]}
    for att, mods in grilles.items():
        cls = np.array(mods)
        vrai = r.choice(cls, n)
        # attributs visuels : bien prédits ; style et usage : mal prédits
        force = 30.0 if att in ("couleur", "matiere", "motif", "saison", "col") else 1.0
        p = np.zeros((n, len(cls)))
        for i, v in enumerate(vrai):
            p[i] = r.dirichlet(np.ones(len(cls)))
            p[i, list(cls).index(v)] += force
            p[i] /= p[i].sum()
        classes[att] = cls
        # positions : les lignes annotees pour cet attribut
        positions[att] = np.arange(n)
        proba[att], verite[att] = p, vrai
    return classes, positions, proba, verite


classes_attributs, positions, proba, annotees_verite = _simuler_predictions()
classes = classes_attributs
annotees = pd.DataFrame({a: annotees_verite[a] for a in ATTRIBUTS})
annotees.index = pd.RangeIndex(len(annotees))       # index positionnel
annotees["reference"] = [f"REF{i:05d}" for i in range(1, len(annotees) + 1)]
annotees["fournisseur"] = [f"F{i%140:03d}" for i in range(len(annotees))]

emb_ref = pd.DataFrame(
    np.random.default_rng(59).normal(0, 1, (len(annotees), 64)),
    index=annotees.reference)

X_reseau = reseau.drop(columns=["troncon_id", "abonnes_desservis", "criticite"])

_cat = DATA / "catalogue.csv"
catalogue = (pd.read_csv(_cat) if _cat.exists()
             else pd.DataFrame({"reference": annotees.reference,
                                "fournisseur": annotees.fournisseur}))
if len(catalogue) > len(emb_ref):
    catalogue = catalogue.head(len(emb_ref)).copy()
catalogue["reference"] = list(emb_ref.index[:len(catalogue)])


class _Encodeur:
    """Doublure d'un modele de phrases : vecteurs deterministes, hors ligne."""

    def __init__(self, dim=64):
        self.dim = dim

    def encode(self, textes, normalize_embeddings=False, **_):
        import hashlib
        if isinstance(textes, str):
            textes = [textes]
        V = np.vstack([
            np.frombuffer(hashlib.sha256(str(t).encode()).digest(), dtype=np.uint8)
              [:32].astype(np.float32) for t in textes])
        V = np.hstack([V, V]) [:, :self.dim]
        if normalize_embeddings:
            V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-9)
        return V.astype("float32")


modele = _Encodeur()

# Listes de variables posees une fois dans le livre et reutilisees ensuite
num = ["anciennete_mois", "nb_achats_12m", "ca_12m", "panier_moyen",
       "nb_visites_90j", "nb_contacts_service", "recence_jours",
       "remise_moyenne", "satisfaction_10", "nb_categories"]
cat = ["canal_principal", "region"]

df = _clients()                 # la table analytique du fil rouge



# ---------------------------------------------------------------------
# Prétraitement standard du fil rouge, posé une fois au chapitre 14
# et réutilisé par les chapitres suivants.
# ---------------------------------------------------------------------
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

prep = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])

X, y = df[num + cat], df["churn_90j"]
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42)


def _connexion_activite():
    """Source d'activité client — remplace une connexion au système bancaire."""
    return indexer_client()


conn = _connexion_activite()

__all__ = [n for n in dir() if not n.startswith("_")]
