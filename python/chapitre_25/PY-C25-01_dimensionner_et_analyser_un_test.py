# PY-C25-01 — dimensionner et analyser un test
# Chapitre 25 — Cas 10 — La campagne qui semblait marcher
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest
import numpy as np
# 1. Taille necessaire pour detecter 3 points d ecart sur une base a 80 pour cent
p0, effet = 0.80, 0.03
h = 2 * (np.arcsin(np.sqrt(p0 + effet)) - np.arcsin(np.sqrt(p0)))
n = NormalIndPower().solve_power(effect_size=h, power=0.8, alpha=0.05)
print("Taille par groupe :", int(np.ceil(n)))
# 2. Analyse apres coup
succes    = np.array([8_240, 2_000])   # traites, temoins
effectifs = np.array([10_000, 2_500])   # 82,4 % contre 80,0 %
z, pval = proportions_ztest(succes, effectifs)
taux = succes / effectifs
print("Traites", round(taux[0], 3), "Temoins", round(taux[1], 3),
      "ecart", round(taux[0] - taux[1], 3), "p", round(pval, 4))
# Traites 0.824  Temoins 0.8  ecart 0.024  p 0.0053
