# Spam Classifier — Gmail + DistilBERT

Pipeline complet de classification spam avec apprentissage incrémental.

## Structure

```
spam_classifier/
├── 01_explore.ipynb        # Étape 1 : Exploration + baseline SVM
├── 02_finetune.ipynb       # Étape 2 : Fine-tuning DistilBERT
├── pipeline.py             # Étape 3 : Inférence automatique + réentraînement
└── README.md
```

## Prérequis

```bash
pip install google-auth google-auth-oauthlib google-api-python-client \
            transformers torch accelerate scikit-learn pandas \
            matplotlib seaborn umap-learn joblib
```

## Mise en place Gmail API

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet → Activer l'API Gmail
3. Créer des credentials OAuth2 (type : "Application bureau")
4. Télécharger `credentials.json` dans ce dossier

## Workflow recommandé

### Phase 1 — Bootstrap (une fois)

1. Lancer `01_explore.ipynb`
2. Les labels `SPAM_TRAINING` et `HAM_TRAINING` sont créés dans Gmail
3. Déposer manuellement 50-100 spams et 50-100 mails légitimes dans ces labels
4. Relancer le notebook → entraîne le baseline SVM + visualisation t-SNE

### Phase 2 — Fine-tuning (une fois)

1. Lancer `02_finetune.ipynb`
2. Entraîne DistilBERT sur ton dataset → sauvegarde dans `./distilbert_spam_final`

### Phase 3 — Production (en continu)

```bash
# Classifier les nouveaux mails
python pipeline.py --mode infer

# Réentraîner quand tu as corrigé des erreurs dans Gmail
python pipeline.py --mode retrain

# Les deux en une fois
python pipeline.py --mode both
```

## Boucle d'apprentissage incrémental

```
Nouveaux mails → Inférence → AUTO_SPAM (confiance ≥ 90%)
                           ↓
              Tu corriges les erreurs dans Gmail
              (mauvais spam → déplace vers HAM_TRAINING)
              (spam manqué → déplace vers SPAM_TRAINING)
                           ↓
              python pipeline.py --mode retrain
                           ↓
              Modèle s'améliore progressivement
```

## Paramètres clés

| Paramètre | Valeur | Description |
|---|---|---|
| `CONFIDENCE_THR` | 0.90 | Seuil pour déplacement automatique |
| `MAX_LEN` | 256 | Longueur max en tokens |
| `learning_rate` | 1e-5 | LR faible pour éviter l'oubli catastrophique |
| `num_train_epochs` | 2 | Epochs pour le réentraînement incrémental |
