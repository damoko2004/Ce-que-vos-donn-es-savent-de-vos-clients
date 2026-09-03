# R-PG2-05 — surveillance d’un modèle en production
# Projet Quant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(shiny); library(dplyr); library(ggplot2); library(DT); library(readr)
bt <- read_csv("model_risk/backtest_monitoring.csv", show_col_types = FALSE)
calib <- read_csv("model_risk/calibration_monitoring.csv", show_col_types = FALSE)
stopifnot(all(c("cohorte", "gini", "psi", "ecart_calibration") %in% names(bt)))
stopifnot(all(c("predit", "observe", "n", "dans_intervalle") %in% names(calib)))
SEUILS <- list(gini_min = 0.45, psi_max = 0.25, ecart_calib_max = 0.005)
statut <- function(valeur, seuil, sens = "min") {
  ok <- if (sens == "min") valeur >= seuil else valeur <= seuil
  if (ok) "CONFORME" else "ALERTE"
}
ui <- fluidPage(
  titlePanel("Surveillance du modele PD particuliers"),
  fluidRow(
    column(4, wellPanel(h4(textOutput("gini")),  textOutput("gini_st"))),
    column(4, wellPanel(h4(textOutput("psi")),   textOutput("psi_st"))),
    column(4, wellPanel(h4(textOutput("calib")), textOutput("calib_st")))),
  tabsetPanel(
    tabPanel("Discrimination", plotOutput("p_gini", height = "330px")),
    tabPanel("Calibration",    plotOutput("p_calib", height = "330px")),
    tabPanel("Stabilite",      plotOutput("p_psi", height = "330px")),
    tabPanel("Detail par cohorte", DTOutput("detail"))))
server <- function(input, output) {
  dernier <- reactive(bt %>% slice_max(cohorte, n = 1))
  output$gini    <- renderText(sprintf("Gini %.3f", dernier()$gini))
  output$gini_st <- renderText(statut(dernier()$gini, SEUILS$gini_min))
  output$psi     <- renderText(sprintf("PSI %.3f", dernier()$psi))
  output$psi_st  <- renderText(statut(dernier()$psi, SEUILS$psi_max, "max"))
  output$calib   <- renderText(sprintf("Ecart %+.4f", dernier()$ecart_calibration))
  output$calib_st<- renderText(statut(abs(dernier()$ecart_calibration),
                                     SEUILS$ecart_calib_max, "max"))
  output$p_gini <- renderPlot({
    ggplot(bt, aes(cohorte, gini, group = 1)) +
      geom_line(linewidth = 0.7) + geom_point(size = 2) +
      geom_hline(yintercept = SEUILS$gini_min, linetype = "dashed") +
      labs(x = NULL, y = "Coefficient de Gini") +
      theme_minimal(base_size = 13)
  })
  # Predit contre observe : la diagonale est la reference
  output$p_calib <- renderPlot({
    ggplot(calib, aes(predit, observe, size = n)) +
      geom_abline(linetype = "dashed") +
      geom_point(aes(colour = dans_intervalle), alpha = 0.85) +
      scale_colour_manual(values = c("#B3402F", "#1B3A57"),
                          labels = c("hors intervalle", "conforme")) +
      labs(x = "Taux de defaut predit", y = "Taux observe", colour = NULL) +
      theme_minimal(base_size = 13)
  })
  output$p_psi <- renderPlot({
    ggplot(bt, aes(cohorte, psi, group = 1)) +
      geom_col(fill = "#1B3A57", alpha = 0.85) +
      geom_hline(yintercept = SEUILS$psi_max, linetype = "dashed") +
      labs(x = NULL, y = "Indice de stabilite de population") +
      theme_minimal(base_size = 13)
  })
  output$detail <- renderDT(datatable(bt, rownames = FALSE))
}
shinyApp(ui, server)
