# PY-C33-04 — collecte respectueuse
# Chapitre 33 — Cas 15 — Ce que vos clients parcourent
# Extrait de : Ce que vos donnees savent de vos clients
# Le code s'execute depuis la racine du depot, apres
# generation des donnees : python data/generer.py

import time, random, urllib.robotparser as rp
import pandas as pd, requests
from bs4 import BeautifulSoup
AGENT = "NovaRetailVeille/1.0 (+https://novaretail.example/robot)"
def autorise(url, agent=AGENT):
    base = "/".join(url.split("/")[:3])
    rep = requests.get(base + "/robots.txt", headers={"User-Agent": agent}, timeout=5)
    if rep.status_code >= 400:
        return False
    robot = rp.RobotFileParser()
    robot.parse(rep.text.splitlines())
    return robot.can_fetch(agent, url)
def texte(soup, selecteur, attribut=None):
    noeud = soup.select_one(selecteur)
    if noeud is None:
        return None
    return noeud.get(attribut) if attribut else noeud.get_text(strip=True)
def collecter(url):
    if not autorise(url):
        return None
    rep = requests.get(url, headers={"User-Agent": AGENT}, timeout=10)
    if rep.status_code != 200:
        return None
    time.sleep(random.uniform(3, 6))
    soup = BeautifulSoup(rep.text, "html.parser")
    return {"url": url, "libelle": texte(soup, "h1"),
            "prix": texte(soup, "[itemprop=price]", "content"),
            "dispo": texte(soup, "[itemprop=availability]", "href"),
            "releve_le": pd.Timestamp.now(tz="UTC")}
