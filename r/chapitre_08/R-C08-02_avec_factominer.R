# R-C08-02 — avec FactoMineR
# Chapitre 8 — Réduire la complexité avec l’analyse en composantes principales
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(FactoMineR)
library(factoextra)
num <- clients[, c("anciennete_mois","nb_achats_12m","ca_12m",
                   "panier_moyen","nb_visites_90j","nb_contacts_service",
                   "recence_jours","remise_moyenne","satisfaction_10",
                   "nb_categories")]
acp <- PCA(num, scale.unit = TRUE, ncp = 5, graph = FALSE)
fviz_eig(acp, addlabels = TRUE)          # eboulis des valeurs propres
fviz_pca_var(acp, col.var = "cos2",      # cercle des correlations
             repel = TRUE)
acp$eig
