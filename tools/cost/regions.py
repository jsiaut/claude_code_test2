"""v4, point 5 (docs/V4_COST.md, 3.2) : relevé des régions, délimitées à la lecture des copies bench/<langage>_cv.

LANGS[langage] = {
  "dir": répertoire de la copie,
  "files": {fichier: empreinte git (git hash-object) ; tools/cost/count.py refuse de compter si un fichier a changé},
  "regions": {nom: [(fichier, première ligne, dernière ligne), …]} (bornes comprises, lignes numérotées à partir de 1),
  "forms": {"noyau|variante|paramètre": (fonction d'entrée, [régions])},
}
Une région contient ce que la forme ajoute au harnais (3.2) : fonctions appelées dans la zone chronométrée et celles
qu'elles appellent dans le fichier, types et constantes propres à la forme, préparation propre (réserve de fils,
tampons, conversion des données). Le harnais commun (mesure du temps, chargement, somme de contrôle, choix de la
variante) n'en fait pas partie. Une région partagée par plusieurs formes compte dans chacune."""

LANGS = {}
