# R-C40-09 — tableau de bord du comité de gouvernance
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(shiny); library(dplyr); library(DT); library(ggplot2); library(readr)
cas <- read_csv("gouvernance/cas_usage.csv", show_col_types = FALSE)
passages <- read_csv("gouvernance/passages_portes.csv", show_col_types = FALSE)
attaques <- read_csv("gouvernance/tests_securite.csv", show_col_types = FALSE)
ui <- fluidPage(
  titlePanel("Programme Agents - portefeuille des cas d usage"),
  fluidRow(
    column(3, wellPanel(h3(textOutput("n_actifs")),  "cas actifs")),
    column(3, wellPanel(h3(textOutput("n_prod")),    "en production")),
    column(3, wellPanel(h3(textOutput("n_arretes")), "arretes")),
    column(3, wellPanel(h3(textOutput("cout_mois")), "cout mensuel"))),
  tabsetPanel(
    tabPanel("Portefeuille",
             plotOutput("entonnoir", height = "300px"),
             DTOutput("table")),
    tabPanel("Passage des portes",
             plotOutput("portes", height = "340px"),
             helpText("Un programme qui ne rejette rien en porte 1",
                      "n explore pas assez.")),
    tabPanel("Securite",
             DTOutput("attaques"),
             helpText("Chaque reussite de l equipe d attaque devient",
                      "un cas permanent du jeu d evaluation."))))
server <- function(input, output) {
  output$n_actifs  <- renderText(sum(cas$statut == "actif"))
  output$n_prod    <- renderText(sum(cas$statut == "production"))
  output$n_arretes <- renderText(sum(cas$statut == "arrete"))
  output$cout_mois <- renderText(
    paste0(format(round(sum(cas$cout_mensuel)), big.mark = " "), " EUR"))
  # Entonnoir : combien entrent, combien passent chaque porte
  output$entonnoir <- renderPlot({
    etapes <- cas %>%
      count(etape = factor(etape,
                           levels = c("qualifie", "prototype",
                                      "mvp", "production")))
    ggplot(etapes, aes(etape, n)) +
      geom_col(fill = "#1B3A57", alpha = 0.9) +
      geom_text(aes(label = n), vjust = -0.4, size = 5) +
      labs(x = NULL, y = "Nombre de cas d usage") +
      theme_minimal(base_size = 13)
  })
  output$portes <- renderPlot({
    ggplot(passages, aes(porte, fill = issue)) +
      geom_bar(position = "fill") +
      scale_y_continuous(labels = scales::percent) +
      scale_fill_manual(values = c("passe" = "#1B3A57",
                                   "arrete" = "#9C6B3C",
                                   "en cours" = "grey70")) +
      labs(x = NULL, y = NULL, fill = NULL) +
      theme_minimal(base_size = 13)
  })
  output$table <- renderDT(
    datatable(select(cas, cas_usage, metier, etape, risque,
                     conformite, cout_mensuel, prochaine_porte),
              rownames = FALSE, options = list(pageLength = 12)))
  output$attaques <- renderDT(
    datatable(select(attaques, cas_usage, date, type, reussite,
                     corrige, ajoute_au_jeu_test), rownames = FALSE))
}
shinyApp(ui, server)
