#!/usr/bin/env python3
# =============================================================================
# Gestor Aules GVA – Punt d'entrada
# Llança la interfície gràfica per gestionar escales i outcomes (RA–CE)
# =============================================================================

import os
import sys
import tkinter as tk

def carregar_icono(root):
    """Intenta carregar l'icono des de diverses rutes"""
    # Rutes possibles per a l'icono
    rutes_prova = [
        "icons/gestor-aules.ico",
        "../icons/gestor-aules.ico",
        os.path.join(os.path.dirname(__file__), "..", "icons", "gestor-aules.ico"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons", "gestor-aules.ico")
    ]
    
    for ruta in rutes_prova:
        try:
            if os.path.exists(ruta):
                root.iconbitmap(ruta)
                print(f"✅ Icono carregat des de: {ruta}")
                return True
        except Exception as e:
            print(f"⚠️ Error carregant icono des de {ruta}: {e}")
            continue
    
    print("❌ No s'ha pogut carregar cap icono")
    return False

def main():
    """Inicia la interfície principal del Gestor Aules GVA."""
    try:
        # CANVIA AQUESTA LINIA:
        from gestor_aules_gva.gui import AulesManager  # ← ABSOLUT, NO RELATIU
        app = AulesManager()
    except ImportError as e:
        print(f"❌ Error d'importació: {e}")
        # Fallback alternatiu
        try:
            from gui import AulesManager
            app = AulesManager()
        except ImportError:
            print("❌ No s'ha pogut importar AulesManager des de cap ruta")
            raise

if __name__ == "__main__":
    main()