# R-PG3-06 — pondération en trois temps	R-PG3-06
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(survey); library(readr)
# 1. Poids de tirage : inverse de la probabilite d inclusion
enq <- enq %>% mutate(poids_tirage = 1 / prob_inclusion)
# 2. Correction de non-reponse, par groupe homogene de reponse
enq <- enq %>%
  group_by(strate, milieu) %>%
  mutate(taux_reponse = mean(repondant, na.rm = TRUE),
         poids_nr = poids_tirage / taux_reponse) %>%
  ungroup()
if (any(!is.finite(enq$poids_nr))) stop("groupe sans repondant : correction impossible")
design_nr <- svydesign(ids = ~grappe, strata = ~strate,
                       weights = ~poids_nr, nest = TRUE, data = enq)
# 3. Calage : les marges viennent d un fichier versionne, jamais d un vecteur
# recopie a la main dont l ordre pourrait diverger de model.matrix.
f <- ~sexe + classe_age + milieu
noms <- colnames(model.matrix(f, model.frame(f, enq)))
m <- read_csv("marges_calage.csv", show_col_types = FALSE)
stopifnot(all(c("coefficient", "total") %in% names(m)))
marges <- setNames(m$total, m$coefficient)
if (!all(noms %in% names(marges)))
  stop("marges_calage.csv ne couvre pas tous les coefficients du modele")
marges <- marges[noms]
design_cal <- calibrate(design_nr, formula = f,
                        population = marges, calfun = "raking")
w <- as.numeric(weights(design_cal))
cat("Rapport poids max / poids min :", round(max(w) / min(w), 1), "\n")
