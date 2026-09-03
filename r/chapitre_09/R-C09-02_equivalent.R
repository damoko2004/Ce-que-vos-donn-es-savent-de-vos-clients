# R-C09-02 — équivalent
# Chapitre 9 — K-means : créer rapidement des groupes
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

set.seed(42)
Z <- acp$ind$coord[, 1:3]
for (k in 2:8) {
  km <- kmeans(Z, centers = k, nstart = 20)
  cat(k, "inertie intra", round(km$tot.withinss), "\n")
}
km <- kmeans(Z, centers = 5, nstart = 20)
clients$cluster <- km$cluster
table(clients$cluster)
