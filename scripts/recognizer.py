#!/usr/bin/env python3
"""
Modulo per il riconoscimento vocale in streaming usando Vosk.
Ottimizzato per migliorare l'accuratezza del riconoscimento.
"""

import json
import queue
import threading
import os
import logging

try:
    import vosk
    import numpy as np
    import pyaudio
except ImportError as e:
    print(f"Errore nell'importazione delle librerie: {e}")
    print("Assicurati di aver installato tutte le dipendenze con: pip install -r requirements.txt")
    raise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """
    Classe per gestire il riconoscimento vocale in streaming con Vosk.

    Miglioramenti rispetto alla versione base:
    - Buffer audio più grande (4096) per ridurre artefatti
    - Uso corretto di AcceptWaveform + Result/PartialResult
    - Pre-enfasi audio per aumentare chiarezza delle consonanti
    - Normalizzazione del volume del segnale
    - Soglia di silenzio per evitare falsi positivi
    - Supporto risultati parziali (testo mentre si parla)
    """

    # Parametri audio ottimizzati per Vosk
    CHUNK_SIZE    = 4096   # Buffer più grande = meno frammentazione
    FORMAT        = pyaudio.paInt16
    CHANNELS      = 1
    SAMPLE_RATE   = 16000  # Vosk richiede 16 kHz

    # Pre-emphasis: boost delle frequenze alte (consonanti)
    PRE_EMPHASIS  = 0.97

    # Soglia RMS sotto la quale il frame viene considerato silenzio
    DEFAULT_SILENCE_THRESHOLD = 50  # Valore di default
    
    def __init__(self, model_path="models/vosk-model-small-it-0.22", sample_rate=SAMPLE_RATE, silence_threshold=DEFAULT_SILENCE_THRESHOLD):
        self.sample_rate   = sample_rate
        self.model_path    = model_path
        self.silence_threshold = silence_threshold
        self.model         = None
        self.recognizer    = None
        self.audio         = None
        self.stream        = None
        self.running       = False
        self.thread        = None
        self._partial_cb   = None  # callback per risultati parziali (opzionale)

    # ------------------------------------------------------------------
    # Inizializzazione
    # ------------------------------------------------------------------

    def initialize(self):
        """
        Carica il modello Vosk e crea il riconoscitore.

        Returns:
            bool: True se l'inizializzazione è riuscita, False altrimenti.
        """
        if not os.path.exists(self.model_path):
            logger.error(f"Modello non trovato: {self.model_path}")
            return False

        try:
            # Silenzia i log interni di Vosk (molto verbosi)
            vosk.SetLogLevel(-1)

            logger.info(f"Caricamento modello: {self.model_path}")
            self.model = vosk.Model(model_path=self.model_path)

            # Abilita i risultati parziali nel riconoscitore
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)        # include confidence per parola
            self.recognizer.SetPartialWords(True) # abilita partial results

            logger.info("Modello caricato con successo")
            return True

        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione: {e}")
            return False

    # ------------------------------------------------------------------
    # Avvio / Stop
    # ------------------------------------------------------------------

    def start(self, on_result_callback=None, on_partial_callback=None, device_id=None):
        """
        Avvia il riconoscimento vocale in streaming.

        Args:
            on_result_callback:  Chiamato con il testo finale (frase completa).
            on_partial_callback: Chiamato con il testo parziale (mentre si parla).
            device_id:           ID dispositivo PyAudio (None = default).
        """
        if self.running:
            logger.warning("Riconoscimento già in corso")
            return

        self._partial_cb = on_partial_callback

        try:
            self.audio = pyaudio.PyAudio()

            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_id,
                frames_per_buffer=self.CHUNK_SIZE,
            )

            self.running = True
            self.thread  = threading.Thread(
                target=self._listen,
                args=(on_result_callback,),
                daemon=True,
            )
            self.thread.start()

            logger.info(f"Riconoscimento avviato — device={device_id}, "
                        f"chunk={self.CHUNK_SIZE}, rate={self.sample_rate}Hz")

        except Exception as e:
            logger.error(f"Errore nell'avvio: {e}")
            self.running = False

    def stop(self):
        """Ferma il riconoscimento e rilascia le risorse audio."""
        self.running = False

        if self.thread:
            self.thread.join(timeout=3)
            self.thread = None

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio:
            self.audio.terminate()
            self.audio = None

        logger.info("Riconoscimento vocale fermato")

    # ------------------------------------------------------------------
    # Loop di ascolto (thread dedicato)
    # ------------------------------------------------------------------

    def _listen(self, on_result_callback):
        """
        Legge continuamente dal microfono, applica pre-elaborazione
        e invia i campioni a Vosk.
        """
        while self.running:
            try:
                raw = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

                # ---- Pre-elaborazione audio --------------------------------
                processed = self._preprocess(raw)
                if processed is None:
                    # Frame troppo silenzioso: invia comunque audio grezzo a Vosk
                    # così il riconoscitore sa che c'è silenzio (necessario per terminare le frasi)
                    logger.debug("Frame silenzioso, invio audio grezzo")
                    processed = raw

                # ---- Invio a Vosk ------------------------------------------
                # AcceptWaveform restituisce True quando Vosk ha terminato
                # una frase (silenzio rilevato internamente dal modello).
                if self.recognizer.AcceptWaveform(processed):
                    # Risultato FINALE: frase completa
                    result = json.loads(self.recognizer.Result())
                    text   = result.get("text", "").strip()
                    if text:
                        confidence = self._avg_confidence(result)
                        logger.info(f"✔ Riconosciuto [{confidence:.0%}]: {text}")
                        if on_result_callback:
                            on_result_callback(text, confidence)
                else:
                    # Risultato PARZIALE: testo in progress
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "").strip()
                    if partial_text:
                        logger.debug(f"⏳ Parziale: {partial_text}")
                        if self._partial_cb:
                            self._partial_cb(partial_text)

            except Exception as e:
                if self.running:
                    logger.error(f"Errore durante l'ascolto: {e}")

    # ------------------------------------------------------------------
    # Pre-elaborazione audio
    # ------------------------------------------------------------------

    def _preprocess(self, raw_bytes: bytes):
        """
        Applica pre-emphasis e normalizzazione al frame audio grezzo.

        Pre-emphasis: amplifica le frequenze alte (tipiche delle consonanti)
        migliorando la distinzione tra fonemi simili (es. s/z, p/b).

        Returns:
            bytes elaborati, oppure None se il frame è considerato silenzio.
        """
        # Converti in array numpy int16
        samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)

        # Scarta frame troppo silenziosi (RMS basso)
        rms = np.sqrt(np.mean(samples ** 2))
        if rms < self.silence_threshold:
            return None

        # Pre-emphasis filter: y[n] = x[n] - alpha * x[n-1]
        emphasized = np.append(samples[0], samples[1:] - self.PRE_EMPHASIS * samples[:-1])

        # Normalizzazione: porta il picco a ~90% del range int16
        peak = np.max(np.abs(emphasized))
        if peak > 0:
            emphasized = emphasized / peak * 29000

        return emphasized.astype(np.int16).tobytes()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _avg_confidence(result: dict) -> float:
        """Calcola la confidence media dalle parole riconosciute."""
        words = result.get("result", [])
        if not words:
            return 0.0
        confs = [w.get("conf", 0.0) for w in words]
        return sum(confs) / len(confs)

    def is_running(self) -> bool:
        return self.running

    def reset(self):
        """Resetta lo stato interno del riconoscitore."""
        if self.recognizer:
            self.recognizer.Reset()
            logger.info("Riconoscitore resettato")

    @staticmethod
    def list_devices():
        """Stampa tutti i dispositivi audio disponibili (utile per debug)."""
        pa = pyaudio.PyAudio()
        print("\n── Dispositivi audio disponibili ──")
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                print(f"  [{i}] {info['name']}  "
                      f"(in={info['maxInputChannels']}, "
                      f"rate={int(info['defaultSampleRate'])}Hz)")
        pa.terminate()
        print()