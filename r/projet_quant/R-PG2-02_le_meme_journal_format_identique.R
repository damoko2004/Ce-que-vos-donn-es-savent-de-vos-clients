# R-PG2-02 — le même journal, format identique
# Projet Quant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(jsonlite); library(digest); library(dplyr)
JOURNAL <- "model_risk/journal_specifications.jsonl"
dir.create(dirname(JOURNAL), recursive = TRUE, showWarnings = FALSE)
enregistrer <- function(spec, resultats, auteur, motivation, sort) {
  empreinte <- substr(digest(spec, algo = "sha256"), 1, 12)
  ligne <- list(
    id            = empreinte,
    horodatage    = format(Sys.time(), "%Y-%m-%dT%H:%M:%S", tz = "UTC"),
    auteur        = auteur,        # "humain" ou "agent"
    motivation    = motivation,
    specification = spec,
    resultats     = resultats,
    sort          = sort)          # retenue, ecartee, a revoir
  cat(toJSON(ligne, auto_unbox = TRUE), "\n",
      file = JOURNAL, append = TRUE, sep = "")
  invisible(empreinte)
}
synthese <- function() {
  if (!file.exists(JOURNAL) || file.info(JOURNAL)$size == 0) {
    message("Aucune specification journalisee.")
    return(invisible(tibble()))
  }
  j <- stream_in(file(JOURNAL), verbose = FALSE)
  cat("Specifications testees :", nrow(j), "\n")
  print(count(j, auteur))
  print(count(j, sort))
  invisible(j)
}
