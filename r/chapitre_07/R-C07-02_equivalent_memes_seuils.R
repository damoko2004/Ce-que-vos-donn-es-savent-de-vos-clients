# R-C07-02 — équivalent, mêmes seuils
# Chapitre 7 — Segmenter sans algorithme : PMG et RFM
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr)
clients <- read.csv("clients_360.csv")
SEUIL_DORMANT <- 270; SEUIL_RECENT <- 90
SEUIL_FIDELE  <- 4;   SEUIL_NOUVEAU <- 12
clients <- clients %>% mutate(segment_rfm = case_when(
  recence_jours >  SEUIL_DORMANT                          ~ "Endormis",
  recence_jours <= SEUIL_RECENT  & nb_achats_12m >= SEUIL_FIDELE ~ "Champions",
  anciennete_mois <= SEUIL_NOUVEAU & nb_achats_12m <  SEUIL_FIDELE ~ "Nouveaux",
  recence_jours >  SEUIL_RECENT  & nb_achats_12m >= SEUIL_FIDELE ~ "A reconquerir",
  TRUE                                                    ~ "Reguliers"))
clients %>%
  group_by(segment_rfm) %>%
  summarise(clients = n(), ca = sum(ca_12m)) %>%
  mutate(part_ca = round(ca / sum(ca) * 100, 1)) %>%
  arrange(desc(clients))
