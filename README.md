# Ce que vos données savent de vos clients

**Dépôt compagnon de l'ouvrage** — *De la question métier à l'impact prouvé*
Machine learning, IA générative et décision · R & Python

> 📖 **Page du projet : https://damoko2004.github.io/Ce-que-vos-donn-es-savent-de-vos-clients/**

---

## Ce que contient ce dépôt

| | |
|---|---|
| **Le sommaire** | 11 parties, 40 chapitres — consultable sur la page du projet |
| **Le code** | 96 blocs : 62 en Python, 24 en R et R Shiny, 10 ressources |
| **Les données** | 10 jeux, tous générés par un script, avec leurs contrôles |

**Ce dépôt ne contient pas le texte du livre**, et ne le contiendra pas. On y trouve de quoi
travailler, s'entraîner et vérifier — pas l'ouvrage.

---

## Démarrer

```bash
git clone https://github.com/damoko2004/Ce-que-vos-donn-es-savent-de-vos-clients.git
cd Ce-que-vos-donn-es-savent-de-vos-clients
pip install -r requirements.txt
python data/generer.py
```

Le générateur affiche ses contrôles. Vous devez lire exactement ceci :

```
Controles conformes aux chiffres publies :
   80 000 clients, 4,6 % de churn, 63 534 actifs
   RFM : 23 654 endormis, 20 267 champions
```

Pour la partie R :

```bash
Rscript r/installer.R
Rscript r/chapitre_07/R-C07-02_equivalent_memes_seuils.R
```

---

## Arborescence

```
.
├── index.html              page du projet (GitHub Pages)
├── data/
│   ├── generer.py          produit TOUS les jeux de données
│   ├── clients_360.csv     le fil rouge NovaRetail
│   ├── brut/               les cinq sources du projet ETL
│   ├── surveyops/          enquête + vérité de terrain
│   ├── catalogue.csv
│   └── accords_fournisseurs.csv
├── python/
│   ├── chapitre_02/ … chapitre_40/
│   ├── exercices/
│   ├── projet_negociateur/  projet_quant/  projet_surveyops/
│   └── annexes/
├── r/
│   ├── installer.R
│   └── (même organisation par chapitre)
├── ressources/             schémas, configurations, arborescences
├── tests/                  vérifie que les chiffres publiés sont reproduits
└── requirements.txt
```

---

## Identifiants de code

Chaque bloc du livre porte un identifiant, repris tel quel dans le nom de fichier.

| Identifiant | Signification |
|---|---|
| `PY-C08-01` | Python, chapitre 8, premier bloc |
| `R-C07-02` | R, chapitre 7, deuxième bloc |
| `R-PG3-07` | R, projet SurveyOps, septième bloc |
| `SH-AXA-02` | Ressource, annexe A, deuxième bloc |

Les blocs d'un même chapitre se lisent **dans l'ordre de leur rang** : certains réutilisent
les objets créés par le précédent, comme dans un carnet de notes.

---

## Reproductibilité

C'est l'exigence que le livre s'applique à lui-même : aucun tableau du fil rouge n'est saisi
à la main.

| Vérification | Imprimé | Exécuté |
|---|---|---|
| Clients générés | 80 000 | 80 000 |
| Taux de churn à 90 jours | 4,6 % | 4,6 % |
| Clients actifs | 63 534 | 63 534 |
| RFM — Endormis | 23 654 · 5,4 % | 23 654 · 5,4 % |
| RFM — Champions | 20 267 · 66,1 % | 20 267 · 66,1 % |
| ACP, axes 1 à 3 | 35,1 · 12,2 · 10,4 % | 35,1 · 12,2 · 10,4 % |
| Typologie, 5 segments | 2 637 · 14 114 · 17 408 · 16 353 · 13 022 | identiques |

Vérifiez vous-même :

```bash
pytest tests/ -q
```

**R et Python donnent le même résultat**, et ce n'est pas une affirmation : le bloc
`R-C07-02` rend les mêmes effectifs que son équivalent Python, et FactoMineR donne
35,087 / 12,204 / 10,387 % là où scikit-learn donne 35,1 / 12,2 / 10,4.

---

## Les données

Tous les jeux sont **synthétiques**. Aucune donnée réelle d'entreprise ou de personne n'est
diffusée ici. Ils sont construits pour porter les structures qu'ils doivent enseigner —
corrélations latentes, biais de sélection, anomalies connues — et non pour imiter une base
particulière.

Deux d'entre eux méritent une mention :

- `surveyops/verite_terrain.csv` contient les **anomalies injectées**. C'est ce qui permet de
  calculer une précision et un rappel réels sur le dispositif de contrôle qualité.
- `brut/satisfaction.csv` ne couvre que **11 % des clients**. Ce biais de réponse est
  volontaire : le livre s'en sert pour montrer ce qu'on n'a pas le droit d'en conclure.

---

## Environnement de référence

| | Version |
|---|---|
| Python | 3.12 |
| R | 4.3.3 |

Les résultats numériques ont été obtenus avec ces versions et les dépendances figées dans
`requirements.txt`. Les bibliothèques évoluent : certains chiffres peuvent bouger à la marge,
les ordres de grandeur et les conclusions non.

---

## Licence

Le **code** de ce dépôt est publié sous licence MIT : réutilisez-le, adaptez-le, y compris
en entreprise.

Le **texte de l'ouvrage** n'est pas diffusé ici et reste protégé.

© 2026 Dickers AMOKO

---

## Le socle

Certains blocs du livre s'appuient sur des objets que le texte décrit sans les
reproduire : une matrice d'interactions, un corpus déjà indexé, un service de
langue. Le fichier `socle.py` en fournit une implémentation minimale, pour que
**chaque bloc s'exécute** sur votre poste.

```python
from socle import *      # depuis la racine du dépôt
```

Ces implémentations sont volontairement simples : elles servent à faire tourner
le code, pas à remplacer un vrai système. Le livre explique ce que chacune
devrait être en production.

---

## État des tests

| | Python | R |
|---|---|---|
| Blocs | 63 | 26 |
| Syntaxe valide | **63 / 63** | **26 / 26** |
| **Erreurs de code** | **0** | **0** |

Les blocs ont été rejoués un à un, dans l'ordre du livre, en conservant
l'espace de travail — c'est ainsi qu'un lecteur les exécute.

**Six blocs n'ont pas pu être exécutés dans l'environnement de test**, et il
faut le dire plutôt que de l'arrondir :

- deux téléchargent un modèle pré-entraîné (torch hub, Hugging Face) ;
- quatre dépendent de `duckdb`, `quanteda`, `leaflet` ou `srvyr`, indisponibles
  sur la machine de test.

Sur un poste connecté disposant de ces paquets, ils fonctionnent. Leur syntaxe
est validée et leurs dépendances sont déclarées aux annexes A et B.

---

## Vérifier vous-même

```bash
pip install -r requirements.txt
python data/generer.py        # doit afficher 23 654 endormis, 20 267 champions
pytest tests/ -q              # 5 tests
Rscript r/installer.R
```
