"""Verifie que les donnees generees reproduisent les chiffres du livre."""
import subprocess, sys
from pathlib import Path
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]


def charger():
    f = RACINE / "data" / "clients_360.csv"
    if not f.exists():
        subprocess.run([sys.executable, str(RACINE / "data" / "generer.py")], check=True)
    return pd.read_csv(f)


def test_volumetrie():
    df = charger()
    assert len(df) == 80_000
    assert df.client_id.is_unique


def test_taux_de_churn():
    assert abs(charger().churn_90j.mean() - 0.046) < 0.004


def test_clients_actifs():
    assert int((charger().nb_achats_12m >= 1).sum()) == 63_534


def test_segmentation_rfm():
    """Les effectifs imprimes au chapitre 7."""
    df = charger()

    def segment(r):
        if r.recence_jours > 270: return "Endormis"
        if r.recence_jours <= 90 and r.nb_achats_12m >= 4: return "Champions"
        if r.anciennete_mois <= 12 and r.nb_achats_12m < 4: return "Nouveaux"
        if r.recence_jours > 90 and r.nb_achats_12m >= 4: return "A reconquerir"
        return "Reguliers"

    t = df.assign(seg=df.apply(segment, axis=1)).groupby("seg").size()
    assert t["Endormis"] == 23_654
    assert t["Champions"] == 20_267
    assert t["Reguliers"] == 20_001
    assert t["A reconquerir"] == 11_733
    assert t["Nouveaux"] == 4_345


def test_acp():
    """Les variances imprimees au chapitre 8."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    df = charger()
    num = ["anciennete_mois", "nb_achats_12m", "ca_12m", "panier_moyen",
           "nb_visites_90j", "nb_contacts_service", "recence_jours",
           "remise_moyenne", "satisfaction_10", "nb_categories"]
    X = StandardScaler().fit_transform(df[num].fillna(df[num].median()))
    v = PCA().fit(X).explained_variance_ratio_
    assert abs(v[0] - 0.351) < 0.002
    assert abs(v[1] - 0.122) < 0.002
    assert abs(v[2] - 0.104) < 0.002
