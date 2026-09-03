# R-C40-08 — analyse comparative des modèles testés
# Chapitre 40 — Projet de passage à l’échelle — Le programme Agents
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

library(dplyr); library(tidyr); library(ggplot2)
comp <- readr::read_csv("eval/comparatif_modeles.csv")
# colonnes : modele, cas_usage, conformite, fidelite, latence_p90_ms,
#            cout_1k_requetes, cout_hebergement_1k,
#            cout_exploitation_1k, hebergeable_interne
# Regle 3 : le cout complet, pas le prix affiche.
comp <- comp %>%
  mutate(cout_complet = cout_1k_requetes + cout_hebergement_1k +
           cout_exploitation_1k)
# On ne cherche pas un gagnant, on cherche la frontiere efficace.
frontiere <- comp %>%
  group_by(cas_usage) %>%
  arrange(cout_complet, desc(conformite)) %>%
  mutate(meilleur_moins_cher = lag(cummax(conformite), default = -Inf),
         domine = meilleur_moins_cher >= conformite) %>%
  ungroup()
ggplot(frontiere, aes(cout_complet, conformite)) +
  geom_point(aes(colour = hebergeable_interne,
                 shape = domine), size = 3) +
  geom_hline(yintercept = 0.95, linetype = "dashed") +
  facet_wrap(~ cas_usage) +
  scale_colour_manual(values = c("grey60", "#1B3A57"),
                      labels = c("externe", "hebergeable en interne")) +
  labs(x = "Cout complet pour 1000 requetes (euros)",
       y = "Taux de conformite", colour = NULL, shape = NULL) +
  theme_minimal(base_size = 13)
# Les modeles domines : plus chers ET moins conformes qu un autre.
frontiere %>% filter(domine) %>% count(modele, sort = TRUE)
