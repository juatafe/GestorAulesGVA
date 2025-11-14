# gestor_aules_gva/aules_api.py
from tkinter import messagebox
import requests, re, csv, json, time
from bs4 import BeautifulSoup
import tkinter as tk
import unicodedata

# === LOGIN ===================================================
def login(session, base_url, username, password, output=None):
    try:
        if output:
            output.insert(tk.END, "➡️ Iniciant sessió a Aules...\n")
        r = session.get(f"{base_url}/login/index.php", timeout=15)
        token = re.search(r'name="logintoken" value="(\w{32})"', r.text)
        if not token:
            output.insert(tk.END, "❌ No s’ha trobat logintoken.\n", "error")
            return None, None

        payload = {"username": username, "password": password, "logintoken": token.group(1)}
        r = session.post(f"{base_url}/login/index.php", data=payload, timeout=15)
        sesskey = re.search(r"sesskey=(\w+)", r.text)
        if not sesskey:
            output.insert(tk.END, "❌ Error d’autenticació. Revisa usuari/contrasenya.\n", "error")
            return None, None

        output.insert(tk.END, f"✅ Sessió iniciada (sesskey={sesskey.group(1)})\n")
        return session.cookies.get_dict(), sesskey.group(1)
    except Exception as e:
        if output:
            output.insert(tk.END, f"❌ Error de connexió: {e}\n", "error")
        return None, None


# === OBTINDRE ESCALES EXISTENTS ==============================
def obtenir_escalas_existents(session, cookie, base_url, course_id, output=None):
    escalas = {}
    try:
        if output: output.insert(tk.END, "🔍 Obtenint escales existents...\n")
        url = f"{base_url}/grade/edit/scale/index.php?id={course_id}"
        r = session.get(url, cookies=cookie, timeout=15)
        if r.status_code != 200:
            output.insert(tk.END, f"⚠️ Error HTTP {r.status_code}\n", "warning")
            return escalas
        soup = BeautifulSoup(r.text, "html.parser")
        for fila in soup.select("table.generaltable tr"):
            celdas = fila.find_all("td")
            if not celdas: continue
            nom = celdas[0].get_text(strip=True)
            link = fila.find("a", href=re.compile(r"edit\.php\?courseid=\d+&id=\d+"))
            if link:
                m = re.search(r"&id=(\d+)", link["href"])
                if m:
                    escalas[nom] = m.group(1)
                    if output: output.insert(tk.END, f"  - {nom} (ID {m.group(1)})\n")
        if output: output.insert(tk.END, f"✅ Total escales trobades: {len(escalas)}\n")
    except Exception as e:
        if output: output.insert(tk.END, f"❌ Error: {e}\n", "error")
    return escalas


# === IMPORTAR ESCALES DES DE CSV =============================
def importar_escalas_des_de_csv(session, cookie, base_url, sesskey, course_id, fitxer_csv, output):
    try:
        output.insert(tk.END, f"📥 Important escales des de: {fitxer_csv}\n")
        with open(fitxer_csv, 'r', encoding='utf-8', errors='replace') as ftest:
            primera = ftest.readline()
            delimiter = ';' if ';' in primera and ',' not in primera else ','
        with open(fitxer_csv, newline='', encoding='utf-8', errors='replace') as f:
            lector = csv.DictReader(f, delimiter=delimiter)
            total = 0
            for fila in lector:
                nom = fila.get('Nom') or fila.get('name')
                valors = fila.get('Valors') or fila.get('scale')
                descripcio = fila.get('Descripció') or fila.get('description')
                if not nom or not valors:
                    output.insert(tk.END, f"⚠️ Fila incompleta: {fila}\n", "warning")
                    continue
                form = {
                    'id': 0, 'courseid': course_id, 'sesskey': sesskey,
                    '_qf__edit_scale_form': 1,
                    'name': nom.strip(),
                    'scale': valors.strip(),
                    'description[text]': (descripcio or '').strip(),
                    'description[format]': 1,
                    'standard': 1,
                    'submitbutton': 'Guardar canvis'
                }
                r = session.post(f"{base_url}/grade/edit/scale/edit.php", cookies=cookie, data=form, timeout=15)
                if any(w in r.text.lower() for w in ['guardat', 'saved', 'creat', 'created']):
                    output.insert(tk.END, f"✅ Escala '{nom}' creada.\n")
                else:
                    time.sleep(1)
                    check = session.get(f"{base_url}/grade/edit/scale/index.php?id={course_id}", cookies=cookie, timeout=15)
                    if nom.lower() in check.text.lower():
                        output.insert(tk.END, f"ℹ️ Escala '{nom}' detectada després del reintent.\n")
                    else:
                        output.insert(tk.END, f"⚠️ No s’ha pogut verificar '{nom}'.\n", "warning")
                total += 1
        output.insert(tk.END, f"\n📊 Escales processades: {total}\n")
    except Exception as e:
        output.insert(tk.END, f"❌ Error durant la importació: {e}\n", "error")



def fix_text(s):
    """Normalitza caràcters rars que trenquen Tkinter."""
    return unicodedata.normalize("NFKC", s)


def validar_pesos_ra(ra_data, output):
    """Valida que els pesos dels criteris sumin 100%"""
    errors = []
    for ra in ra_data.get("resultados", []):
        ra_nom = ra["nombre"]
        criterios = ra.get("criterios", [])
        suma_pesos = sum(c.get("peso", 0) for c in criterios)
        
        if suma_pesos != 100:
            errors.append(f"❌ RA '{ra_nom}': Els pesos sumen {suma_pesos}% (haurien de sumar 100%)")
    
    for error in errors:
        output.insert(tk.END, f"{error}\n", "error")
    
    return len(errors) == 0

def obtenir_outcomes_existents(session, cookie, base_url, course_id, output=None):
    """Retorna els shortnames dels outcomes existents"""
    outcomes = set()
    try:
        url = f"{base_url}/grade/edit/outcome/index.php?id={course_id}"
        r = session.get(url, cookies=cookie)
        soup = BeautifulSoup(r.text, "html.parser")
        
        for fila in soup.select("table.generaltable tr"):
            celdas = fila.find_all("td")
            if len(celdas) > 1:
                shortname = celdas[0].get_text(strip=True)
                if shortname:
                    outcomes.add(shortname.lower())
        
        if output:
            output.insert(tk.END, f"📊 Outcomes existents: {len(outcomes)}\n")
    except Exception as e:
        if output:
            output.insert(tk.END, f"⚠️ Error obtenint outcomes: {e}\n")
    
    return outcomes
# -------------------------------------------------------------
# CREAR CATEGORIA RA
# -------------------------------------------------------------
def crear_categoria_ra(session, cookie, base_url, sesskey, course_id, nom, output):
    output.insert(tk.END, f"➕ Creant categoria RA: {nom}\n")
    form = {
        "courseid": course_id,
        "sesskey": sesskey,
        "_qf__edit_category_form": 1,
        "fullname": nom,
        "aggregation": 10,  # Mitjana ponderada
        "aggregateonlygraded": 1,
        "keephigh": 0,
        "droplow": 0,
        "hidden": 0,
        "submitbutton": "Guardar canvis"
    }
    r = session.post(f"{base_url}/grade/edit/tree/category.php", cookies=cookie, data=form)
    if r.status_code == 200:
        output.insert(tk.END, f"✅ Categoria '{nom}' creada correctament.\n")
        return True
    else:
        output.insert(tk.END, f"⚠️ Error en crear la categoria '{nom}' ({r.status_code})\n")
        return False
# -------------------------------------------------------------
# CREAR OUTCOME CE AMB CALLBACK
# -------------------------------------------------------------
def crear_outcome(
    session, cookie, base_url, sesskey, course_id,
    shortname, fullname, scaleid,
    output, categoryid=None, progress_callback=None
):
    try:
        # FULLNAME = criteri complet (RA1.b) Se han...)
        # DESCRIPTION = exactament igual
        form = {
            'id': 0,
            'courseid': course_id,
            'sesskey': sesskey,
            '_qf__edit_outcome_form': 1,
            'fullname': fix_text(fullname),
            'shortname': fix_text(shortname),
            'scaleid': scaleid,
            'description[text]': fix_text(fullname),
            'description[format]': 1,
            'gradecat': categoryid,
            'submitbutton': 'Guardar canvis'
        }

        r = session.post(
            f"{base_url}/grade/edit/outcome/edit.php",
            cookies=cookie, data=form, timeout=15
        )

        if any(w in r.text.lower() for w in ["guardat", "saved", "creat", "created"]):
            output.insert(tk.END, f"   ✔ CE creat: {shortname}\n")
        else:
            time.sleep(1)
            check = session.get(
                f"{base_url}/grade/edit/outcome/index.php?id={course_id}",
                cookies=cookie, timeout=15
            )
            if shortname.lower() in check.text.lower():
                output.insert(tk.END, f"   ℹ CE detectat després del reintent: {shortname}\n")
            else:
                output.insert(tk.END, f"   ⚠ CE no creat: {shortname}\n", "warning")

        if progress_callback:
            progress_callback()

    except Exception as e:
        output.insert(tk.END, f"❌ Error CE {shortname}: {e}\n", "error")

# -------------------------------------------------------------
# OBTINDRE CATEGORIES RA EXISTENTS AL CURS
# -------------------------------------------------------------
def obtenir_categories_existents(session, cookie, base_url, course_id, output=None):
    """
    Retorna un conjunt amb els noms complets de categories del llibre de qualificacions d'Aules.
    Detecta les files que representen totals (p. ex. 'Total R42', 'Total RA42', 'Total CE42').
    """
    url = f"{base_url}/grade/edit/tree/index.php?id={course_id}"
    r = session.get(url, cookies=cookie)
    if r.status_code != 200:
        if output:
            output.insert(tk.END, f"⚠️ Error HTTP {r.status_code} en obtindre categories.\n")
        return set()

    soup = BeautifulSoup(r.text, "html.parser")
    categories = set()

    # Buscar textos del tipus 'Total R42', 'Total RA42', 'Total CE42'
    for td in soup.select("td.column-name"):
        text = td.get_text(" ", strip=True)
        if not text:
            continue
        
        # Patterns més flexibles
        patterns = [
            r"(?i)(total\s+(R|RA|CE)\d+)",  # Total R42, Total RA42, Total CE42
            r"(?i)(c[aá]lculo\s+total\s+(R|RA|CE)\d+)",  # Cálculo total R42
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                # Elimina 'Total ' o 'Cálculo total ' i conserva el nom complet
                nom = re.sub(r"(?i)c[aá]lculo\s+total\s+", "", text)
                nom = re.sub(r"(?i)^total\s+", "", nom).strip()
                categories.add(nom)
                if output:
                    output.insert(tk.END, f"📂 Categoria trobada: {nom}\n")
                break

    if output:
        output.insert(tk.END, f"📁 Total categories existents: {len(categories)}\n\n")
    return categories
    