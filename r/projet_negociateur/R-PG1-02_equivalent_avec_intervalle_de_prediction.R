# R-PG1-02 — équivalent, avec intervalle de prédiction
# Projet Negociateur
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(broom)
acc <- read.csv("accords_fournisseurs.csv")
# Meme logique : on modelise ce qui justifie legitimement la condition,
# le residu est l ecart non explique.
modele <- lm(
  taux_remise ~ log1p(volume_annuel) + categorie + duree_accord +
    taux_service + part_marque_nationale + factor(exercice),
  data = acc)
glance(modele)          # R2, ecart type residuel, degres de liberte
tidy(modele)            # coefficients lisibles pour la restitution
# intervalle de PREDICTION (pas de confiance) : on juge une observation
pred <- predict(modele, newdata = acc, interval = "prediction", level = 0.90)
acc <- acc %>%
  mutate(
    attendu     = pred[, "fit"],
    borne_basse = pred[, "lwr"],
    ecart       = taux_remise - attendu,
    signale     = taux_remise < borne_basse,
    # l ecart est converti en euros, pas en points
    enjeu_euros = pmax(attendu - taux_remise, 0) / 100 * volume_annuel)
top <- acc %>%
  filter(signale) %>%
  arrange(desc(enjeu_euros)) %>%
  select(fournisseur, categorie, taux_remise, attendu, enjeu_euros)
head(top, 20)
dir.create("negociation", recursive = TRUE, showWarnings = FALSE)
write.csv(acc, "negociation/accords_scored.csv", row.names = FALSE)
