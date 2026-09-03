# R-AXB-01 — Installation
# Annexes
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

# Analyse et modelisation
install.packages(c("dplyr", "tidyr", "purrr", "ggplot2",
                   "FactoMineR", "factoextra", "fastcluster",
                   "glmnet", "randomForest", "pROC", "FNN", "caret"))
# Texte, donnees et formats
install.packages(c("quanteda", "quanteda.textstats", "topicmodels",
                   "arrow", "jsonlite", "digest"))
# Interfaces et restitution : les projets des parties IX et X
install.packages(c("shiny", "DT", "scales", "broom", "MASS", "readr",
               "DBI", "duckdb", "survey", "srvyr", "leaflet", "tibble",
               "writexl", "quarto"))
