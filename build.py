#!/usr/bin/env python3
# =============================================================================
# build.py - Compilador universal per a Linux, Windows i macOS
# =============================================================================

import os
import sys
import shutil
import subprocess
import platform

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {descripcion}...")
    print(f"   Comando: {' '.join(comando)}")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print(f"   ✅ {descripcion} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error en {descripcion}:")
        print(f"      Salida: {e.stdout}")
        print(f"      Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"   ❌ PyInstaller no encontrado. Instala con: pip install pyinstaller")
        return False

def compilar_para_sistema(sistema):
    """Compila para un sistema operativo específico"""
    print(f"\n🎯 Compilando para {sistema}...")
    
    # Configuración específica por sistema
    if sistema == "windows":
        nombre_ejecutable = "GestorAulesGVA.exe"
        icono = "icons/gestor-aules.ico"
        args_extra = ["--console"]  # O "--windowed" para sin consola
    elif sistema == "macos":
        nombre_ejecutable = "GestorAulesGVA.app"
        icono = "icons/gestor-aules.icns"  # Necesitarías crear este archivo
        args_extra = ["--windowed"]
    else:  # linux
        nombre_ejecutable = "GestorAulesGVA"
        icono = "icons/gestor-aules.png"
        args_extra = []
    
    # Comando base de PyInstaller
    comando = [
        "pyinstaller",
        "--name", nombre_ejecutable.replace('.exe', '').replace('.app', ''),
        "--onefile",
        "--add-data", "icons:icons",
        "--add-data", "data:data",
        "--add-data", "gestor_aules_gva:gestor_aules_gva",
        "--hidden-import", "gestor_aules_gva.gui",        # ← CORREGIT
        "--hidden-import", "gestor_aules_gva.aules_api",  # ← AFEGIT
        "--collect-all", "gestor_aules_gva",
        "--icon", icono,
        "--clean",
        "--noconfirm"
    ] + args_extra + [
        "gestor_aules_gva/__main__.py"
    ]
    
    # Ejecutar compilación
    if ejecutar_comando(comando, f"Compilando {sistema}"):
        # Mover el ejecutable a la carpeta dist/
        carpeta_destino = f"dist/{sistema}"
        os.makedirs(carpeta_destino, exist_ok=True)
        
        if sistema == "windows":
            origen = f"dist/{nombre_ejecutable}"
            destino = f"{carpeta_destino}/{nombre_ejecutable}"
        elif sistema == "macos":
            origen = f"dist/{nombre_ejecutable}"
            destino = f"{carpeta_destino}/"
        else:  # linux
            origen = f"dist/{nombre_ejecutable}"
            destino = f"{carpeta_destino}/{nombre_ejecutable}"
        
        if os.path.exists(origen):
            if sistema == "macos":
                shutil.copytree(origen, destino, dirs_exist_ok=True)
            else:
                shutil.copy2(origen, destino)
            print(f"   📦 Ejecutable movido a: {destino}")
        
        return True
    return False

def main():
    """Función principal de compilación"""
    print("🚀 Iniciando compilación del Gestor Aules GVA")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("gestor_aules_gva") or not os.path.exists("icons"):
        print("❌ Error: Debes ejecutar este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Crear estructura de carpetas
    os.makedirs("dist/linux", exist_ok=True)
    os.makedirs("dist/windows", exist_ok=True)
    os.makedirs("dist/macos", exist_ok=True)
    
    # Limpiar compilaciones anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist") and not any("linux" in d or "windows" in d or "macos" in d 
                                        for d in os.listdir("dist") if os.path.isdir(os.path.join("dist", d))):
        shutil.rmtree("dist")
    
    # Determinar qué compilar
    sistema_actual = platform.system().lower()
    
    if len(sys.argv) > 1:
        objetivos = sys.argv[1:]
    else:
        objetivos = [sistema_actual]
    
    # Compilar para cada objetivo
    for objetivo in objetivos:
        if objetivo in ["linux", "windows", "macos"]:
            compilar_para_sistema(objetivo)
        else:
            print(f"❌ Objetivo no válido: {objetivo}")
    
    print(f"\n🎉 Compilación completada!")
    print("📁 Los ejecutables están en las carpetas:")
    print("   - dist/linux/   (Para Linux)")
    print("   - dist/windows/ (Para Windows)") 
    print("   - dist/macos/   (Para macOS)")

if __name__ == "__main__":
    main()