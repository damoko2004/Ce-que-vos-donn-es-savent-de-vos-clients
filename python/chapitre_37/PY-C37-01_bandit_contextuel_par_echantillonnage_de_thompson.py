# PY-C37-01 — bandit contextuel par échantillonnage de Thompson
# Chapitre 37 — Cas 19, 20 et 21 — Apprendre en agissant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import copy
import numpy as np
class BanditOffres:
    """Une regression bayesienne lineaire par offre. Contexte = profil client."""
    def __init__(self, n_offres, dim_contexte, bruit=1.0, prior=1.0, seed=42):
        if n_offres <= 0 or dim_contexte <= 0 or bruit <= 0 or prior <= 0:
            raise ValueError("parametres strictement positifs requis")
        self.k = n_offres
        self.sigma2 = bruit ** 2
        self.A = [np.eye(dim_contexte) / prior for _ in range(n_offres)]
        self.b = [np.zeros(dim_contexte) for _ in range(n_offres)]
        self.rng = np.random.default_rng(seed)
    def choisir(self, x):
        x = np.asarray(x, dtype=float)
        scores = []
        for i in range(self.k):
            cov = np.linalg.inv(self.A[i])
            mu = cov @ self.b[i]
            theta = self.rng.multivariate_normal(mu, cov)
            scores.append(float(x @ theta))
        return int(np.argmax(scores))
    def apprendre(self, x, offre, recompense):
        if not 0 <= offre < self.k:
            raise IndexError("offre hors plage")
        x = np.asarray(x, dtype=float)
        self.A[offre] += np.outer(x, x) / self.sigma2
        self.b[offre] += recompense * x / self.sigma2
    def part_par_offre(self, contextes):
        """Diagnostic sans modifier la suite aleatoire utilisee en production."""
        contextes = list(contextes)
        if not contextes:
            return np.zeros(self.k)
        etat = copy.deepcopy(self.rng.bit_generator.state)
        try:
            choix = [self.choisir(x) for x in contextes]
        finally:
            self.rng.bit_generator.state = etat
        return np.bincount(choix, minlength=self.k) / len(choix)
