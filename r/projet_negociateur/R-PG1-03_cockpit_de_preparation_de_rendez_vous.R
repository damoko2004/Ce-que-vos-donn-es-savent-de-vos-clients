# R-PG1-03 — cockpit de préparation de rendez-vous
# Projet Negociateur
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(shiny); library(dplyr); library(DT); library(ggplot2)
acc <- read.csv("negociation/accords_scored.csv")
stopifnot(all(c("categorie", "enjeu_euros", "signale", "volume_annuel",
                "taux_remise", "attendu", "ecart", "fournisseur") %in% names(acc)))
ui <- fluidPage(
  titlePanel("Preparation de negociation"),
  sidebarLayout(
    sidebarPanel(
      selectInput("cat", "Categorie", choices = sort(unique(acc$categorie))),
      sliderInput("enjeu", "Enjeu minimum (euros)",
                  min = 0, max = 200000, value = 20000, step = 5000),
      checkboxInput("signales", "Uniquement les ecarts signales", TRUE),
      helpText("Ecart = condition obtenue moins condition attendue,",
               "a volume, categorie, duree et service comparables."),
      width = 3),
    mainPanel(
      fluidRow(
        column(4, wellPanel(h4(textOutput("n_fourn")),  "fournisseurs")),
        column(4, wellPanel(h4(textOutput("enjeu_tot")), "enjeu total")),
        column(4, wellPanel(h4(textOutput("ecart_med")), "ecart median"))),
      plotOutput("nuage", height = "320px"),
      DTOutput("table"),
      width = 9)))
server <- function(input, output) {
  filtre <- reactive({
    d <- acc %>% filter(categorie == input$cat, enjeu_euros >= input$enjeu)
    if (input$signales) d <- d %>% filter(signale)
    d %>% arrange(desc(enjeu_euros))
  })
  output$n_fourn   <- renderText(nrow(filtre()))
  output$enjeu_tot <- renderText(
    format(round(sum(filtre()$enjeu_euros)), big.mark = " "))
  output$ecart_med <- renderText(
    sprintf("%+.2f pt", if (nrow(filtre())) median(filtre()$ecart) else NA_real_))
  # Volume en abscisse, condition en ordonnee, attendu en courbe :
  # le negociateur voit d un coup d oeil ou se situe son fournisseur.
  output$nuage <- renderPlot({
    d <- acc %>% filter(categorie == input$cat)
    ggplot(d, aes(volume_annuel, taux_remise)) +
      geom_point(aes(colour = signale), alpha = 0.7, size = 2) +
      geom_line(aes(y = attendu), linewidth = 0.6) +
      scale_x_log10(labels = scales::comma) +
      scale_colour_manual(values = c("grey60", "#9C6B3C"),
                          labels = c("conforme", "ecart signale")) +
      labs(x = "Volume annuel (echelle log)", y = "Taux de remise",
           colour = NULL) +
      theme_minimal(base_size = 13)
  })
  output$table <- renderDT({
    filtre() %>%
      select(fournisseur, taux_remise, attendu, ecart, enjeu_euros) %>%
      datatable(rownames = FALSE, options = list(pageLength = 10)) %>%
      formatRound(c("taux_remise", "attendu", "ecart"), 2) %>%
      formatCurrency("enjeu_euros", currency = " EUR", before = FALSE,
                     digits = 0)
  })
}
shinyApp(ui, server)
