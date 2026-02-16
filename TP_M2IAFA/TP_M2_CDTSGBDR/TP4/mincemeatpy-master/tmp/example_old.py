#!/usr/bin/env python
import mincemeat

_data = ["Humpty Dumpty sat on a wall",
        "Humpty Dumpty had a great fall",
        "All the King's horses and all the King's men",
        "Couldn't put Humpty together again",
        ]

import os

def lire_fichiers(chemin_repertoire):
    contenu_fichiers = {}
    
    for nom_fichier in os.listdir(chemin_repertoire):
        chemin_complet = os.path.join(chemin_repertoire, nom_fichier)
        if os.path.isfile(chemin_complet):
            try:
                with open(chemin_complet, 'r', encoding='utf-8') as fichier:
                    contenu = fichier.read()
                    contenu_fichiers[nom_fichier] = contenu
            except Exception as e:
                print(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}")
    
    return contenu_fichiers

# Utilisation du programme
chemin_repertoire = "../Data"  # Remplacez par le chemin de votre répertoire
data = lire_fichiers(chemin_repertoire)

# Affichage du contenu de


# The data source can be any dictionary-like object
datasource = dict(enumerate(data))

def mapfn(k, v):
    for w in v.split():
        yield w, 1

def reducefn(k, vs):
    result = sum(vs)
    return result

s = mincemeat.Server()
s.datasource = datasource
s.mapfn = mapfn
s.reducefn = reducefn

results = s.run_server(password="changeme")
print(results)
