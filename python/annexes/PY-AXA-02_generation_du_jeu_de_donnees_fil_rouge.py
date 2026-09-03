# PY-AXA-02 — Génération du jeu de données fil rouge
# Annexes
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import numpy as np, pandas as pd
rng = np.random.default_rng(42)
n = 80_000
# Trois facteurs latents. Ce sont eux qui donnent sa structure a l ACP :
# ils produisent des correlations realistes entre variables observees.
engagement = rng.normal(0, 1, n)      # intensite de la relation
prix       = rng.normal(0, 1, n)      # sensibilite au prix
friction   = rng.normal(0, 1, n)      # irritation, contacts service
anc = np.clip(rng.gamma(3, 12, n) + 8 * engagement, 1, 96).astype(int)
# Un client engage revient vite : la recence en depend.
rec = np.clip(rng.exponential(np.exp(5.35 - 0.60 * engagement + 0.25 * friction)),
              0, 900).astype(int)
# Un client parti tot dans l annee a mecaniquement moins achete.
intensite = np.exp(1.35 + 0.95 * engagement - 0.10 * friction)
freq = rng.binomial(rng.poisson(intensite), np.clip(1 - rec / 750, 0.12, 1.0))
panier = np.exp(3.6 + 0.30 * engagement - 0.45 * prix + rng.normal(0, .25, n))
ca = np.round(freq * panier, 2)
marge_taux = np.clip(0.34 - 0.16 * prix / 3 + rng.normal(0, .03, n), .05, .55)
intensite_serv = 0.35 + 0.75 * np.maximum(friction, 0) + 0.05 * freq
serv = rng.poisson(np.clip(intensite_serv, 0, None))
moy_sat = 7.6 + 0.35 * engagement - 0.95 * friction
sat  = np.clip(rng.normal(moy_sat, 1.1), 1, 10).round(0)
vis  = rng.poisson(np.clip(np.exp(0.9 + 0.65 * engagement)
                           * np.clip(1 - rec / 500, .05, 1), 0, 60))
remise = np.clip(rng.beta(2, 8, n) + 0.10 * prix / 3, 0, .6).round(3)
ncat = np.clip(rng.poisson(0.8 + 0.8 * np.maximum(engagement + 1, 0)), 1, 12)
df = pd.DataFrame({
    "client_id": np.arange(1, n + 1),
    "anciennete_mois": anc, "nb_achats_12m": freq, "ca_12m": ca,
    "panier_moyen": np.where(freq > 0, ca / np.maximum(freq, 1), 0).round(2),
    "marge_12m": (ca * marge_taux).round(2),
    "nb_visites_90j": vis, "nb_contacts_service": serv,
    "recence_jours": rec, "remise_moyenne": remise,
    "satisfaction_10": sat, "nb_categories": ncat,
    "canal_principal": rng.choice(["web", "magasin", "mixte"], n, p=[.45, .30, .25]),
    "region": rng.choice(list("ABCDE"), n),
})
logit = (-3.55 + 0.0045 * df.recence_jours + 0.42 * df.nb_contacts_service
         - 0.22 * df.satisfaction_10 - 0.09 * df.nb_achats_12m)
df["churn_90j"] = rng.binomial(1, 1 / (1 + np.exp(-logit)))
# Valeurs de reference de l edition. Toute divergence signale un
# changement d environnement, et non une variante acceptable.
assert len(df) == 80_000
assert abs(df.churn_90j.mean() - 0.04605) < 1e-12
assert int((df.nb_achats_12m >= 1).sum()) == 63_534
df.to_csv("clients_360.csv", index=False)
print(round(df.churn_90j.mean(), 3), "de taux de churn,",
      int((df.nb_achats_12m >= 1).sum()), "clients actifs")
