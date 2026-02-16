#!/usr/bin/env python
import mincemeat
import os

def lire_fichiers(chemin_repertoire):
    contenu_fichiers = []
    
    for nom_fichier in os.listdir(chemin_repertoire):
        chemin_complet = os.path.join(chemin_repertoire, nom_fichier)
        if os.path.isfile(chemin_complet):
            try:
                with open(chemin_complet, 'r', encoding='utf-8') as fichier:
                    contenu = fichier.read()
                    contenu_fichiers.append(contenu)
            except Exception as e:
                print(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}")
    
    return contenu_fichiers

def stopwords(filename):
    with open(filename, 'r') as f:
        return set(word.strip().lower() for word in f)
    
def collectfn(k, v):
    print(f'check_stopwords : {k}')
    if k not in stop_words:
          return True
    else: return False

def mapfn(k, v):
    # print(f' k  -{k} : v  - {v}')
    dico = {}   
    # Vérifier si on traite les stop words
    if k == "stop_words":
        return  # Ne rien faire pour la clé des mots-vides   
    # Accéder aux stop words à partir de la datasource
#    stop_words = datasource["stop_words"]
    for w in v.split():   
        w = w.lower()
        if w not in stop_words:
            print(f'not in stop_words {w}')
            if w in dico: dico[w] += 1
            else: dico[w] = 1  
    for w, nb in dico.items() :  
        yield w, nb        

def reducefn(k, vs):
    # print(f'reducefn - {k} : {vs}')
    return sum(vs)    
      
# Charger les mots-vides
stop_words = stopwords('../stop_words_english.txt')

# Utilisation du programme
chemin_repertoire = "../Data_1"  # Remplacez par le chemin de votre répertoire
contenu_fichiers = lire_fichiers(chemin_repertoire)

# Charger les données
datasource = dict(enumerate(contenu_fichiers))  

# print(f'datasource : {datasource}')
datasource['stop_words'] = stop_words
# print(f'len datasource {len(datasource)} len contenu_fichiers {len(contenu_fichiers)}')

s = mincemeat.Server()
s.datasource = datasource

# Attacher stop_words à la fonction mapfn

s.collectfn = collectfn
s.mapfn = mapfn
s.reducefn = reducefn

results = s.run_server(password="changeme")

if results:
    max_occurrence = max(results.values())
    print(f'max_occurence : {max_occurrence}')
    # Lister les noms ayant le maximum d'occurrences
    noms_max_occurrence = [nom for nom, occurrence in results.items() if occurrence == max_occurrence]
    print(f"Noms avec le plus haut nombre {max_occurrence} d'occurrences {noms_max_occurrence}")
    # rest of your code
else:
    print("No results were returned from the MapReduce job.")    