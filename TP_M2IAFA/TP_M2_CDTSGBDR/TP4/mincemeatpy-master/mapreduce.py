#!/usr/bin/env python
import mincemeat
import os

import re
import string

def nettoyer_texte(texte):
    ma_chaine = texte
    if isinstance(ma_chaine, list) : 
        ma_chaine = ' '.join(texte)
    ma_chaine = ma_chaine.replace('\ufeff', '')
    ma_chaine = ma_chaine.translate(str.maketrans('', '', string.punctuation))   
    ma_chaine = ma_chaine.lower()
    mots = re.findall(r'\b\w+\b', ma_chaine)
    return [' '.join(mots)]

def lire_fichiers(chemin_repertoire):
    contenu_fichiers = []
    
    for nom_fichier in os.listdir(chemin_repertoire):
        chemin_complet = os.path.join(chemin_repertoire, nom_fichier)
        if os.path.isfile(chemin_complet):
            try:
                with open(chemin_complet, 'r', encoding='utf-8') as fichier:
                    contenu = fichier.read()
                    contenu_fichiers.append(contenu.replace('\ufeff', ''))
            except Exception as e:
                print(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}")               
    return contenu_fichiers

def load_stop_words(filename):
    with open(filename, 'r') as f:
         return set(word.strip().lower() for word in f)


def collectfn(w, vs):
    return vs[0]

def mapfn(k, v):
    global stop_words
    dico={}
    if k == "stopWords":
        stop_words = list(v)
        return      
    for w in v.split(): 
        w = w.lower()  
        if w not in stop_words:
            if w in dico: 
                dico[w] += 1
            else: 
                dico[w] = 1    
    for w, nb in dico.items() :  
        yield w, nb          

def reducefn(k, vs):
    result = sum(vs)
    return result

# Charger les mots-vides
datasource={}
stop_words = load_stop_words('../stop_words_english.txt')
stop_words = nettoyer_texte('\n'.join(map(str, list(stop_words))))

# Utilisation du programme
chemin_repertoire = "../Data" 
contenu_fichiers = lire_fichiers(chemin_repertoire)
#contenu_fichiers = nettoyer_texte(contenu_fichiers)

# The data source can be any dictionary-like object
stopWords = {"stopWords": stop_words}
datasource = dict(enumerate(contenu_fichiers))
datasource = {**stopWords , **datasource}

s = mincemeat.Server()
s.datasource = datasource
s.mapfn = mapfn
s.reducefn = reducefn
s.collectfn = collectfn

results = s.run_server(password="changeme")

#for cle, valeur in results.items():
#    print(f"Le terme {cle}, dénombre {valeur} occurence(s)")

ma_sortie = results.keys()

difference_result = [item for item in ma_sortie if item in stop_words]
print(f"\n\nLes items non filtrés sont : {difference_result} ")

# Trouver le maximum d'occurrences
max_occurrence = max(results.values())
print(f"le nombre d'occurences maximum est : {max_occurrence}")

# Lister les noms ayant le maximum d'occurrences
noms_max_occurrence = [nom for nom, occurrence in results.items() if occurrence == max_occurrence]
print(f"Le terme {noms_max_occurrence} révèle {max_occurrence} occurrences\n\n")