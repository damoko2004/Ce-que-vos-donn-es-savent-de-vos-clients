# PY-C32-01 — normalisation et matrice terme-document
# Chapitre 32 — Cas 14 — Ce que vos clients écrivent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import spacy, pandas as pd, re
from sklearn.feature_extraction.text import TfidfVectorizer
nlp = spacy.load("fr_core_news_md", disable=["ner", "parser"])
NEGATIONS = {"pas", "plus", "jamais", "aucun", "sans", "ni"}
LEXIQUE   = {"service client": "service_client",
             "delai de livraison": "delai_livraison",
             "carte fidelite": "carte_fidelite"}
PORTEE_NEGATION = 3   # trois tokens utiles au maximum, jamais toute la phrase
def normaliser(txt):
    t = txt.lower()
    for expr, jeton in LEXIQUE.items():
        t = t.replace(expr, jeton)
    doc = nlp(t)
    sortie, reste_neg = [], 0
    for tok in doc:
        if tok.is_punct:
            reste_neg = 0
            continue
        if tok.is_space:
            continue
        if tok.text in NEGATIONS:
            reste_neg = PORTEE_NEGATION
            continue
        if tok.is_stop:
            continue
        lemme = tok.lemma_
        sortie.append("NEG_" + lemme if reste_neg > 0 else lemme)
        if reste_neg > 0:
            reste_neg -= 1
    return " ".join(sortie)
verb = pd.read_csv("verbatims.csv", parse_dates=["date"])
verb["clean"] = verb.texte.fillna("").map(normaliser)
tfidf = TfidfVectorizer(min_df=8, max_df=0.4, ngram_range=(1, 2))
X = tfidf.fit_transform(verb.clean)
print(X.shape, "->", len(tfidf.vocabulary_), "termes retenus")
