"""
SicilyER-Flow: AWS S3 Data Uploader
Si occupa di prelevare i batch di dati generati dal mock API e caricarli 
in tempo reale sul Data Lake (Amazon S3) in formato JSON.
"""

import boto3
import json
import time
from datetime import datetime
from generator import generate_batch

BUCKET_NAME = "sicilyer-flow-raw"  
PREFIX = "raw-data/"    
UPLOAD_INTERVAL_SEC = 60       # Intervallo di tempo tra un invio e l'altro (60 secondi)

# Inizializza il client AWS (legge in automatico le credenziali configurate con 'aws configure')
s3_client = boto3.client("s3")

def upload_to_datalake():
    """Genera un batch di accessi ospedalieri e lo carica su S3."""
    
    # 1. Estrae i dati dal generatore
    batch = generate_batch(10) 
    
    # 2. Crea un nome file univoco con il timestamp attuale
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"er_admissions_{timestamp}.json"
    s3_key = f"{PREFIX}{file_name}"
    
    try:
        # 3. Esegue l'upload del payload JSON sul bucket S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(batch, ensure_ascii=False),
            ContentType="application/json"
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Upload S3 completato: s3://{BUCKET_NAME}/{s3_key} ({len(batch)} records)")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Errore durante l'upload su S3: {e}")

if __name__ == "__main__":
    print(f"🚀 Avvio Data Pipeline: Ingestion verso AWS S3 (Bucket: {BUCKET_NAME})")
    print(f"⏱️ Frequenza invio: Ogni {UPLOAD_INTERVAL_SEC} secondi. Premi CTRL+C per fermare.\n")
    
    try:
        while True:
            upload_to_datalake()
            time.sleep(UPLOAD_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline di ingestion fermata manualmente dall'utente.")