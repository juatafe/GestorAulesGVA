# Gestor Aules GVA – Escales i Outcomes

![Logo](icons/gestor-aules.png)

En aquest repositori trobaràs el Gestor Aules GVA, una eina gràfica que facilita la importació massiva de resultats d’aprenentatge i criteris als cursos Moodle d’Aules GVA —o a qualsevol altra plataforma basada en Moodle.A Aules GVA, els outcomes són la manera d’avaluar competències específiques o resultats d’aprenentatge (RA). Com que el sistema de competències nadiu de Moodle és un altre món i els administradors el tenen desactivat, fem servir els "resultats" (outcomes) amb este propòsit.

El plantejament és senzill: convertim els resultats d’Aules en criteris específics i els fiquem dins de categories que representen les Competències Específiques (CE) o els Resultats d’Aprenentatge (RA). D’esta manera, podem avaluar igual de bé tant per competències específiques (ESO/BAT) com per RA (FP).

## 📚 Com funciona??

Has de tindre a mà la web del Moodle/Aules, l’ID del curs, el teu usuari i contrasenya, i els teus RA o CE en un fitxer JSON.
![Id curs](imatges/id_curs.png)
![Login](imatges/accedir.png)
 L’eina els importarà a Aules automàticament, crearà les categories que calen i assignarà els criteris amb els seus pesos corresponents.


També necessites una escala d’avaluació. Aquesta cal crear-la prèviament de manera manual, perquè per a crear escales a nivell global s’ha de ser administrador (i, almenys a mi, Aules no m’ha deixat fer-ho automàticament). Si utilitzes un Moodle diferent, l’eina també pot importar escales des de fitxers CSV sempre que tingues permisos d’administració.

![Escales](imatges/escales.png)
![afigura escala](imatges/afigEscalanova.png)
![crea escala](imatges/esalanova.png)

> Recorda que les escales són globals per a tot el Moodle/Aules —excepte les que crees manualment dins d’un curs, que només s’apliquen allí. Per això és important identificar amb exactitud quina escala vols utilitzar abans d’importar els outcomes. 



L’app comprova si els RA o CE ja existeixen i no els duplica. També revisa que els pesos dels criteris dins de cada RA sumen 100%, i crea automàticament les categories per a cada resultat. Tingues present que el que importes realment són els criteris dins de cada RA o CE, no els RA o CE en si mateixos.
![llibre abans](imatges/llibre.png)
![connexió](imatges/connexion.png)
![importa](imatges/importaroutcomes.png)

Una volta importat tot, al llibre de qualificacions veuràs les categories, i conforme vages creant tasques i assignant-los criteris, aquests apareixeran automàticament al llibre i s’utilitzaran per a calcular les notes segons el seu pes i escala. Això et permet avaluar per competències específiques o per RA d’una manera molt més coherent i senzilla.

![categories](imatges/categories.png)
![tasca](imatges/tasca.png)
![tasquesras](imatges/tascquesras.png)

## 🚩 Característiques Principals

Permet:
- Fer login docent de manera segura.
- Importar escales des de fitxers CSV.
- Crear outcomes (criteris i resultats d’aprenentatge o competències específiques) des de fitxers JSON.
- Evitar duplicats i llistar elements existents.

---

## 🎯 Avaluació per competències i RA (Outcomes)

Volem permetre avaluar per competències específiques o per resultats d’aprenentatge (RA). En Aules aquests apareixen com a `Resultats/Resultados/Outcomes`. Cada criteri ponderat es representa com un resultat d’Aules, i es col·loca dins d’una categoria que correspon a la competència específica o al RA, segons treballem a ESO/BAT o FP.

- Al llibre de qualificacions veuràs les categories (CE/RA/Competències) com a carpetes.
- En cada tasca/activitat podràs afegir el criteri a valorar associant l’outcome corresponent.
- La tasca pot tenir la seua pròpia nota, escala o rúbrica, però l’outcome s’utilitzarà per al càlcul global segons el seu pes i escala de forma independent. 
- Per defecte et demana una escala 0–10, però es pot utilitzar qualsevol escala de Moodle/Aules.

> Un bon plugin per a Moodle seria poder assignar directament els criteris d’una rúbrica als outcomes, però això ja és una altra guerra i mereixeria una eina pròpia.
>  De moment, la rúbrica i els criteris poden conviure perfectament en una mateixa tasca: tu valores amb la rúbrica i, a banda, assignes manualment la nota del criteri (outcome). Això permet que l’alumne tinga una nota per a la tasca i una altra per al criteri, cadascuna amb el seu sentit.
> La nota que deuria comptar al llibre de qualificacions serà la del criteri, ponderada segons el seu pes, i no la de la tasca. Això és així perquè no es poden ponderar instruments d’avaluació, ja que aniria en contra del que marca la LOMLOE sobre ponderació dels criteris.
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

## ℹ️ Consells

- Verifica que els pesos dels criteris de cada RA sumen 100.
- Revisa que el nom de l’escala és exactament igual al d’Aules (accents, majúscules/minúscules).
- Si l’import falla per a alguns criteris, comprova l’escala i el format del JSON/CSV.

---
