#!/usr/bin/env python3
"""
Script per installare le dipendenze Python necessarie per l'applicazione.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Installa tutte le dipendenze da requirements.txt"""
    
    print("=" * 60)
    print("INSTALLAZIONE DIPENDENZE")
    print("=" * 60)
    
    # Verifica se requirements.txt esiste
    if not os.path.exists('requirements.txt'):
        print("ERROR: requirements.txt non trovato!")
        return False
    
    print("\nInstallazione delle dipendenze...")
    print("Questo potrebbe richiedere alcuni minuti.\n")
    
    try:
        # Installa le dipendenze
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minuti di timeout
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("DIPENDENZE INSTALLATE CON SUCCESSO!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("ERRORE NELL'INSTALLAZIONE DELLE DIPENDENZE")
            print("=" * 60)
            print("\nOutput stderr:")
            print(result.stderr)
            print("\nOutput stdout:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("\n" + "=" * 60)
        print("ERRORE: L'installazione ha superato il tempo limite!")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"\n" + "=" * 60)
        print(f"ERRORE INATTESO: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    install_dependencies()
