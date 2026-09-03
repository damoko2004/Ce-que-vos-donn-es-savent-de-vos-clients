# Installe les paquets R utilises par le livre.
#   Rscript r/installer.R

paquets <- c(
  # Analyse et modelisation
  "dplyr", "tidyr", "purrr", "ggplot2", "broom", "MASS", "readr",
  "FactoMineR", "factoextra", "fastcluster",
  "glmnet", "randomForest", "pROC", "FNN", "caret",
  # Statistique d enquete : projet SurveyOps
  "survey",
  # Texte : chapitre 32
  "quanteda", "quanteda.textstats", "topicmodels",
  # Donnees et formats
  "arrow", "jsonlite", "digest", "DBI", "duckdb",
  # Interfaces : les trois applications Shiny
  "shiny", "DT", "scales", "leaflet"
)

manquants <- setdiff(paquets, rownames(installed.packages()))
if (length(manquants)) {
  cat("Installation de", length(manquants), "paquets...\n")
  install.packages(manquants, repos = "https://cloud.r-project.org")
} else {
  cat("Tous les paquets sont deja presents.\n")
}

# Controle final
absents <- setdiff(paquets, rownames(installed.packages()))
if (length(absents)) {
  cat("\nParquets non installes :", paste(absents, collapse = ", "), "\n")
} else {
  cat("\nEnvironnement R complet.\n")
}
