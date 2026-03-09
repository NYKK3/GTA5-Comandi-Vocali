#!/usr/bin/env python3
"""
Modulo per gestire i comandi vocali per GTA5.
Riceve le parole complete dal riconoscitore e le esegue.
"""

import json
import logging
import os
import http.client
import json as json_lib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GTA5Commands:
    """
    Classe per gestire i comandi vocali per GTA5.
    """
    
    # URL del server HTTP per inviare i comandi
    HTTP_SERVER_URL = "127.0.0.1"
    DEFAULT_HTTP_SERVER_PORT = 51250
    
    def __init__(self, http_port=DEFAULT_HTTP_SERVER_PORT):
        """Inizializza il gestore dei comandi caricando da commands.json."""
        self.commands = {}
        self.http_port = http_port
        self._load_commands()
    
    def process_command(self, text):
        """
        Processa un comando vocale riconosciuto.
        
        Args:
            text: Testo completo riconosciuto (non parziale)
            
        Returns:
            bool: True se il comando è stato riconosciuto ed eseguito, False altrimenti
        """
        # Normalizza il testo (minuscolo, senza punteggiatura e simboli)
        normalized_text = text.lower().strip()
        # Sostituisci tutti i simboli non alfanumerici con uno spazio
        import re
        normalized_text = re.sub(r'[^\w\s]', ' ', normalized_text)
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        
        logger.info(f"Comando ricevuto: '{normalized_text}'")
        
        # Cerca il comando nella lista
        for command, cmd_data in self.commands.items():
            # Ottieni tutte le phrase per questo comando
            phrases = cmd_data.get("phrases", [command])
            
            # Controlla ogni phrase
            for phrase in phrases:
                # Splitta la phrase in parole
                command_words = phrase.split()
                text_words = normalized_text.split()
                
                # Controlla se tutte le parole della phrase sono presenti nel testo (in ordine)
                if self._words_in_text(command_words, text_words):
                    # Se ci sono parole chiave, controlla che almeno una sia presente
                    keywords = cmd_data.get("keywords", "")
                    if keywords:
                        keyword_list = [kw.strip() for kw in keywords.split(",")]
                        has_keyword = any(kw in normalized_text for kw in keyword_list)
                        if not has_keyword:
                            continue  # Salta questo comando se non ha le parole chiave
                    
                    logger.info(f"Esecuzione comando: {phrase}")
                    cmd_data["handler"]()
                    return True
        
        logger.debug(f"Nessun comando riconosciuto in: '{normalized_text}'")
        return False
    
    def _words_in_text(self, command_words, text_words):
        """
        Controlla se tutte le parole del comando sono presenti nel testo in ordine.
        Permette parole extra tra le parole del comando e parole parziali (es. "inviare" per "invia").
        
        Args:
            command_words: Lista di parole del comando
            text_words: Lista di parole del testo riconosciuto
            
        Returns:
            bool: True se tutte le parole del comando sono presenti in ordine
        """
        if not command_words:
            return False
        
        text_idx = 0
        cmd_idx = 0
        
        while text_idx < len(text_words) and cmd_idx < len(command_words):
            # Controlla se la parola corrisponde esattamente o inizia con la parola del comando
            if (text_words[text_idx] == command_words[cmd_idx] or 
                text_words[text_idx].startswith(command_words[cmd_idx])):
                cmd_idx += 1
            text_idx += 1
        
        return cmd_idx == len(command_words)
    
    def _load_commands(self):
        """Carica i comandi dal file commands.json."""
        # Trova il file commands.json nella root del progetto
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        commands_file = os.path.join(project_root, "commands.json")
        
        try:
            with open(commands_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for cmd in data.get("commands", []):
                    phrases = cmd.get("phrases", "")
                    action = cmd["action"]
                    description = cmd.get("description", "")
                    keywords = cmd.get("keywords", "")
                    
                    # Se non ci sono phrases, usa la vecchia chiave "phrase" per compatibilità
                    if not phrases:
                        phrases = cmd.get("phrase", "")
                    
                    # Splitta le phrases separate da virgole
                    phrase_list = [p.strip() for p in phrases.split(",") if p.strip()]
                    
                    if not phrase_list:
                        logger.warning(f"Comando senza phrases: {cmd}")
                        continue
                    
                    # Usa la prima phrase come chiave principale
                    main_phrase = phrase_list[0]
                    
                    # Crea un handler dinamico che invia l'azione al server HTTP
                    def make_handler(action_name):
                        return lambda: self._send_http_command(action_name)
                    
                    # Crea il mapping frase -> handler
                    self.commands[main_phrase] = {
                        "phrases": phrase_list,
                        "action": action,
                        "description": description,
                        "keywords": keywords,
                        "handler": make_handler(action)
                    }
                
                logger.info(f"Comandi caricati: {len(self.commands)}")
                
        except FileNotFoundError:
            logger.error("File commands.json non trovato!")
            self.commands = {}
        except json.JSONDecodeError:
            logger.error("Errore nel parsing di commands.json!")
            self.commands = {}
        except Exception as e:
            logger.error(f"Errore nel caricamento dei comandi: {e}")
            self.commands = {}
    
    def _send_http_command(self, action):
        """Invia il comando al server HTTP."""
        try:
            conn = http.client.HTTPConnection(self.HTTP_SERVER_URL, self.http_port, timeout=5)
            headers = {'Content-Type': 'text/plain'}
            conn.request('POST', '/', action, headers)
            response = conn.getresponse()
            conn.close()
            logger.info(f"✔ Comando inviato: {action} (HTTP {response.status})")
        except Exception as e:
            logger.error(f"Errore nell'invio del comando: {e}")


# Esempio di utilizzo
if __name__ == "__main__":
    # Crea un'istanza del gestore comandi
    commands = GTA5Commands()
    
    print("Comandi caricati:")
    for phrase, data in commands.commands.items():
        phrases = data.get('phrases', [phrase])
        print(f"  - {', '.join(phrases)} -> {data['action']}")
    
    # Test con alcuni comandi
    test_commands = [
        "invia ambulanza",
        "chiama ambulanza",
        "ambulanza",
        "invia polizia",
        "fermati",
        "stop",
        "comando sconosciuto"
    ]
    
    print("\nTest comandi:")
    for cmd in test_commands:
        result = commands.process_command(cmd)
        print(f"Comando '{cmd}': {'Eseguito' if result else 'Non riconosciuto'}")