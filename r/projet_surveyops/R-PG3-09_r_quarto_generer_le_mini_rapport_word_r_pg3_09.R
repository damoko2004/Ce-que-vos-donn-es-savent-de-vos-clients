# R-PG3-09 — R / Quarto - générer le mini-rapport Word	R-PG3-09
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

generer_mini_rapport <- function(resultats_valides, sortie_docx) {
  if (!file.exists(resultats_valides))
    stop("resultats valides introuvables : rapport refuse")
  if (!requireNamespace("quarto", quietly = TRUE))
    stop("le paquet quarto est requis")
  # mini_report.qmd lit uniquement le CSV de resultats valides passe en
  # parametre. Il ne charge ni survey_clean.parquet ni les microdonnees.
  tmp <- tempfile("surveyops_report_")
  dir.create(tmp)
  quarto::quarto_render(
    input = "surveyops/report/mini_report.qmd",
    output_format = "docx",
    output_file = "mini_rapport.docx",
    output_dir = tmp,
    execute_params = list(resultats = normalizePath(resultats_valides)))
  produit <- file.path(tmp, "mini_rapport.docx")
  if (!file.exists(produit)) stop("Quarto n a pas produit le rapport")
  if (!file.copy(produit, sortie_docx, overwrite = TRUE))
    stop("copie du rapport impossible")
  invisible(sortie_docx)
}
