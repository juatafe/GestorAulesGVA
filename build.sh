#!/bin/bash
# Script de compilación principal

echo "🚀 Gestor Aules GVA - Sistema de Compilación"
echo "=============================================="

# Verificar dependencias
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

if ! pip3 show pyinstaller &> /dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

# Ejecutar compilación
echo "🔨 Iniciando compilación..."
python3 build.py $@

echo "✅ Proceso completado!"