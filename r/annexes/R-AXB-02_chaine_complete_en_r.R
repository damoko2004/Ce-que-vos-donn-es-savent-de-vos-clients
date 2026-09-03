# R-AXB-02 — Chaîne complète en R
# Annexes
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(FactoMineR); library(pROC)
clients <- read.csv("clients_360.csv")
# 1. segmentation RFM
clients <- clients %>% mutate(
  R = ntile(-recence_jours, 5), F = ntile(nb_achats_12m, 5),
  M = ntile(ca_12m, 5), score_rfm = R + F + M)
# 2. ACP puis typologie
num <- clients %>% select(anciennete_mois, nb_achats_12m, ca_12m,
                          panier_moyen, recence_jours, satisfaction_10,
                          nb_contacts_service, nb_categories)
acp <- PCA(num, scale.unit = TRUE, ncp = 3, graph = FALSE)
km  <- kmeans(acp$ind$coord, centers = 5, nstart = 20)
clients$segment <- km$cluster
# 3. modele de churn. Ce jeu synthetique est une photographie sans date_ref ;
# le split aleatoire est uniquement un smoke test. Les cas reels utilisent
# la validation temporelle du chapitre 16.
set.seed(42)
i <- sample(nrow(clients), 0.75 * nrow(clients))
m <- glm(churn_90j ~ recence_jours + nb_achats_12m + log1p(ca_12m) +
           nb_contacts_service + satisfaction_10,
         data = clients[i, ], family = binomial)
p <- predict(m, clients[-i, ], type = "response")
auc(clients$churn_90j[-i], p)
