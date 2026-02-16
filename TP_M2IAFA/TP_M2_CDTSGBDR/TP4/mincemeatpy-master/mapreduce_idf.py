#!/usr/bin/env python
import mincemeat
import os
import math

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
    return ' '.join(mots)

def lire_fichiers(chemin_repertoire):
    contenu_fichiers = []
    
    for nom_fichier in os.listdir(chemin_repertoire):
        chemin_complet = os.path.join(chemin_repertoire, nom_fichier)
        if os.path.isfile(chemin_complet):
            try:
                with open(chemin_complet, 'r', encoding='utf-8') as fichier:
                    contenu = fichier.read()
                    contenu = nettoyer_texte(contenu)
                    contenu_fichiers.append(contenu)
            except Exception as e:
                print(f"Erreur lors de la lecture de {nom_fichier}: {str(e)}")               
    return contenu_fichiers

def load_stop_words(filename):
    with open(filename, 'r') as f:
         return set(word.strip().lower() for word in f)

# par document : 
#    - pour chaque terme, son nombre d’occurrences par document
# .  - le nombre de termes par documents
# .  - pour chaque terme, sa fréquence d’apparition par document
def collectfn(k, v):

    total_terms = 0
    term_count  = {}         
    for w in v[0].split() : 
        if w in term_count: 
            term_count[w] += 1
        else: 
            term_count[w] = 1 
        total_terms += 1
    term_frequency = {term: count / total_terms for term, count in term_count.items()}
    return { 'doc_num': k, 'term_count': term_count, 'total_terms': total_terms,
            'term_frequency': term_frequency, "term_doc_count" : term_doc_count} 


def mapfn(k, v):
    global term_doc_count
    if k == "start":
        term_doc_count = dict()
        return
           
    unique_terms = set(v.split())
    for term in unique_terms:
        if term in term_doc_count: 
            term_doc_count[term] += 1
        else: 
            term_doc_count[term] = 1      
    yield k,v

def reducefn(k, vs):
    return vs[0]

datasource={}
# Utilisation du programme
chemin_repertoire = "../Data" 
contenu_fichiers = lire_fichiers(chemin_repertoire)
datasource = dict(enumerate(contenu_fichiers))

start = {"start":"start"}
datasource = {**start , **datasource}

s = mincemeat.Server()
s.datasource = datasource

s.mapfn = mapfn
s.reducefn = reducefn
s.collectfn = collectfn

results = s.run_server(password="changeme")

nbDoc = len(results)

idf = {}

for k, vs in results.items() : 
    for term, doc_count in vs['term_doc_count'].items():
        if term in idf: 
           idf[term] += doc_count
        else :   
           idf[term] = doc_count 

    print(f'results document : {k} : doc_num : {vs["doc_num"]}\n ')
    print(f'results document : {k} : term_count : {vs["term_count"]}\n ')
    print(f'results document : {k} : total_terms : {vs["total_terms"]}\n ')
    print(f'results document : {k} : term_frequency : {vs["term_frequency"]}\n\n\n\n ')

for term, doc_count in idf.items():
    idf[term] = math.log(nbDoc / doc_count)
    print(f'results idf term : {term} doc_count {doc_count} value : {idf[term]}')