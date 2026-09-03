# R-C14-02 — équivalent
# Chapitre 14 — Régression logistique et modèles linéaires
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(pROC)
clients <- read.csv("clients_360.csv")
set.seed(42)
i <- sample(seq_len(nrow(clients)), floor(0.75 * nrow(clients)))
train <- clients[i, , drop = FALSE]
test  <- clients[-i, , drop = FALSE]
modele <- glm(churn_90j ~ recence_jours + nb_achats_12m + log1p(ca_12m) +
                nb_contacts_service + satisfaction_10 + remise_moyenne +
                canal_principal,
              data = train, family = binomial)
summary(modele)
exp(coef(modele))
proba <- predict(modele, newdata = test, type = "response")
auc(test$churn_90j, proba)
