# R-PG3-05 — la proportion brute n est pas une estimation
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(survey); library(dplyr)
enq <- read.csv("survey_clean.csv")
# Ce que produit un simple comptage : une description de l echantillon.
naif <- mean(enq$compte_bancaire == "oui", na.rm = TRUE)
cat("Proportion brute :", round(100 * naif, 1), "%\n")
# Ce que produit le plan de sondage : une estimation de la population.
design <- svydesign(
  ids     = ~grappe,      # tirage en grappes
  strata  = ~strate,      # stratification
  weights = ~poids_final, # probabilites inegales et non-reponse
  nest    = TRUE,
  data    = enq)
est <- svymean(~I(compte_bancaire == "oui"), design, deff = TRUE, na.rm = TRUE)
print(est)
print(confint(est))
# Proportion brute      : 42.8 %
# Estimation ponderee   : 39.7 %   IC95 [37.8 ; 41.6]
# Effet de plan (deff)  : 2.14
# -> l echantillon en grappes equivaut a 8 400 tirages aleatoires simples,
#    et non a 18 000. La precision reelle est deux fois moindre.
