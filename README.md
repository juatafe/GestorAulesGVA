# 🧩 Gestor Aules GVA – Escales i Outcomes

![Logo](icons/gestor-aules.png)

Eina gràfica (Tkinter + Requests + BeautifulSoup) per automatitzar la importació d’escales i la creació de Resultats/Outcomes dins dels cursos Moodle d’Aules GVA.

Permet:
- Fer login docent de manera segura.
- Importar escales des de fitxers CSV.
- Crear outcomes (criteris i resultats d’aprenentatge o competències específiques) des de fitxers JSON.
- Evitar duplicats i llistar elements existents.

---

## 🎯 Avaluació per competències i RA (Outcomes)

Volem permetre avaluar per competències específiques o per resultats d’aprenentatge (RA). En Aules aquests apareixen com a Resultats/Resultados/Outcomes. El criteri ponderat el representem com un Resultat d’Aules i l’ubiquem dins d’una categoria d’Aules que correspondrà a la competència específica o al resultat d’aprenentatge, segons si treballem a ESO/BAT o a FP.

- Al llibre de qualificacions veuràs les categories (CE/RA/Competències) com a carpetes.
- En cada tasca/activitat podràs afegir el criteri a valorar associant l’outcome corresponent.
- Per defecte s’usa una escala 0–10, però es pot utilitzar qualsevol escala de Moodle/Aules.

---

## 📦 Formats d’importació i requisits

### 1) Escales (CSV)

Format esperat: capçalera i camps
- Capçalera: name,scale,description,standard
- Separador: coma , (si tens ; assegura’t de convertir-lo abans d’importar)
- Exemple:
```csv
name,scale,description,standard
"Superado/No superado","No superado, Superado","Escala binaria en castellano",1
"No Fet/Fet","No Fet, Fet","Escala binària en valencià",1
```
Notes:
- standard: 1 per a fer-la disponible, 0 per a mantenir-la com a no estàndard.
- Pots importar un CSV amb moltes escales seguint este mateix format.

### 2) Outcomes (JSON)

Cada resultat d’aprenentatge (RA) porta un “peso” i conté criteris (CE), cadascun amb el seu “peso”. Els pesos dels criteris d’un mateix RA han de sumar 100.

Exemple:
```json
{
  "resultados": [
    {
      "nombre": "RA1: Selecciona los criterios que configuran las redes para la transmisión de voz y datos, describiendo sus principales características y funcionalidad.",
      "peso": 15,
      "criterios": [
        { "nombre": "RA1.a: ...", "peso": 17 },
        { "nombre": "RA1.b: ...", "peso": 17 },
        { "nombre": "RA1.c: ...", "peso": 17 },
        { "nombre": "RA1.d: ...", "peso": 17 },
        { "nombre": "RA1.e: ...", "peso": 16 },
        { "nombre": "RA1.f: ...", "peso": 16 }
      ]
    }
  ]
}
```

### 3) Escala obligatòria per a outcomes

Abans d’importar outcomes cal:
- Tindre triada/creada una escala al curs d’Aules.
- Indicar el nom exacte de l’escala que s’associarà als criteris (outcomes).
- Si el nom no coincideix exactament amb una escala existent, l’import no es farà per a eixos criteris.

Maneres d’indicar l’escala:
- Via interfície: selecciona l’escala en el desplegable abans d’importar outcomes.
- Via CLI: passa el paràmetre `--escala "Nom exacte de l'escala"`.
- Opcional per JSON avançat: pots afegir el camp `"escala"` a nivell de RA o de criteri per sobreescriure l’escala global.
  - Precedència: escala del criteri > escala del RA > `--escala` global > per defecte “0-10”.

Exemple amb “escala” al JSON:
```json
{
  "resultados": [
    {
      "nombre": "RA5: ...",
      "peso": 20,
      "escala": "Notes (Insuficient, Suficient, Bé, Notable, Excel·lent)",
      "criterios": [
        { "nombre": "CE5.e: ...", "peso": 14, "escala": "No realizado, Realizado" },
        { "nombre": "CE5.f: ...", "peso": 15 }
      ]
    }
  ]
}
```

---

## 👀 Visibilitat al llibre i en les tasques

- Les categories que crees (RA/Competències) apareixen al llibre de qualificacions.
- Quan crees una tasca i li assignes un resultat (criteri), aquest també apareixerà al llibre i s’usarà en el càlcul segons el seu pes i escala.
- Recomanat: utilitzar “Mitjana ponderada de les qualificacions” com a agregació en categories per aprofitar els pesos.

---

## 🚀 Ús ràpid

- Importar escales (CSV):
```bash
python3 gestor_aules_gva.py  # i tria “Importar escales”
```

- Importar outcomes (JSON) indicant l’escala:
```bash
python3 gestor_aules_gva.py  # tria “Importar outcomes”
# o CLI (si està disponible al teu script)
python3 crear_outcomes_aules.py --base-url ... --username ... --password ... --course-id ... --escala "Notes (Insuficient, Suficient, Bé, Notable, Excel·lent)"
```

---

## ℹ️ Consells

- Verifica que els pesos dels criteris de cada RA sumen 100.
- Revisa que el nom de l’escala és exactament igual al d’Aules (accents, majúscules/minúscules).
- Si l’import falla per a alguns criteris, comprova l’escala i el format del JSON/CSV.
