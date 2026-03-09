#!/usr/bin/env python3
"""
Script per scaricare il modello vocale Vosk per la lingua italiana.
Supporta sia Small che Medium model.
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path

# Configurazione dei modelli
MODELS = {
    "small": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip",
        "name": "vosk-model-small-it-0.22",
        "size": "48 MB"
    },
    "medium": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-it-0.22.zip",
        "name": "vosk-model-it-0.22",
        "size": "1.2 GB"
    }
}

MODELS_DIR = "models"

def download_model(model_type="small"):
    """Scarica ed estrae il modello vocale italiano
    
    Args:
        model_type: "small" o "medium"
    """
    config = MODELS.get(model_type.lower())
    if not config:
        print(f"Modello '{model_type}' non trovato! Usa 'small' o 'medium'.")
        return False
    
    MODEL_URL = config["url"]
    MODEL_NAME = config["name"]
    
    print("=" * 60)
    print("SCARICAMENTO MODELLO VOCALE")
    print("=" * 60)
    
    # Crea la cartella models se non esiste
    models_path = Path(MODELS_DIR)
    if not models_path.exists():
        print(f"\nCreazione cartella {MODELS_DIR}...")
        models_path.mkdir()
    
    model_dir = models_path / MODEL_NAME
    zip_file = models_path / f"{MODEL_NAME}.zip"
    
    # Verifica se il modello è già presente
    if model_dir.exists() and any(model_dir.iterdir()):
        print(f"\nModello {MODEL_NAME} già presente!")
        print("=" * 60)
        return True
    
    print(f"\nScaricamento modello {MODEL_NAME} ({config['size']})...")
    print(f"URL: {MODEL_URL}")
    print("Questo potrebbe richiedere alcuni minuti in base alla connessione.\n")
    
    try:
        # Scarica il file zip
        print("Download in corso...")
        urllib.request.urlretrieve(MODEL_URL, str(zip_file), reporthook=download_progress)
        print("\nDownload completato!")
        
        # Estrae il file zip
        print(f"\nEstrazione del modello...")
        with zipfile.ZipFile(str(zip_file), 'r') as zip_ref:
            zip_ref.extractall(MODELS_DIR)
        
        # Rimuove il file zip dopo l'estrazione
        if zip_file.exists():
            os.remove(zip_file)
            print("File zip rimosso.")
        
        print("\n" + "=" * 60)
        print("MODELLO SCARICATO E ESTRATTO CON SUCCESSO!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"ERRORE NELLO SCARICAMENTO DEL MODELLO: {e}")
        print("=" * 60)
        return False

def download_progress(block_num, block_size, total_size):
    """Funzione di callback per mostrare la progressione del download"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, (downloaded / total_size) * 100)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(f"\rDownload: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')

if __name__ == "__main__":
    # Prendi il tipo di modello dagli argomenti della riga di comando
    model_type = sys.argv[1] if len(sys.argv) > 1 else "small"
    download_model(model_type)
