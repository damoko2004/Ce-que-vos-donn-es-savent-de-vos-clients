# R-C32-03 — équivalent avec quanteda
# Chapitre 32 — Cas 14 — Ce que vos clients écrivent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(quanteda); library(quanteda.textstats); library(topicmodels); library(readr)
verb <- read_csv("verbatims.csv", show_col_types = FALSE)
stopifnot(all(c("texte", "client_id", "canal", "date") %in% names(verb)))
meta <- as.data.frame(verb[, c("client_id", "canal", "date")])
corp <- corpus(verb$texte, docvars = meta)
toks <- tokens(corp, remove_punct = TRUE) |>
  tokens_tolower() |>
  tokens_compound(phrase(c("service client", "delai de livraison"))) |>
  tokens_remove(stopwords("fr"))
dfmat <- dfm(toks) |> dfm_trim(min_docfreq = 8) |> dfm_tfidf()
topfeatures(dfmat, 20)
dfm_counts <- dfm(toks) |> dfm_trim(min_docfreq = 8)
if (ndoc(dfm_counts) < 8 || nfeat(dfm_counts) < 8)
  stop("corpus trop petit pour 8 themes")
lda <- LDA(convert(dfm_counts, to = "topicmodels"), k = 8)
terms(lda, 10)
