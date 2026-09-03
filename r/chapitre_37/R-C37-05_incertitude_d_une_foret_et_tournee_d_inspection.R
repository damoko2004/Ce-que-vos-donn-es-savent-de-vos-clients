# R-C37-05 — incertitude d’une forêt, et tournée d’inspection
# Chapitre 37 — Cas 19, 20 et 21 — Apprendre en agissant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(randomForest); library(dplyr)
rf <- randomForest(risque ~ ., data = hist_inspections,
                   ntree = 400, nodesize = 5)
# predict.all rend la prediction de CHAQUE arbre : leur dispersion
# fournit une heuristique de desaccord, pas une incertitude calibree.
incertitude <- function(modele, X) {
  p <- predict(modele, X, predict.all = TRUE)$individual
  apply(p, 1, sd)
}
reseau <- reseau %>%
  mutate(
    risque_pred = predict(rf, .),
    consequence = abonnes_desservis * criticite,
    enjeu       = risque_pred * consequence,
    incert       = incertitude(rf, .))
CAPACITE <- min(200L, nrow(reseau))
n_exploit <- floor(0.70 * CAPACITE)
n_explore <- floor(0.20 * CAPACITE)
n_hasard  <- CAPACITE - n_exploit - n_explore
exploit <- reseau %>% slice_max(enjeu, n = n_exploit, with_ties = FALSE)
restant <- reseau %>% anti_join(exploit, by = "troncon_id")
explore <- restant %>% slice_max(incert, n = min(n_explore, nrow(restant)),
                                 with_ties = FALSE)
pool <- restant %>% anti_join(explore, by = "troncon_id")
set.seed(42)
hasard <- pool %>% slice_sample(n = min(n_hasard, nrow(pool)))
tournee <- bind_rows(
  mutate(exploit, motif = "exploitation"),
  mutate(explore, motif = "exploration_ciblee"),
  mutate(hasard,  motif = "controle_aleatoire"))
stopifnot(nrow(tournee) <= CAPACITE,
          !anyDuplicated(tournee$troncon_id))
count(tournee, motif)
