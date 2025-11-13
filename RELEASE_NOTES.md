# Gestor Aules GVA v2.0.0

## 🎉 Noves Funcionalitats

### ✨ Interfície Millorada
- Icones i disseny modern
- Barres de progrés en temps real
- Missatges d'error descriptius
- Càrrega d'icones multiplataforma

### 🔄 Compatibilitat Ampliada
- Suport per a CE, RA i R als fitxers JSON
- Processament idempotent (no crea duplicats)
- Detecció automàtica d'elements existents
- Normalització automàtica de formats

### 🛠 Sistema de Compilació
- Executables independents per Linux, Windows i macOS
- Scripts d'instal·lació automàtica
- Llançador d'escriptori per Linux (.desktop)
- Gestió de dependències automatitzada

## 📊 Gestió d'Outcomes
- Creació automàtica de categories RA
- Assignació d'escales personalitzades
- Compatibilitat amb múltiples criteris d'avaluació
- Verificació en temps real dels resultats

## 📥 Instal·lació

### 🐧 Linux
```bash
# Opció 1: Executable directe
./dist/linux/GestorAulesGVA

# Opció 2: Des del codi font
python -m gestor_aules_gva

# Opció 3: Instal·lació al sistema
./install.sh
```

### 🪟 Windows
- Doble clic a GestorAulesGVA.exe

### 🍎 macOS
- Doble clic a GestorAulesGVA.app

## 🚀 Ús Ràpid
1) Inicia sessió amb les teues credencials d'Aules  
2) Selecciona el curs on vols actuar  
3) Tria l'opció:
- 📈 Importar escales des de CSV
- 📋 Llistar escales existents
- 🧾 Crear outcomes RA-CE des de JSON

## 📁 Estructura de Fitxers

### Fitxers d'Entrada
- CSV d'escales: data/example_escalas.csv
- JSON d'outcomes: data/example_outcomes.json

### Format JSON Acceptat
```json
{
  "resultados": [
    {
      "nombre": "RA1: Descripció del resultat",
      "criterios": [
        {
          "nombre": "CE1.a: Descripció del criteri",
          "peso": 25.0
        }
      ]
    }
  ]
}
```

## 🐛 Correccions
- Solucionat problema amb caràcters especials
- Millorat el maneig d'errors de connexió
- Optimitzat el temps de processament
- Correcció de càrrega d'icones en Linux

## 🔧 Requisits del Sistema

### Per a Executables
- Linux: GLIBC 2.28 o superior
- Windows: Windows 10 o superior
- macOS: macOS 10.15 o superior

### Per a Codi Font
- Python 3.8 o superior
- Pip per a gestió de dependències

## 📚 Dependències
- requests>=2.31.0 — Peticions HTTP
- beautifulsoup4>=4.12.2 — Anàlisi HTML
- lxml>=4.9.3 — Processament XML/HTML

## 🆕 Novetats Tècniques

### Compilació Multiplataforma
- Scripts automatitzats per a cada SO
- Gestió d'icones específica per sistema
- Executables auto-continguts

### Interfície Gràfica
- Temes colors corporatius GVA
- Efectes hover i feedback visual
- Log d'operacions en temps real

### Seguretat
- No emmagatzema credencials
- Connexions amb timeout
- Validació d'entrada d'usuaris

## 🤝 Contribucions
Basat en idees de:
- GestionCalificacionesAules (Martínez Peña i J. García)
- Comunitat educativa valenciana

## 📄 Llicència
Aquest projecte està sota llicència GPL-3.0. Consulta el fitxer LICENSE per a més informació.

## 🐛 Informar de Problemes
Si trobes algun problema:
- Verifica que tens la versió més recent
- Comprova la teua connexió a Internet
- Assegura't que les credencials són correctes
- Obri un issue al repositori

## 🔄 Historial de Versions
- v2.0.0: Versió estable amb interfície gràfica completa
- v1.x: Versions inicials amb funcionalitat bàsica

© 2024 jbtalens - Llicència GPL-3.0