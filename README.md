# Riconoscimento Vocale - Vosk

Applicazione Windows per il riconoscimento vocale in tempo reale utilizzando la libreria Vosk.

## Caratteristiche

- 🎤 Riconoscimento vocale in streaming
- 🇮🇹 Supporto per la lingua italiana
- 🖱️ Interfaccia grafica semplice e intuitiva
- ⚡ Riconoscimento offline (nessuna connessione internet richiesta dopo l'installazione)
- 📋 Copia e cancella del testo riconosciuto
- 💾 Salvataggio automatico delle impostazioni (modello e microfono selezionati)
- 🎯 Supporto per due modelli vocali (Small 48 MB e Medium 1.2 GB)

## Requisiti

- Windows 10/11
- Python 3.8 o superiore
- Microfono funzionante

## Installazione Rapida

### Metodo 1: Installazione Automatica (Consigliato)

1. Apri il prompt dei comandi o PowerShell nella cartella del progetto
2. Esegui lo script di installazione:

```bash
install_all.bat
```

Oppure fai doppio click su `install_all.bat`.

Lo script installerà automaticamente:
- Tutte le dipendenze Python necessarie
- Ti permetterà di scegliere tra due modelli vocali:
  - **Small (48 MB)**: Più veloce, meno accurato
  - **Medium (1.2 GB)**: Più lento, più accurato

### Metodo 2: Installazione Manuale

1. Installa le dipendenze Python:

```bash
pip install -r requirements.txt
```

2. Scarica il modello vocale italiano:

```bash
python scripts/download_model.py small  # Per il modello Small (48 MB)
python scripts/download_model.py medium  # Per il modello Medium (1.2 GB)
```

## Uso

Dopo l'installazione, avvia l'applicazione con:

```bash
python main.py
```

### Interfaccia

1. **Modello**: Seleziona il modello vocale da utilizzare (Small o Medium)
2. **Microfono**: Seleziona il microfono da utilizzare
3. **ACCENDI/SPEGNI**: Attiva o disattiva il riconoscimento vocale
4. **Cancella**: Pulisce il testo riconosciuto dall'area di testo
5. **Copia**: Copia il testo riconosciuto negli appunti

### Impostazioni

L'applicazione salva automaticamente le tue preferenze in `settings.json`:
- Modello vocale selezionato
- Microfono selezionato

Le impostazioni vengono caricate automaticamente all'avvio dell'applicazione.

## Struttura dei File

```
GTA5ComandiVocali/
├── scripts/             # Script di installazione
│   ├── install_dependencies.py  # Installa le dipendenze
│   └── download_model.py    # Scarica il modello vocale
├── main.py              # Applicazione principale
├── recognizer.py        # Modulo per il riconoscimento vocale
├── requirements.txt     # Dipendenze Python
├── install_all.bat      # Script di installazione automatica
├── avvia_app.bat        # Avvia l'applicazione
├── README.md           # Questo file
├── settings.json        # Impostazioni salvate (creato automaticamente)
└── models/             # Cartella per i modelli (creata automaticamente)
    ├── vosk-model-small-it-0.22/ # Modello Small (48 MB)
    └── vosk-model-it-0.22/       # Modello Medium (1.2 GB)
```

## Dipendenze

| Libreria | Versione | Scopo |
|----------|----------|-------|
| vosk | 0.3.45 | Motore di riconoscimento vocale |
| numpy | 1.26.4 | Elaborazione array audio |
| pyaudio | 0.2.13 | Accesso al microfono |

## Risoluzione dei Problemi

### Errore: "Modello non trovato"

Assicurati che il modello vocale sia stato scaricato correttamente:

```bash
python scripts/download_model.py small  # Per Small
python scripts/download_model.py medium  # Per Medium
```

### Errore: "pyaudio non trovato"

Su Windows, potrebbe essere necessario installare pyaudio manualmente:

1. Scarica il file wheel da: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Installa con: `pip install pyaudio‑<version>‑cp<version>‑<platform>.whl`

### Il riconoscimento non funziona

1. Verifica che il microfono sia funzionante
2. Controlla che i permessi del microfono siano abilitati nelle impostazioni di Windows
3. Assicurati che il modello vocale sia presente nella cartella `models/`

### Microfono salvato non disponibile

Se il microfono salvato nelle impostazioni non è più disponibile, l'applicazione userà automaticamente il primo microfono disponibile.

## Note Tecniche

- **Modelli disponibili**: 
  - Vosk Italian Small (48 MB) - Più veloce, meno accurato
  - Vosk Italian Medium (1.2 GB) - Più lento, più accurato
- **Frequenza di campionamento**: 16000 Hz
- **Formato audio**: 16-bit mono
- **Buffer audio**: 4096 frame

## Licenza

Questo progetto utilizza:
- Vosk (MIT License)
- Python (Python Software Foundation License)

## Contributi

I contributi sono benvenuti! Per apportare modifiche:

1. Fai un fork del repository
2. Crea un branch per la tua feature
3. Commit delle tue modifiche
4. Push al branch
5. Apri una Pull Request

## Versione

- Versione: 1.0.0
- Data: 2024
