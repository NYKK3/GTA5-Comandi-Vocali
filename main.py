#!/usr/bin/env python3
"""
Applicazione principale per il riconoscimento vocale con Vosk.
Interfaccia grafica realizzata con Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import os
import json
from scripts.recognizer import VoiceRecognizer
from scripts.gta5commands import GTA5Commands


class VoiceRecognitionApp:
    """
    Applicazione GUI per il riconoscimento vocale.
    """
    
    def __init__(self, root):
        """
        Inizializza l'applicazione.
        
        Args:
            root: Finestra principale Tkinter
        """
        self.root = root
        self.root.title("GTA 5 Comandi Vocali - LSPDFR")
        self.root.geometry("600x550")
        self.root.resizable(True, True)
        
        # Inizializza il riconoscitore e il gestore comandi (dopo load_settings per avere http_port)
        self.recognizer = VoiceRecognizer()
        # I comandi verranno inizializzati dopo il caricamento delle impostazioni
        self.commands = None
        self.is_recognizing = False
        self.microphones = []
        self.selected_microphone = None
        
        # Modelli disponibili
        self.available_models = [
            {"name": "Small (48 MB)", "path": "models/vosk-model-small-it-0.22"},
            {"name": "Medium (1.2 GB)", "path": "models/vosk-model-it-0.22"}
        ]
        self.selected_model = None
        
        # Soglia di silenzio (valore di default: 50)
        self.silence_threshold = 50
        
        # Porta HTTP per i comandi GTA5 (valore di default: 51250)
        self.http_port = 51250
        
        # Percorso del file delle impostazioni
        self.settings_file = "settings.json"
        
        # Configura lo stile
        self.setup_styles()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Carica le impostazioni salvate
        self.load_settings()
        
        # Inizializza i comandi con la porta HTTP caricata
        self.commands = GTA5Commands(http_port=self.http_port)
        
        # Carica i modelli e i microfoni disponibili
        self.load_models()
        self.load_microphones()
        
        # Gestisce la chiusura della finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_styles(self):
        """Configura gli stili per l'interfaccia."""
        self.style = ttk.Style()
        
        # Configura i colori
        self.style.configure("Active.TButton", foreground="white", background="#2ecc71")
        self.style.configure("Inactive.TButton", foreground="white", background="#e74c3c")
    
    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia."""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(
            main_frame,
            text="Riconoscimento Vocale",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame per la selezione del modello
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(pady=5, fill=tk.X)
        
        # Label per il modello
        model_label = ttk.Label(
            model_frame,
            text="Modello:",
            font=("Arial", 11)
        )
        model_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Menu a tendina per selezionare il modello
        self.model_combo = ttk.Combobox(
            model_frame,
            state="readonly",
            width=40
        )
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)
        
        # Frame per la selezione del microfono
        mic_frame = ttk.Frame(main_frame)
        mic_frame.pack(pady=5, fill=tk.X)
        
        # Label per il microfono
        mic_label = ttk.Label(
            mic_frame,
            text="Microfono:",
            font=("Arial", 11)
        )
        mic_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Menu a tendina per selezionare il microfono
        self.microphone_combo = ttk.Combobox(
            mic_frame,
            state="readonly",
            width=40
        )
        self.microphone_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.microphone_combo.bind("<<ComboboxSelected>>", self.on_microphone_selected)
        
        # Frame per il pulsante di controllo
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        # Pulsante ON/OFF
        self.toggle_button = ttk.Button(
            control_frame,
            text="ACCENDI",
            command=self.toggle_recognition,
            width=20
        )
        self.toggle_button.pack()
        
        # Frame per lo stato
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(pady=10, fill=tk.X)
        
        # Label di stato
        self.status_label = ttk.Label(
            status_frame,
            text="Stato: Inattivo",
            font=("Arial", 12)
        )
        self.status_label.pack()
        
        # Frame per la soglia di silenzio
        threshold_frame = ttk.Frame(main_frame)
        threshold_frame.pack(pady=5, fill=tk.X)
        
        # Label per la soglia di silenzio
        threshold_label = ttk.Label(
            threshold_frame,
            text="Soglia Silenzio:",
            font=("Arial", 11)
        )
        threshold_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Slider per la soglia di silenzio
        self.threshold_scale = ttk.Scale(
            threshold_frame,
            from_=10,
            to=200,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.threshold_scale.set(self.silence_threshold)
        self.threshold_scale.bind('<ButtonRelease>', self.on_threshold_changed)
        
        # Label per visualizzare il valore della soglia
        self.threshold_value_label = ttk.Label(
            threshold_frame,
            text=f" {self.silence_threshold}",
            font=("Arial", 11)
        )
        self.threshold_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame per la porta HTTP
        port_frame = ttk.Frame(main_frame)
        port_frame.pack(pady=5, fill=tk.X)
        
        # Label per la porta HTTP
        port_label = ttk.Label(
            port_frame,
            text="Porta HTTP:",
            font=("Arial", 11)
        )
        port_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry per la porta HTTP
        self.port_entry = ttk.Entry(
            port_frame,
            width=15,
            font=("Arial", 11)
        )
        self.port_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.port_entry.insert(0, str(self.http_port))
        self.port_entry.bind('<Return>', self.on_port_changed)
        
        # Label per visualizzare il valore della porta
        self.port_value_label = ttk.Label(
            port_frame,
            text=f" (default: 51250)",
            font=("Arial", 11)
        )
        self.port_value_label.pack(side=tk.LEFT, padx=(0, 0))
        
        # Frame per il testo riconosciuto
        text_frame = ttk.LabelFrame(main_frame, text="Testo Riconosciuto", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text area per il testo riconosciuto
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.text_area, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=(scrollbar.set,))
        
        # Frame per i pulsanti di azione
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=10)
        
        # Pulsante Cancella
        clear_button = ttk.Button(
            action_frame,
            text="Cancella",
            command=self.clear_text,
            width=15
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsante Copia
        copy_button = ttk.Button(
            action_frame,
            text="Copia",
            command=self.copy_text,
            width=15
        )
        copy_button.pack(side=tk.LEFT, padx=5)
    
    def toggle_recognition(self):
        """Attiva o disattiva il riconoscimento vocale."""
        if self.is_recognizing:
            self.stop_recognition()
        else:
            self.start_recognition()
    
    def start_recognition(self):
        """Avvia il riconoscimento vocale."""
        # Controlla se il modello selezionato è installato
        if not self.selected_model:
            messagebox.showerror("Errore", "Seleziona un modello vocale!")
            return
        
        model_path = self.selected_model["path"]
        if not os.path.exists(model_path):
            model_name = self.selected_model["name"]
            messagebox.showerror(
                "Errore", 
                f"Modello {model_name} non trovato!\n\n"
                f"Esegui install_all.bat e scegli l'opzione per installare il modello {model_name.lower()}."
            )
            return
        
        # Imposta il percorso del modello nel riconoscitore
        self.recognizer.model_path = model_path
        
        # Inizializza il riconoscitore
        if not self.recognizer.initialize():
            messagebox.showerror("Errore", "Impossibile inizializzare il modello vocale!")
            return
        
        # Avvia il riconoscimento con il microfono selezionato
        self.recognizer.start(
            on_result_callback=self.on_recognition_result,
            on_partial_callback=self.on_partial_result,
            device_id=self.selected_microphone
        )
        self.is_recognizing = True
        
        # Aggiorna l'interfaccia
        self.toggle_button.config(text="SPEGNI")
        self.status_label.config(text="Stato: In ascolto...", foreground="green")
        self.text_area.insert(tk.END, "[Riconoscimento avviato...]\n")
    
    def stop_recognition(self):
        """Ferma il riconoscimento vocale."""
        self.recognizer.stop()
        self.is_recognizing = False
        
        # Aggiorna l'interfaccia
        self.toggle_button.config(text="ACCENDI")
        self.status_label.config(text="Stato: Inattivo", foreground="black")
        self.text_area.insert(tk.END, "[Riconoscimento fermato]\n")
    
    def on_recognition_result(self, text, confidence=0):
        """
        Callback chiamata quando c'è un risultato finale dal riconoscimento.
        
        Args:
            text: Testo riconosciuto
            confidence: Livello di confidenza (0-1)
        """
        # Processa il comando GTA5
        self.commands.process_command(text)
        
        # Aggiorna l'interfaccia nella thread principale
        self.root.after(0, lambda: self.update_text_area(f"[CONFIDENZA {confidence:.0%}] {text}\n"))
    
    def on_partial_result(self, text):
        """
        Callback chiamata quando c'è un risultato parziale (mentre si parla).
        
        Args:
            text: Testo parziale riconosciuto
        """
        # Aggiorna l'interfaccia nella thread principale
        self.root.after(0, lambda: self.update_text_area(f"(parziale: {text}) ", clear_previous_partial=True))
    
    def update_text_area(self, text, clear_previous_partial=False):
        """Aggiorna l'area di testo con il nuovo risultato."""
        if text:
            if clear_previous_partial:
                # Cancella l'ultima riga (il parziale precedente)
                current_text = self.text_area.get(1.0, tk.END)
                if "\n" in current_text:
                    last_newline = current_text.rfind("\n")
                    self.text_area.delete(f"{last_newline + 1}.0", tk.END)
            self.text_area.insert(tk.END, text)
            self.text_area.see(tk.END)
    
    def clear_text(self):
        """Cancella il testo dall'area di testo."""
        self.text_area.delete(1.0, tk.END)
    
    def copy_text(self):
        """Copia il testo nell'area di trasferimento."""
        text = self.text_area.get(1.0, tk.END)
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
    
    def on_model_selected(self, event):
        """Gestisce la selezione del modello."""
        self.selected_model = self.available_models[self.model_combo.current()]
        print(f"Modello selezionato: {self.model_combo.get()}")
        # Salva le impostazioni immediatamente
        self.save_settings()
    
    def on_threshold_changed(self, event=None):
        """Gestisce la modifica della soglia di silenzio."""
        self.silence_threshold = int(self.threshold_scale.get())
        self.threshold_value_label.config(text=f" {self.silence_threshold}")
        # Aggiorna il riconoscitore con il nuovo valore
        self.recognizer.silence_threshold = self.silence_threshold
        print(f"Soglia silenzio modificata: {self.silence_threshold}")
        # Salva le impostazioni immediatamente
        self.save_settings()
    
    def on_port_changed(self, event=None):
        """Gestisce la modifica della porta HTTP."""
        try:
            new_port = int(self.port_entry.get())
            if 1 <= new_port <= 65535:
                self.http_port = new_port
                print(f"Porta HTTP modificata: {self.http_port}")
                # Salva le impostazioni immediatamente
                self.save_settings()
            else:
                print("Porta non valida (deve essere tra 1 e 65535)")
        except ValueError:
            print("Inserisci un numero valido per la porta")
    
    def on_microphone_selected(self, event):
        """Gestisce la selezione del microfono."""
        self.selected_microphone = self.microphone_combo.current()
        print(f"Microfono selezionato: {self.microphone_combo.get()}")
        # Salva le impostazioni immediatamente
        self.save_settings()
    
    def load_models(self):
        """Carica l'elenco dei modelli disponibili."""
        # Popola il menu a tendina con i modelli
        self.model_combo['values'] = [model["name"] for model in self.available_models]
        
        # Se abbiamo un indice salvato, usalo, altrimenti usa il primo modello disponibile
        if hasattr(self, 'selected_model_index') and self.selected_model_index is not None:
            if 0 <= self.selected_model_index < len(self.available_models):
                self.model_combo.current(self.selected_model_index)
                self.selected_model = self.available_models[self.selected_model_index]
                print(f"Modello selezionato dalle impostazioni: {self.selected_model['name']}")
                return
        
        # Seleziona il primo modello disponibile
        for model in self.available_models:
            if os.path.exists(model["path"]):
                index = self.available_models.index(model)
                self.model_combo.current(index)
                self.selected_model = model
                print(f"Modello selezionato: {model['name']}")
                return
        
        # Se nessun modello è installato, seleziona il primo
        if self.available_models:
            self.model_combo.current(0)
            self.selected_model = self.available_models[0]
            print("Nessun modello installato, seleziona Small di default")
    
 
    
    def on_close(self):
        """Gestisce la chiusura dell'applicazione."""
        if self.is_recognizing:
            self.stop_recognition()
        self.save_settings()
        self.root.destroy()
    
    def load_settings(self):
        """Carica le impostazioni dal file settings.json."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                print(f"Contenuto settings: {settings}")
                
                # Carica il modello selezionato (dopo che load_models() è stato chiamato)
                if "model_index" in settings:
                    model_index = settings["model_index"]
                    # Salva l'indice del modello per applicarlo dopo il caricamento dei modelli
                    self.selected_model_index = model_index
                    print(f"Indice modello salvato: {model_index}")
                
                # Carica il microfono selezionato (indice PyAudio)
                if "microphone_index" in settings:
                    mic_index = settings["microphone_index"]
                    # L'indice del microfono verrà applicato dopo il caricamento dei microfoni
                    self.selected_microphone_index = mic_index
                    print(f"Indice microfono PyAudio salvato: {mic_index}")
                else:
                    print("Nessun microphone_index trovato nelle impostazioni")
                
                # Carica la soglia di silenzio
                if "silence_threshold" in settings:
                    self.silence_threshold = settings["silence_threshold"]
                    print(f"Soglia silenzio salvata: {self.silence_threshold}")
                    # Aggiorna lo slider e la label con il valore caricato
                    if hasattr(self, 'threshold_scale'):
                        self.threshold_scale.set(self.silence_threshold)
                        self.threshold_value_label.config(text=f" {self.silence_threshold}")
                else:
                    print("Nessuna silence_threshold trovata nelle impostazioni, uso default: 50")
                
                # Carica la porta HTTP
                if "http_port" in settings:
                    self.http_port = settings["http_port"]
                    print(f"Porta HTTP salvata: {self.http_port}")
                    # Aggiorna l'entry con il valore caricato
                    if hasattr(self, 'port_entry'):
                        self.port_entry.delete(0, tk.END)
                        self.port_entry.insert(0, str(self.http_port))
                else:
                    print("Nessuna http_port trovata nelle impostazioni, uso default: 51250")
                
                print("Impostazioni caricate con successo!")
            except Exception as e:
                import traceback
                print(f"Errore nel caricamento delle impostazioni: {e}")
                traceback.print_exc()
        else:
            print("Nessun file di impostazioni trovato, uso valori predefiniti")
    
    def save_settings(self):
        """Salva le impostazioni nel file settings.json."""
        try:
            settings = {}
            
            # Salva l'indice del modello selezionato
            if hasattr(self, 'model_combo'):
                model_index = self.model_combo.current()
                if model_index >= 0:
                    settings["model_index"] = model_index
            
            # Salva l'indice PyAudio del microfono selezionato
            if hasattr(self, 'microphone_combo') and hasattr(self, 'selected_microphone'):
                mic_index = self.microphone_combo.current()
                if mic_index >= 0 and self.selected_microphone is not None:
                    # Salva l'indice PyAudio del dispositivo, non l'indice della lista
                    settings["microphone_index"] = self.selected_microphone
                    print(f"Salvo microphone_index (PyAudio): {self.selected_microphone}")
            
            # Salva la soglia di silenzio
            if hasattr(self, 'silence_threshold'):
                settings["silence_threshold"] = self.silence_threshold
                print(f"Salvo silence_threshold: {self.silence_threshold}")
            
            # Salva la porta HTTP
            if hasattr(self, 'http_port'):
                settings["http_port"] = self.http_port
                print(f"Salvo http_port: {self.http_port}")
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            print("Impostazioni salvate con successo!")
        except Exception as e:
            print(f"Errore nel salvataggio delle impostazioni: {e}")
    
    def load_microphones(self):
        """Carica l'elenco dei microfoni disponibili."""
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            self.microphones = []
            
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    self.microphones.append({
                        'index': i,
                        'name': device_info['name']
                    })
            
            audio.terminate()
            
            # Popola il menu a tendina
            self.microphone_combo['values'] = [mic['name'] for mic in self.microphones]
            if self.microphones:
                print(f"Microfoni trovati: {len(self.microphones)}")
                for mic in self.microphones:
                    print(f"  - {mic['name']} (index PyAudio: {mic['index']})")
                
                # Se abbiamo un indice PyAudio salvato, cerca il microfono corrispondente
                if hasattr(self, 'selected_microphone_index') and self.selected_microphone_index is not None:
                    print(f"Tento di caricare microfono con indice PyAudio: {self.selected_microphone_index}")
                    # Cerca il microfono con l'indice PyAudio salvato
                    found_index = -1
                    for i, mic in enumerate(self.microphones):
                        if mic['index'] == self.selected_microphone_index:
                            found_index = i
                            break
                    
                    if found_index >= 0:
                        # Microfono trovato, selezionalo
                        self.microphone_combo.current(found_index)
                        self.selected_microphone = self.microphones[found_index]['index']
                        print(f"Microfono selezionato dalle impostazioni: {self.microphones[found_index]['name']}")
                    else:
                        # Microfono non più disponibile, usa il primo
                        print(f"Microfono con indice PyAudio {self.selected_microphone_index} non trovato, uso il primo disponibile")
                        self.microphone_combo.current(0)
                        self.selected_microphone = self.microphones[0]['index']
                else:
                    print("Nessun indice microfono PyAudio salvato trovato")
                    self.microphone_combo.current(0)
                    self.selected_microphone = self.microphones[0]['index']
        except Exception as e:
            print(f"Errore nel caricamento dei microfoni: {e}")


def main():
    """Funzione principale."""
    # Crea la finestra principale
    root = tk.Tk()
    
    # Imposta l'icona della finestra (opzionale)
    try:
        root.iconbitmap(default="icon.ico")
    except:
        pass
    
    # Crea l'applicazione
    app = VoiceRecognitionApp(root)
    
    # Avvia il loop principale
    root.mainloop()


if __name__ == "__main__":
    main()
