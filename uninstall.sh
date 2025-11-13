#!/bin/bash
echo "🗑 Desinstal·lant Gestor Aules GVA..."

# Eliminar executable
sudo rm -f /usr/local/bin/gestor-aules-gva

# Eliminar icona
sudo rm -f /usr/share/icons/gestor-aules.png

# Eliminar llançador
sudo rm -f /usr/share/applications/GestorAulesGVA.desktop

echo "✅ Desinstal·lació completada!"