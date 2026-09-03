# PY-C33-03 — séquences prédictives
# Chapitre 33 — Cas 15 — Ce que vos clients parcourent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from collections import Counter
cle_session = ["visiteur_id", "session_id"]
seq = (log.sort_values("horodatage")
          .groupby(cle_session).type_page
          .apply(lambda s: tuple(s)))
# La cible est definie sur le meme MultiIndex que les sequences.
cible = (log.groupby(cle_session).type_page
           .apply(lambda s: int((s == "achat").any()))
           .reindex(seq.index).fillna(0).astype(int))
def trigrammes(t):
    return [t[i:i + 3] for i in range(len(t) - 2)]
avec = Counter(g for s in seq[cible.eq(1)] for g in trigrammes(s))
sans = Counter(g for s in seq[cible.eq(0)] for g in trigrammes(s))
tot_avec, tot_sans = max(sum(avec.values()), 1), max(sum(sans.values()), 1)
# Lissage + plafond : un trigramme absent du groupe temoin ne doit pas
# produire un lift de plusieurs millions uniquement a cause d un zero.
ALPHA, LIFT_MAX = 1.0, 50.0
vocab = set(avec) | set(sans)
den_avec = tot_avec + ALPHA * len(vocab)
den_sans = tot_sans + ALPHA * len(vocab)
lift = {}
for g in avec:
    if avec[g] <= 200:
        continue
    p1 = (avec[g] + ALPHA) / den_avec
    p0 = (sans[g] + ALPHA) / den_sans
    lift[g] = min(p1 / p0, LIFT_MAX)
for g, l in sorted(lift.items(), key=lambda x: -x[1])[:10]:
    suffixe = " (plafonne)" if l >= LIFT_MAX else ""
    print(round(l, 2), " -> ".join(g), suffixe)
