# R-C39-05 — console de revue des échecs d’évaluation
# Chapitre 39 — Projet de production — Douze mois chez Kairo
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(shiny); library(dplyr); library(DT); library(jsonlite); library(tidyr)
eval_v <- function(chemin) {
  stream_in(file(chemin), verbose = FALSE) %>%
    as_tibble() %>%
    mutate(version = ifelse(grepl("1.4.1", basename(chemin)), "avant", "apres"))
}
res <- bind_rows(eval_v("eval/resultats_1.4.1.jsonl"),
                 eval_v("eval/resultats_1.4.2.jsonl"))
comparaison <- res %>%
  select(id, version, conforme) %>%
  pivot_wider(names_from = version, values_from = conforme, values_fill = FALSE) %>%
  mutate(evolution = case_when(
    !avant & apres ~ "corrige", avant & !apres ~ "REGRESSION",
    TRUE ~ "inchange"))
ui <- fluidPage(
  titlePanel("Revue des cas d evaluation"),
  sidebarLayout(
    sidebarPanel(
      selectInput("version", "Version", choices = unique(res$version)),
      selectInput("famille", "Famille de cas",
                  choices = c("toutes", sort(unique(res$famille)))),
      radioButtons("filtre", "Afficher",
                   c("Echecs seulement" = "echec",
                     "Regressions seulement" = "regression",
                     "Tous les cas" = "tous")),
      hr(),
      actionButton("ajouter", "Proposer au jeu de reference",
                   class = "btn-primary"),
      helpText("La proposition est journalisee ; son ajout au jeu de reference",
               "reste une validation humaine."), width = 3),
    mainPanel(DTOutput("cas"), hr(), h4("Detail du cas selectionne"),
              verbatimTextOutput("question"), verbatimTextOutput("reponse"),
              verbatimTextOutput("trace"), width = 9)))
server <- function(input, output, session) {
  cas <- reactive({
    d <- res %>% filter(version == input$version)
    if (input$famille != "toutes") d <- d %>% filter(famille == input$famille)
    if (input$filtre == "echec") d <- d %>% filter(!conforme | !fidele)
    if (input$filtre == "regression") d <- d %>% semi_join(
      filter(comparaison, evolution == "REGRESSION"), by = "id")
    d
  })
  output$cas <- renderDT(datatable(
    select(cas(), id, famille, conforme, fidele, abstenu, latence_ms, cout),
    selection = "single", rownames = FALSE))
  courant <- reactive({
    i <- input$cas_rows_selected
    if (length(i)) cas()[i, , drop = FALSE] else NULL
  })
  output$question <- renderText(
    if (is.null(courant())) "" else paste("QUESTION :", courant()$question))
  output$reponse <- renderText(
    if (is.null(courant())) "" else paste("REPONSE :", courant()$reponse))
  output$trace <- renderText(if (is.null(courant())) "" else paste(
    "TRACE :", toJSON(courant()$trace, pretty = TRUE)))
  observeEvent(input$ajouter, {
    d <- courant(); req(is.data.frame(d), nrow(d) == 1)
    dir.create("eval", showWarnings = FALSE, recursive = TRUE)
    journal <- "eval/candidats_jeu_reference.csv"
    ligne <- data.frame(id=d$id, famille=d$famille, question=d$question,
                        version=d$version, propose_le=as.character(Sys.time()))
    write.table(ligne, journal, sep=",", row.names=FALSE,
                col.names=!file.exists(journal), append=file.exists(journal),
                qmethod="double")
    showNotification("Cas propose pour revue humaine.", type="message")
  })
}
shinyApp(ui, server)
