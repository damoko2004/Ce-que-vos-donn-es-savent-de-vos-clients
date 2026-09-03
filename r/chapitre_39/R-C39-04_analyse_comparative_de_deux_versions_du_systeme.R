# R-C39-04 — analyse comparative de deux versions du système
# Chapitre 39 — Projet de production — Douze mois chez Kairo
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(jsonlite); library(tidyr); library(ggplot2)
eval_v <- function(chemin) {
  stream_in(file(chemin), verbose = FALSE) %>%
    as_tibble() %>%
    mutate(version = ifelse(grepl("1.4.1", basename(chemin)), "avant", "apres"))
}
res <- bind_rows(eval_v("eval/resultats_1.4.1.jsonl"),
                 eval_v("eval/resultats_1.4.2.jsonl"))
# Vue d ensemble : la moyenne cache les regressions par famille de cas.
synthese <- res %>%
  group_by(version, famille) %>%
  summarise(n = n(),
            conformite = mean(conforme),
            fidelite   = mean(fidele),
            abstention = mean(abstenu),
            latence_p90 = quantile(latence_ms, 0.90),
            cout_moyen  = mean(cout),
            .groups = "drop")
# Le tableau qui decide : gain ou regression, cas par cas.
comparaison <- res %>%
  select(id, famille, version, conforme) %>%
  pivot_wider(names_from = version, values_from = conforme, values_fill = FALSE) %>%
  mutate(evolution = case_when(
    !avant &  apres ~ "corrige",
    avant  & !apres ~ "REGRESSION",
    TRUE            ~ "inchange"))
count(comparaison, evolution)
filter(comparaison, evolution == "REGRESSION")   # a traiter avant livraison
ggplot(synthese, aes(famille, conformite, fill = version)) +
  geom_col(position = "dodge") +
  geom_hline(yintercept = 0.98, linetype = "dashed") +
  coord_flip() +
  labs(x = NULL, y = "Taux de conformite", fill = NULL) +
  theme_minimal(base_size = 13)
