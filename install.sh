#!/bin/bash
echo "📦 Instal·lant Gestor Aules GVA..."

# Compilar si no existeix
if [ ! -f "dist/linux/GestorAulesGVA" ]; then
    echo "🔨 Compilant l'aplicació..."
    ./build_linux.sh
fi

# Instal·lar executable
echo "📁 Instal·lant executable..."
sudo cp dist/linux/GestorAulesGVA /usr/local/bin/gestor-aules-gva
sudo chmod +x /usr/local/bin/gestor-aules-gva

# Instal·lar icona
echo "🎨 Instal·lant icona..."
sudo cp icons/gestor-aules.png /usr/share/icons/

# Instal·lar llançador
echo "🚀 Instal·lant llançador d'escriptori..."
sudo cp GestorAulesGVA.desktop /usr/share/applications/

echo "✅ Instal·lació completada!"
echo "🔍 Cerca 'Gestor Aules GVA' al teu menú d'aplicacions"