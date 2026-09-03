# R-PG3-08 — plan de tabulation, intervalles et exports	R-PG3-08
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(srvyr); library(readr); library(tibble)
# Le plan est declaratif : on peut ajouter des dizaines de lignes sans
# recopier le calcul statistique. design_cal vient du bloc R-PG3-06.
enq$poids_final <- as.numeric(weights(design_cal))
design_tab <- as_survey_design(enq, ids = grappe, strata = strate,
                               weights = poids_final, nest = TRUE)
plan_tab <- tribble(
  ~id, ~titre, ~variable, ~modalite, ~ventilation, 
  "T01", "Compte bancaire par sexe",  "compte_bancaire", "oui",     "sexe",
  "T02", "Compte bancaire par region", "compte_bancaire", "oui",     "region")
tabuler <- function(ligne) {
  var <- rlang::sym(ligne$variable)
  vent <- rlang::sym(ligne$ventilation)
  design_tab %>%
    group_by(!!vent) %>%
    summarise(estimation = survey_mean((!!var) == ligne$modalite,
              vartype = c("ci", "cv"), na.rm = TRUE)) %>%
    mutate(table_id = ligne$id, titre = ligne$titre, .before = 1)
}
resultats <- bind_rows(lapply(seq_len(nrow(plan_tab)),
                              function(i) tabuler(plan_tab[i, ])))
dir.create("surveyops/publication", recursive = TRUE, showWarnings = FALSE)
write_csv(plan_tab, "surveyops/publication/plan_tabulation.csv")
write_csv(resultats, "surveyops/publication/tabulations_a_valider.csv")
writexl::write_xlsx(list(plan = plan_tab, resultats = resultats),
                     "surveyops/publication/tabulations_a_valider.xlsx")
# Une validation humaine/statistique promeut ensuite le fichier accepte en
# tabulations_validees.csv. Le dashboard ne relit jamais les microdonnees.
