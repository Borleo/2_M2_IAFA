"""
pipeline.py — Inférence automatique + boucle d'apprentissage incrémental

Usage :
    python pipeline.py --mode infer    # Classifie les nouveaux mails
    python pipeline.py --mode retrain  # Réentraîne sur les labels corrigés
    python pipeline.py --mode both     # Inférence puis réentraînement
"""

import os
import re
import base64
import argparse
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Gmail
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ML
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer
)
from torch.utils.data import Dataset
from sklearn.metrics import classification_report

# ─── Configuration ────────────────────────────────────────────────────────────

SCOPES         = ['https://www.googleapis.com/auth/gmail.modify']
MODEL_PATH     = './distilbert_spam_final'   # Chemin du modèle fine-tuné
DATASET_PATH   = './dataset.csv'             # Dataset cumulatif
MAX_LEN        = 256
BATCH_SIZE     = 32
CONFIDENCE_THR = 0.90  # Seuil de confiance pour archivage automatique

# Labels Gmail
SPAM_LABEL     = 'SPAM_TRAINING'
HAM_LABEL      = 'HAM_TRAINING'
AUTO_SPAM_LABEL = 'AUTO_SPAM'  # Créé automatiquement par le pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
log = logging.getLogger(__name__)

# ─── Gmail helpers ─────────────────────────────────────────────────────────────

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def get_or_create_label(service, name):
    existing = service.users().labels().list(userId='me').execute().get('labels', [])
    for label in existing:
        if label['name'] == name:
            return label['id']
    new = service.users().labels().create(
        userId='me',
        body={'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    ).execute()
    log.info(f'Label "{name}" créé.')
    return new['id']


def fetch_inbox_emails(service, max_results=100):
    """Récupère les mails non lus de la boîte de réception."""
    messages_ref = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=max_results
    ).execute().get('messages', [])

    emails = []
    for msg_ref in messages_ref:
        msg = service.users().messages().get(
            userId='me', id=msg_ref['id'], format='full'
        ).execute()
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}

        body = ''
        parts = msg['payload'].get('parts', [msg['payload']])
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break

        emails.append({
            'id':      msg_ref['id'],
            'subject': headers.get('Subject', ''),
            'sender':  headers.get('From', ''),
            'body':    body
        })

    return emails


def move_to_label(service, msg_id, add_label_id, remove_label_ids=None):
    """Déplace un mail vers un label donné."""
    body = {'addLabelIds': [add_label_id]}
    if remove_label_ids:
        body['removeLabelIds'] = remove_label_ids
    service.users().messages().modify(userId='me', id=msg_id, body=body).execute()

# ─── Prétraitement ─────────────────────────────────────────────────────────────

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', ' URL ', text)
    text = re.sub(r'\S+@\S+', ' EMAIL ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─── Dataset PyTorch ───────────────────────────────────────────────────────────

class EmailDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.encodings = tokenizer(
            list(texts), truncation=True,
            padding='max_length', max_length=max_len, return_tensors='pt'
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            'input_ids':      self.encodings['input_ids'][idx],
            'attention_mask': self.encodings['attention_mask'][idx],
            'labels':         self.labels[idx]
        }

# ─── Inférence ─────────────────────────────────────────────────────────────────

def run_inference(service):
    """
    Récupère les nouveaux mails non lus, prédit spam/ham,
    et déplace les spams à haute confiance vers AUTO_SPAM.
    Enregistre les prédictions dans predictions_log.csv.
    """
    log.info('=== MODE INFÉRENCE ===')

    # Chargement du modèle
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    log.info(f'Modèle chargé sur {device}')

    # Récupération des mails
    emails = fetch_inbox_emails(service)
    if not emails:
        log.info('Aucun nouveau mail à traiter.')
        return

    log.info(f'{len(emails)} mails récupérés.')

    # Prédictions
    texts = [clean_text(e['subject'] + ' ' + e['body']) for e in emails]
    auto_spam_id = get_or_create_label(service, AUTO_SPAM_LABEL)

    results = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_emails = emails[i:i + BATCH_SIZE]

        encoding = tokenizer(
            batch_texts, truncation=True,
            padding='max_length', max_length=MAX_LEN,
            return_tensors='pt'
        ).to(device)

        with torch.no_grad():
            logits = model(**encoding).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()

        for j, email in enumerate(batch_emails):
            spam_prob = float(probs[j][1])
            predicted = 'spam' if spam_prob > 0.5 else 'ham'
            confident = spam_prob >= CONFIDENCE_THR

            results.append({
                'id':        email['id'],
                'subject':   email['subject'],
                'sender':    email['sender'],
                'predicted': predicted,
                'spam_prob': round(spam_prob, 4),
                'confident': confident,
                'timestamp': datetime.now().isoformat()
            })

            # Déplacement automatique si spam très confiant
            if predicted == 'spam' and confident:
                move_to_label(service, email['id'], auto_spam_id, remove_label_ids=['INBOX'])
                log.info(f"  → SPAM ({spam_prob:.1%}) : {email['subject'][:60]}")
            else:
                log.info(f"  → HAM  ({1-spam_prob:.1%}) : {email['subject'][:60]}")

    # Sauvegarde du log
    log_path = Path('predictions_log.csv')
    df_log = pd.DataFrame(results)
    if log_path.exists():
        df_log = pd.concat([pd.read_csv(log_path), df_log], ignore_index=True)
    df_log.to_csv(log_path, index=False)

    spam_count = sum(1 for r in results if r['predicted'] == 'spam' and r['confident'])
    log.info(f'\nRésumé : {spam_count}/{len(results)} mails déplacés vers {AUTO_SPAM_LABEL}')
    log.info(f'Log sauvegardé dans {log_path}')


# ─── Réentraînement incrémental ────────────────────────────────────────────────

def run_retrain(service):
    """
    Récupère les mails des labels SPAM_TRAINING et HAM_TRAINING (corrections manuelles),
    les ajoute au dataset cumulatif, et réentraîne le modèle.
    """
    log.info('=== MODE RÉENTRAÎNEMENT ===')

    # Récupération des labels
    spam_id = get_or_create_label(service, SPAM_LABEL)
    ham_id  = get_or_create_label(service, HAM_LABEL)

    def fetch_label(label_id, label_val):
        from 01_explore import fetch_emails_by_label  # noqa — import relatif simplifié
        pass

    # Version inline (sans import croisé entre notebooks)
    def _fetch(label_id, label_value):
        messages_ref = service.users().messages().list(
            userId='me', labelIds=[label_id], maxResults=1000
        ).execute().get('messages', [])
        rows = []
        for msg_ref in messages_ref:
            msg = service.users().messages().get(
                userId='me', id=msg_ref['id'], format='full'
            ).execute()
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            body = ''
            for part in msg['payload'].get('parts', [msg['payload']]):
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
            rows.append({
                'subject': headers.get('Subject', ''),
                'sender':  headers.get('From', ''),
                'body':    body,
                'label':   label_value
            })
        return rows

    spam_rows = _fetch(spam_id, 1)
    ham_rows  = _fetch(ham_id, 0)
    log.info(f'Exemples récupérés — Spam: {len(spam_rows)} | Ham: {len(ham_rows)}')

    # Fusion avec le dataset existant
    df_new = pd.DataFrame(spam_rows + ham_rows)
    df_new['text'] = df_new['subject'].fillna('') + ' ' + df_new['body'].fillna('')
    df_new['text_clean'] = df_new['text'].apply(clean_text)

    if Path(DATASET_PATH).exists():
        df_existing = pd.read_csv(DATASET_PATH)
        df_all = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates(
            subset=['text_clean']
        )
    else:
        df_all = df_new

    df_all.to_csv(DATASET_PATH, index=False)
    log.info(f'Dataset mis à jour : {len(df_all)} exemples au total')

    if len(df_all) < 20:
        log.warning('Pas assez de données pour réentraîner (minimum 20 exemples).')
        return

    # Réentraînement
    from sklearn.model_selection import train_test_split
    X = df_all['text_clean'].values
    y = df_all['label'].values
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH, num_labels=2)

    train_ds = EmailDataset(X_train, y_train, tokenizer, MAX_LEN)
    val_ds   = EmailDataset(X_val,   y_val,   tokenizer, MAX_LEN)

    training_args = TrainingArguments(
        output_dir='./distilbert_spam_retrain',
        num_train_epochs=2,                    # Moins d'epochs pour l'incrémental
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        warmup_ratio=0.05,
        weight_decay=0.01,
        learning_rate=1e-5,                    # LR plus faible pour ne pas oublier
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        logging_steps=10,
        fp16=torch.cuda.is_available(),
        report_to='none'
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds
    )

    trainer.train()

    # Sauvegarde du modèle mis à jour
    model.save_pretrained(MODEL_PATH)
    tokenizer.save_pretrained(MODEL_PATH)
    log.info(f'✓ Modèle réentraîné et sauvegardé dans {MODEL_PATH}')

    # Évaluation rapide
    preds_output = trainer.predict(val_ds)
    y_pred = np.argmax(preds_output.predictions, axis=-1)
    print('\n' + classification_report(y_val, y_pred, target_names=['Ham', 'Spam']))


# ─── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Spam classifier pipeline')
    parser.add_argument('--mode', choices=['infer', 'retrain', 'both'],
                        default='infer', help='Mode d\'exécution')
    args = parser.parse_args()

    service = get_gmail_service()

    if args.mode in ('infer', 'both'):
        run_inference(service)

    if args.mode in ('retrain', 'both'):
        run_retrain(service)
