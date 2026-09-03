# R-C37-03 — le même bandit contextuel
# Chapitre 37 — Cas 19, 20 et 21 — Apprendre en agissant
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(MASS)
BanditOffres <- function(n_offres, dim_contexte, bruit = 1, prior = 1) {
  stopifnot(n_offres > 0, dim_contexte > 0, bruit > 0, prior > 0)
  env <- new.env()
  env$k <- n_offres
  env$sigma2 <- bruit^2
  env$A <- replicate(n_offres, diag(dim_contexte) / prior, simplify = FALSE)
  env$b <- replicate(n_offres, rep(0, dim_contexte), simplify = FALSE)
  env
}
choisir <- function(bandit, x) {
  scores <- vapply(seq_len(bandit$k), function(i) {
    cov <- solve(bandit$A[[i]])
    mu <- as.vector(cov %*% bandit$b[[i]])
    theta <- mvrnorm(1, mu, cov)
    sum(x * theta)
  }, numeric(1))
  which.max(scores)
}
apprendre <- function(bandit, x, offre, recompense) {
  if (offre < 1 || offre > bandit$k) stop("offre hors plage")
  bandit$A[[offre]] <- bandit$A[[offre]] + outer(x, x) / bandit$sigma2
  bandit$b[[offre]] <- bandit$b[[offre]] + recompense * x / bandit$sigma2
  invisible(bandit)
}
COUTS <- c(12, 8, 3, 0, 22)
PLANCHER <- 0.05
campagne_mensuelle <- function(bandit, clients, contextes) {
  purrr::map_dfr(seq_along(clients), function(i) {
    if (runif(1) < PLANCHER) {
      offre <- sample.int(bandit$k, 1); mode <- "exploration"
    } else {
      offre <- choisir(bandit, contextes[i, ]); mode <- "exploitation"
    }
    tibble::tibble(client = clients[i], offre = offre,
                   mode = mode, cout = COUTS[offre])
  })
}
