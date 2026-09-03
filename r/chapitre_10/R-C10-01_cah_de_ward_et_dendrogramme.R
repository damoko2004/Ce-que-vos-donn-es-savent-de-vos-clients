# R-C10-01 — CAH de Ward et dendrogramme
# Chapitre 10 — Classification hiérarchique et segmentation mixte
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(fastcluster)
# Une CAH exacte sur 80 000 clients matérialiserait une matrice de distances
# quadratique. Le dendrogramme est donc construit sur un échantillon fixe.
set.seed(42)
idx <- sample(seq_len(nrow(Z)), min(5000, nrow(Z)))
Z_cah <- Z[idx, , drop = FALSE]
d <- dist(Z_cah, method = "euclidean")
arbre <- hclust(d, method = "ward.D2")
plot(arbre, labels = FALSE, hang = -1,
     main = "Dendrogramme, critere de Ward - echantillon")
rect.hclust(arbre, k = 5, border = "steelblue")
inertie <- sort(arbre$height, decreasing = TRUE)
barplot(inertie[1:min(10, length(inertie))],
        main = "Gain d inertie par regroupement")
classes_echantillon <- cutree(arbre, k = 5)
# Pour affecter toute la base, utiliser la segmentation mixte decrite ci-dessous
# (micro-clusters sur la base complete, puis CAH sur leurs centres).
