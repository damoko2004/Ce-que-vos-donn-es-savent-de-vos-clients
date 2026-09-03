# R-PG2-04 — backtest glissant, Gini et indice de stabilité
# Projet Quant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(purrr); library(pROC)
gini <- function(y, p) 2 * as.numeric(auc(y, p, quiet = TRUE)) - 1
backtest_glissant <- function(panel, formule, dates) {
  if (length(dates) < 4) return(tibble())
  map_dfr(4:length(dates), function(i) {
    train <- panel %>% filter(cohorte %in% dates[1:(i - 1)])
    test  <- panel %>% filter(cohorte == dates[i])
    if (nrow(train) == 0 || nrow(test) == 0 ||
        n_distinct(train$defaut) < 2 || n_distinct(test$defaut) < 2)
      return(tibble())
    m <- glm(formule, data = train, family = binomial)
    p <- predict(m, newdata = test, type = "response")
    tibble(cohorte = dates[i], n = nrow(test),
           gini = round(gini(test$defaut, p), 3),
           pd_moyenne_predite = round(mean(p), 4),
           taux_defaut_observe = round(mean(test$defaut), 4),
           ecart_calibration = round(mean(p) - mean(test$defaut), 4))
  })
}
psi <- function(reference, courant, bins = 10) {
  reference <- reference[is.finite(reference)]
  courant <- courant[is.finite(courant)]
  if (!length(reference) || !length(courant) || length(unique(reference)) < 2)
    return(NA_real_)
  coupures <- unique(quantile(reference, probs = seq(0, 1, length.out = bins + 1),
                              na.rm = TRUE, names = FALSE))
  if (length(coupures) < 2) return(NA_real_)
  coupures[1] <- -Inf; coupures[length(coupures)] <- Inf
  br <- cut(reference, coupures, include.lowest = TRUE)
  bc <- cut(courant, coupures, include.lowest = TRUE)
  lev <- levels(br)
  r <- table(factor(br, levels = lev)) / length(reference)
  c <- table(factor(bc, levels = lev)) / length(courant)
  r <- pmax(as.numeric(r), 1e-6); c <- pmax(as.numeric(c), 1e-6)
  sum((c - r) * log(c / r))
}
test_calibration <- function(test, p, n_classes = 10) {
  tibble(p = p, y = test$defaut) %>%
    mutate(classe = ntile(p, min(n_classes, n()))) %>%
    group_by(classe) %>%
    summarise(n = n(), predit = mean(p), observe = mean(y),
              ecart = mean(p) - mean(y), .groups = "drop") %>%
    mutate(se = sqrt(pmax(observe * (1 - observe) / n, 0)),
           dans_intervalle = abs(ecart) < 1.96 * se)
}
