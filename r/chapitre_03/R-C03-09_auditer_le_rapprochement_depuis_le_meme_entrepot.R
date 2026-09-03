# R-C03-09 — auditer le rapprochement depuis le même entrepôt
# Chapitre 3 — Projet — La fabrique du client 360
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(DBI); library(duckdb); library(dplyr); library(ggplot2)
con <- dbConnect(duckdb(), "novaretail.duckdb", read_only = TRUE)
# Taux de rapprochement par source et par methode : c est cette vue
# qui revele une degradation progressive, jamais le taux global.
rappro <- tbl(con, "customer_identity_map") %>%
  group_by(source, methode) %>%
  summarise(n = n(), confiance_moy = mean(confiance), .groups = "drop") %>%
  collect() %>%
  group_by(source) %>%
  mutate(part = round(n / sum(n) * 100, 1)) %>%
  ungroup()
print(rappro)
# Suivi dans le temps : une baisse lente est invisible au jour le jour.
histo <- tbl(con, "data_quality_results") %>%
  filter(controle == "non_rattachees_block") %>%
  collect() %>%
  mutate(taux_rapprochement = 1 - valeur)
ggplot(histo, aes(as.Date(run_date), taux_rapprochement)) +
  geom_line(linewidth = .7) +
  geom_hline(yintercept = 0.99, linetype = "dashed") +
  labs(x = NULL, y = "Taux de rapprochement") +
  theme_minimal(base_size = 13)
