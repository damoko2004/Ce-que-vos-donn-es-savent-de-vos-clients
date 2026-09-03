# R-PG3-07 — le poste de commandement de la collecte	R-PG3-07
# Projet Surveyops
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(shiny); library(dplyr); library(DT)
library(leaflet); library(ggplot2); library(readr)
source("surveyops/report/generer_rapport.R")
q <- read_csv("surveyops/dashboard/questionnaires.csv", show_col_types = FALSE)
strates <- read_csv("surveyops/dashboard/strates.csv", show_col_types = FALSE)
plan_du_jour <- read_csv("surveyops/dashboard/plan_du_jour.csv", show_col_types = FALSE)
enqueteurs <- read_csv("surveyops/dashboard/enqueteurs.csv", show_col_types = FALSE)
grappes <- read_csv("surveyops/dashboard/grappes.csv", show_col_types = FALSE)
PLAN_TAB <- "surveyops/publication/plan_tabulation.csv"
TAB_VALIDEES <- "surveyops/publication/tabulations_validees.csv"
stopifnot(all(c("etat") %in% names(q)),
          all(c("strate", "ecart_pct") %in% names(strates)),
          all(c("lon_prevu", "lat_prevu", "lon_reel",
                "lat_reel", "suspect", "grappe") %in% names(grappes)))
lire_ou_message <- function(chemin, message) {
  if (!file.exists(chemin)) return(tibble::tibble(statut = message))
  read_csv(chemin, show_col_types = FALSE)
}
ui <- fluidPage(
  titlePanel("SurveyOps - pilotage de la collecte"),
  fluidRow(
    column(3, wellPanel(h3(textOutput("realise")), "questionnaires")),
    column(3, wellPanel(h3(textOutput("avancement")), "de l objectif")),
    column(3, wellPanel(h3(textOutput("en_revue")), "en revue")),
    column(3, wellPanel(h3(textOutput("retard")), "strates en retard"))),
  tabsetPanel(
    tabPanel("Plan du jour", DTOutput("plan")),
    tabPanel("Enqueteurs", DTOutput("enq")),
    tabPanel("Couverture", leafletOutput("carte", height = "520px")),
    tabPanel("Avancement", plotOutput("strates", height = "420px")),
    tabPanel("Plan de tabulation", DTOutput("plan_tab"), hr(),
             DTOutput("tabulations"),
             downloadButton("csv_tab", "CSV"),
             downloadButton("xlsx_tab", "Excel")),
    tabPanel("Rapport",
             p("Genere uniquement depuis les resultats statistiques valides."),
             downloadButton("rapport_docx", "Extraire le mini-rapport Word"))))
server <- function(input, output) {
  output$realise <- renderText(format(nrow(q), big.mark = " "))
  output$avancement <- renderText(sprintf("%.1f %%", 100 * nrow(q) / 18000))
  output$en_revue <- renderText(sum(q$etat == "EN_REVUE", na.rm = TRUE))
  output$retard <- renderText(sum(strates$ecart_pct < -15, na.rm = TRUE))
  output$plan <- renderDT(datatable(plan_du_jour, rownames = FALSE))
  output$enq <- renderDT(datatable(enqueteurs, rownames = FALSE))
  output$carte <- renderLeaflet({
    leaflet(grappes) %>% addTiles() %>%
      addCircleMarkers(~lon_prevu, ~lat_prevu, radius = 5,
                       color = "#1B3A57", label = ~grappe) %>%
      addCircleMarkers(~lon_reel, ~lat_reel, radius = 4,
                       color = ~ifelse(suspect, "#B3402F", "#9C6B3C"))
  })
  output$strates <- renderPlot({
    ggplot(strates, aes(reorder(strate, ecart_pct), ecart_pct)) +
      geom_col(aes(fill = ecart_pct < -15), show.legend = FALSE) +
      geom_hline(yintercept = -15, linetype = "dashed") + coord_flip() +
      labs(x = NULL, y = "Ecart a l avancement attendu (%)") +
      theme_minimal(base_size = 13)
  })
  plan_tab <- reactive(lire_ou_message(PLAN_TAB, "Plan de tabulation non publie"))
  tab_val <- reactive(lire_ou_message(TAB_VALIDEES, "Aucune tabulation validee"))
  output$plan_tab <- renderDT(datatable(plan_tab(), rownames = FALSE))
  output$tabulations <- renderDT(datatable(tab_val(), rownames = FALSE))
  output$csv_tab <- downloadHandler(
    filename = function() "tabulations_validees.csv",
    content = function(file) {
      req(file.exists(TAB_VALIDEES)); file.copy(TAB_VALIDEES, file, overwrite = TRUE)
    })
  output$xlsx_tab <- downloadHandler(
    filename = function() "tabulations_validees.xlsx",
    content = function(file) {
      req(file.exists(TAB_VALIDEES))
      writexl::write_xlsx(list(resultats = read_csv(TAB_VALIDEES,
                           show_col_types = FALSE)), file)
    })
  output$rapport_docx <- downloadHandler(
    filename = function() "SurveyOps_mini_rapport.docx",
    content = function(file) {
      req(file.exists(TAB_VALIDEES)); generer_mini_rapport(TAB_VALIDEES, file)
    })
}
shinyApp(ui, server)
