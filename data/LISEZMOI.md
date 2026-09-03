# Les jeux de données

## Régénérer le fil rouge

```bash
python data/generer.py
```

Ce script produit `clients_360.csv` et **vérifie par des assertions** que les
chiffres publiés dans le livre sont reproduits : 80 000 clients, 4,6 % de churn,
63 534 actifs, et la segmentation RFM à 23 654 endormis et 20 267 champions.

Si une assertion échoue, c'est que votre environnement diffère de celui de
l'édition — pas que le livre se trompe.

## Les autres jeux, versionnés ici

| Fichier | Contenu | Utilisé par |
|---|---|---|
| `clients_360.csv` | 80 000 clients, 15 variables | Fil rouge, parties I à VII |
| `panel_churn.csv` | Panel télécom daté, 12 cohortes | Chapitre 16 |
| `comptes.csv`, `usage_j0_j30.csv.gz`, `conversions.csv` | Freemium | Chapitre 17 |
| `assurance_appetence.parquet` | Appétence produits | Chapitre 19 |
| `verbatims.csv` | 8 000 verbatims clients | Chapitre 32 |
| `commandes.csv.gz`, `weblog.csv.gz` | Commandes et navigation | Chapitres 2, 3, 33 |
| `raw/` | Les cinq sources brutes du projet ETL | Chapitre 3 |
| `catalogue.csv`, `images/` | Catalogue et annotations produit | Chapitres 21 et 34 |
| `accords_fournisseurs.csv` | 3 000 accords | Projet du négociateur |
| `surveyops/`, `survey_clean.csv.gz`, `marges_calage.csv` | Enquête et vérité de terrain | Projet SurveyOps |
| `intranet.parquet`, `evaluation/`, `eval/` | Corpus et jeux d'évaluation | Chapitres 36, 39, 40 |
| `model_risk/`, `gouvernance/` | Suivi de modèle et portefeuille | Chapitres 27, 40 |

Les fichiers volumineux sont livrés compressés. `pandas` les lit directement :

```python
pd.read_csv("data/commandes.csv.gz")
```

## Données synthétiques

Tous ces jeux sont **générés**. Aucune donnée réelle d'entreprise ou de personne
n'est diffusée ici. Ils sont construits pour porter les structures qu'ils doivent
enseigner — corrélations latentes, biais de sélection, anomalies connues — et non
pour imiter une base particulière.

Deux méritent une mention :

- `surveyops/verite_terrain.csv` contient les **anomalies injectées** : c'est ce
  qui permet de calculer une précision et un rappel réels sur le dispositif de
  contrôle qualité.
- `raw/satisfaction.csv` ne couvre que **11 % des clients**. Ce biais de réponse
  est volontaire : le livre s'en sert pour montrer ce qu'on n'a pas le droit
  d'en conclure.
