# Mise en ligne — trois étapes

## 1. Pousser le dépôt

Depuis le dossier `depot_github` :

```bash
git init
git add .
git commit -m "Depot compagnon : sommaire, code R et Python, jeux de donnees"
git branch -M main
git remote add origin https://github.com/damoko2004/Ce-que-vos-donn-es-savent-de-vos-clients.git
git push -u origin main
```

Le `.gitignore` exclut déjà `*.docx` et `*.pdf` : le texte du livre ne peut pas partir
par inadvertance.

## 2. Activer GitHub Pages

Dans le dépôt : **Settings → Pages**

- Source : `Deploy from a branch`
- Branch : `main`, dossier `/ (root)`
- Enregistrer

La page sera en ligne sous deux minutes à l'adresse :
**https://damoko2004.github.io/Ce-que-vos-donn-es-savent-de-vos-clients/**

## 3. Renseigner la description du dépôt

Dans l'encadré **About**, en haut à droite :

- Description : `Code R et Python, jeux de donnees et sommaire du livre « Ce que vos donnees savent de vos clients »`
- Website : l'adresse GitHub Pages ci-dessus
- Topics : `data-science` `machine-learning` `r` `python` `customer-analytics` `livre`

---

## Ce qui se lance tout seul

Le fichier `.github/workflows/tests.yml` déclenche à chaque envoi :

- la compilation des 62 blocs Python,
- la génération des données et le contrôle des chiffres publiés,
- les tests `pytest`,
- l'analyse syntaxique des 24 blocs R.

Le badge de statut s'ajoute ensuite en tête de README :

```markdown
![Tests](https://github.com/damoko2004/Ce-que-vos-donn-es-savent-de-vos-clients/actions/workflows/tests.yml/badge.svg)
```

## Si le dépôt est renommé

L'adresse actuelle contient les tirets d'un titre accentué. Un nom plus court —
`ce-que-vos-donnees-savent` par exemple — donnerait une adresse plus lisible.
Dans ce cas, remplacer l'ancienne adresse dans `index.html` et dans `README.md`
(elle y figure une dizaine de fois).
