# R-C02-02 — équivalent
# Chapitre 2 — Construire une vue client 360°
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr)
DATE_REF <- as.Date("2025-10-01")
cmd <- read.csv("commandes.csv") %>%
  mutate(date_commande = as.Date(date_commande))
agg <- cmd %>%
  filter(date_commande < DATE_REF,
         date_commande >= DATE_REF - 365) %>%
  group_by(client_id) %>%
  summarise(nb_achats_12m = n(),
            ca_12m        = sum(montant),
            marge_12m     = sum(marge),
            derniere_cmd  = max(date_commande)) %>%
  mutate(recence_jours = as.numeric(DATE_REF - derniere_cmd),
         panier_moyen  = ca_12m / nb_achats_12m)
