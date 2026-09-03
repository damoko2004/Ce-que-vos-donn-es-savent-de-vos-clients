"""
Génère le jeu de données du fil rouge NovaRetail.

    python data/generer.py

Graine fixée et assertions de contrôle : les chiffres publiés dans le livre
sont reproduits à l'identique. Les autres jeux — panel churn télécom,
freemium, verbatims, catalogue, accords, enquête SurveyOps, corpus et
évaluations — sont versionnés dans ce même dossier ; voir data/LISEZMOI.md.
"""
import numpy as np, pandas as pd
from pathlib import Path

ICI = Path(__file__).resolve().parent


def novaretail(n=80_000):
    r = np.random.default_rng(42)

    # Trois facteurs latents : ce sont eux qui créent les corrélations entre
    # variables, donc la structure que l'ACP du chapitre 8 met au jour.
    engagement = r.normal(0, 1, n)
    prix = r.normal(0, 1, n)
    friction = r.normal(0, 1, n)

    anc = np.clip(r.gamma(3, 12, n) + 8 * engagement, 1, 96).astype(int)
    rec = np.clip(r.exponential(np.exp(5.35 - 0.60 * engagement + 0.25 * friction)),
                  0, 900).astype(int)
    intensite = np.exp(1.35 + 0.95 * engagement - 0.10 * friction)
    freq = r.binomial(r.poisson(intensite), np.clip(1 - rec / 750, 0.12, 1.0))
    panier = np.exp(3.6 + 0.30 * engagement - 0.45 * prix + r.normal(0, .25, n))
    ca = np.round(freq * panier, 2)
    marge_taux = np.clip(0.34 - 0.16 * prix / 3 + r.normal(0, .03, n), .05, .55)
    intensite_serv = 0.35 + 0.75 * np.maximum(friction, 0) + 0.05 * freq
    serv = r.poisson(np.clip(intensite_serv, 0, None))
    moy_sat = 7.6 + 0.35 * engagement - 0.95 * friction
    sat = np.clip(r.normal(moy_sat, 1.1), 1, 10).round(0)
    vis = r.poisson(np.clip(np.exp(0.9 + 0.65 * engagement)
                            * np.clip(1 - rec / 500, .05, 1), 0, 60))
    remise = np.clip(r.beta(2, 8, n) + 0.10 * prix / 3, 0, .6).round(3)
    ncat = np.clip(r.poisson(0.8 + 0.8 * np.maximum(engagement + 1, 0)), 1, 12)

    df = pd.DataFrame({
        "client_id": np.arange(1, n + 1),
        "anciennete_mois": anc, "nb_achats_12m": freq, "ca_12m": ca,
        "panier_moyen": np.where(freq > 0, ca / np.maximum(freq, 1), 0).round(2),
        "marge_12m": (ca * marge_taux).round(2),
        "nb_visites_90j": vis, "nb_contacts_service": serv,
        "recence_jours": rec, "remise_moyenne": remise,
        "satisfaction_10": sat, "nb_categories": ncat,
        "canal_principal": r.choice(["web", "magasin", "mixte"], n, p=[.45, .30, .25]),
        "region": r.choice(list("ABCDE"), n)})

    logit = (-3.55 + 0.0045 * df.recence_jours + 0.42 * df.nb_contacts_service
             - 0.22 * df.satisfaction_10 - 0.09 * df.nb_achats_12m)
    df["churn_90j"] = r.binomial(1, 1 / (1 + np.exp(-logit)))
    return df


def segment(r):
    """Segmentation RFM par seuils métier — chapitre 7."""
    if r.recence_jours > 270:
        return "Endormis"
    if r.recence_jours <= 90 and r.nb_achats_12m >= 4:
        return "Champions"
    if r.anciennete_mois <= 12 and r.nb_achats_12m < 4:
        return "Nouveaux"
    if r.recence_jours > 90 and r.nb_achats_12m >= 4:
        return "A reconquerir"
    return "Reguliers"


if __name__ == "__main__":
    df = novaretail()
    df.to_csv(ICI / "clients_360.csv", index=False)

    # --- Valeurs de référence de l'édition. Toute divergence signale un
    #     changement d'environnement, pas une variante acceptable.
    assert len(df) == 80_000
    assert abs(df.churn_90j.mean() - 0.046) < 0.004
    assert int((df.nb_achats_12m >= 1).sum()) == 63_534

    t = df.assign(seg=df.apply(segment, axis=1)).groupby("seg").size()
    assert t["Endormis"] == 23_654, t["Endormis"]
    assert t["Champions"] == 20_267, t["Champions"]
    assert t["Reguliers"] == 20_001
    assert t["A reconquerir"] == 11_733
    assert t["Nouveaux"] == 4_345

    print("Controles conformes aux chiffres publies :")
    print("   80 000 clients, 4,6 % de churn, 63 534 actifs")
    print("   RFM : 23 654 endormis, 20 267 champions, 20 001 reguliers,")
    print("         11 733 a reconquerir, 4 345 nouveaux")
    print()
    print("clients_360.csv ecrit dans", ICI)
