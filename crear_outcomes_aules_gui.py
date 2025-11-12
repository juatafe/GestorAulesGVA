#!/usr/bin/env python3
# =============================================================================
# crear_outcomes_aules_gui.py
# Versió amb interfície gràfica (Tkinter) per a crear categories RA i outcomes CE a Aules
# Basat en crear_outcomes_aules_v2.py
# =============================================================================

import requests, re, json, time
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, messagebox

# ======================== FUNCIONS PRINCIPALS =============================

def login(session, base_url, username, password, output):
    output.insert(tk.END, "➡️ Iniciant sessió a Aules...\n")
    r = session.get(f"{base_url}/login/index.php")
    token = re.search(r'name="logintoken" value="(\w{32})"', r.text)
    if not token:
        output.insert(tk.END, "❌ No s’ha trobat logintoken.\n")
        return None, None
    payload = {"username": username, "password": password, "logintoken": token.group(1)}
    r = session.post(f"{base_url}/login/index.php", data=payload)
    sesskey = re.search(r"sesskey=(\w+)", r.text)
    if not sesskey:
        output.insert(tk.END, "❌ Error d’autenticació. Revisa usuari/contrasenya.\n")
        return None, None
    output.insert(tk.END, f"✅ Sessió iniciada correctament (sesskey={sesskey.group(1)})\n")
    return session.cookies.get_dict(), sesskey.group(1)


def obtenir_escalas_existents(session, cookie, base_url, course_id, output):
    output.insert(tk.END, "🔍 Obtenint escales existents...\n")
    escalas = {}
    url = f"{base_url}/grade/edit/scale/index.php?id={course_id}"
    r = session.get(url, cookies=cookie)
    if r.status_code != 200:
        output.insert(tk.END, f"⚠️ Error HTTP {r.status_code} en obtindre escales.\n")
        return escalas
    soup = BeautifulSoup(r.text, "html.parser")
    for fila in soup.select("table.generaltable tr"):
        celdas = fila.find_all("td")
        if not celdas:
            continue
        nom = celdas[0].get_text(strip=True)
        link = fila.find("a", href=re.compile(r"edit\.php\?courseid=\d+&id=\d+"))
        if not link:
            continue
        m = re.search(r"&id=(\d+)", link["href"])
        if not m:
            continue
        escala_id = m.group(1)
        escalas[nom] = escala_id
        output.insert(tk.END, f"  - {nom} (ID real: {escala_id})\n")
    if not escalas:
        output.insert(tk.END, "⚠️ No s’han detectat escales a la taula HTML.\n")
    return escalas


def obtenir_categories_existents(session, cookie, base_url, course_id, output):
    url = f"{base_url}/grade/edit/tree/index.php?id={course_id}"
    r = session.get(url, cookies=cookie)
    if r.status_code != 200:
        output.insert(tk.END, f"⚠️ Error HTTP {r.status_code} en obtindre categories.\n")
        return set()
    soup = BeautifulSoup(r.text, "html.parser")
    categories = set()
    for td in soup.select("td.column-name"):
        text = td.get_text(" ", strip=True)
        if not text:
            continue
        if re.search(r"(?i)(total\s+RA\d+)", text):
            nom = re.sub(r"(?i)c[aá]lculo\s+total\s+", "", text)
            nom = re.sub(r"(?i)^total\s+", "", nom).strip()
            categories.add(nom)
    output.insert(tk.END, f"🔍 Categories trobades: {', '.join(categories) if categories else '(cap)'}\n")
    return categories


def crear_categoria_ra(session, cookie, base_url, sesskey, course_id, nom, output):
    output.insert(tk.END, f"➕ Creant categoria RA: {nom}\n")
    form = {
        "courseid": course_id,
        "sesskey": sesskey,
        "_qf__edit_category_form": 1,
        "fullname": nom,
        "aggregation": 10,
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


def obtener_outcomes_existentes(session, cookie, base_url, course_id):
    outcomes_map = {}
    url = f"{base_url}/grade/edit/outcome/index.php?id={course_id}"
    r = session.get(url, cookies=cookie)
    if r.status_code != 200:
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    for fila in soup.find_all('tr'):
        enlaces = fila.find_all('a', href=True)
        outcome_id = None
        for a in enlaces:
            href = a['href']
            if 'action=delete' in href and 'outcomeid=' in href:
                m = re.search(r'outcomeid=(\d+)', href)
                if m:
                    outcome_id = m.group(1)
                    break
        if not outcome_id:
            continue
        texto_fila = fila.get_text(" ", strip=True)
        mname = re.search(r'(RA\d+\.\w+)', texto_fila)
        if mname:
            shortname = mname.group(1)
            outcomes_map[shortname] = outcome_id
    return outcomes_map


def crear_outcome(session, cookie, base_url, sesskey, course_id, shortname, fullname, scaleid, description, output):
    outcomes_existents = obtener_outcomes_existentes(session, cookie, base_url, course_id)
    if shortname in outcomes_existents:
        output.insert(tk.END, f"✓ Outcome '{shortname}' ja existeix.\n")
        return True

    output.insert(tk.END, f"➕ Creant outcome: {shortname}\n")
    form = {
        'id': 0,
        'courseid': course_id,
        'sesskey': sesskey,
        '_qf__edit_outcome_form': 1,
        'fullname': fullname,
        'shortname': shortname,
        'scaleid': scaleid,
        'description[text]': description,
        'description[format]': 1,
        'submitbutton': 'Guardar canvis'
    }
    r = session.post(f"{base_url}/grade/edit/outcome/edit.php", cookies=cookie, data=form)

    # 🔍 Comprovació de text de resposta
    if any(s in r.text.lower() for s in ["guardat", "creat", "saved", "created"]):
        output.insert(tk.END, f"✅ Outcome '{shortname}' creat correctament.\n")
        return True

    # 🕓 Reintent: comprova si ja apareix a la llista després d’uns segons
    time.sleep(2)
    outcomes_nous = obtener_outcomes_existentes(session, cookie, base_url, course_id)
    if shortname in outcomes_nous:
        output.insert(tk.END, f"ℹ️ Outcome '{shortname}' detectat després del reintent.\n")
        return True

    output.insert(tk.END, f"⚠️ No s’ha pogut verificar la creació de '{shortname}', però podria estar ja creat.\n")
    return False



# ======================== INTERFÍCIE TKINTER =============================


def executar_script():
    base_url = entry_url.get().strip()
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    course_id = entry_course.get().strip()
    escala_nom = entry_escala.get().strip()
    json_path = entry_json.get().strip()

    if not all([base_url, username, password, course_id, json_path]):
        messagebox.showerror("Error", "Falten camps obligatoris.")
        return

    output.delete(1.0, tk.END)
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    s = requests.Session()
    cookie, sesskey = login(s, base_url, username, password, output)
    if not sesskey:
        return

    escalas = obtenir_escalas_existents(s, cookie, base_url, course_id, output)
    if not escalas:
        output.insert(tk.END, "❌ No s’han pogut obtenir les escales.\n")
        return

    escala_id = None
    for nom, eid in escalas.items():
        if escala_nom.lower() in nom.lower():
            escala_id = eid
            output.insert(tk.END, f"✅ Escala trobada: {nom} (ID {eid})\n")
            break
    if not escala_id:
        output.insert(tk.END, f"❌ No s’ha trobat cap escala amb el nom '{escala_nom}'.\n")
        return

    categories_existents = obtenir_categories_existents(s, cookie, base_url, course_id, output)
    resultat_final = {}

    for cat in data.get("resultados", []):
        ra_full = cat["nombre"].strip()
        ra_short = ra_full.split(":")[0].strip()
        if any(ra_full.lower() == c.lower() for c in categories_existents):
            output.insert(tk.END, f"✓ Categoria '{ra_full}' ja existeix.\n")
        else:
            crear_categoria_ra(s, cookie, base_url, sesskey, course_id, ra_full, output)

        criteris = cat.get("criterios", [])
        pesos = [float(c.get("peso", 0)) for c in criteris]
        if not any(pesos):
            pesos = [round(100 / len(criteris), 2)] * len(criteris)
        resultat_final[ra_full] = {}

        for i, elem in enumerate(criteris):
            nom = elem["nombre"]
            m = re.match(r"CE(\d+)[\.\-](\w+)", nom)
            if not m:
                continue
            ra, lletra = m.groups()
            short = f"RA{ra}.{lletra}"
            desc = nom.split(":", 1)[-1].strip()
            full = f"{short}: {desc}"
            ok = crear_outcome(s, cookie, base_url, sesskey, course_id, short, full, escala_id, desc, output)
            resultat_final[ra_full][short] = {"creat": bool(ok), "peso": pesos[i]}

    with open("outcomes_created.json", "w", encoding="utf-8") as f:
        json.dump(resultat_final, f, ensure_ascii=False, indent=2)

    output.insert(tk.END, "\n📊 Resultats guardats a 'outcomes_created.json'\n")
    messagebox.showinfo("Finalitzat", "Procés completat correctament!")

def seleccionar_json():
    fitxer = filedialog.askopenfilename(filetypes=[("Fitxers JSON", "*.json")])
    if fitxer:
        entry_json.delete(0, tk.END)
        entry_json.insert(0, fitxer)

# ======================== FINESTRA PRINCIPAL =============================

root = tk.Tk()
root.title("Creador de Outcomes Aules GVA")

tk.Label(root, text="🌐 URL base d’Aules:").grid(row=0, column=0, sticky="e")
entry_url = tk.Entry(root, width=50)
entry_url.grid(row=0, column=1)

tk.Label(root, text="👤 Usuari:").grid(row=1, column=0, sticky="e")
entry_user = tk.Entry(root, width=50)
entry_user.grid(row=1, column=1)

tk.Label(root, text="🔑 Contrasenya:").grid(row=2, column=0, sticky="e")
entry_pass = tk.Entry(root, width=50, show="*")
entry_pass.grid(row=2, column=1)

tk.Label(root, text="📘 ID del curs:").grid(row=3, column=0, sticky="e")
entry_course = tk.Entry(root, width=50)
entry_course.grid(row=3, column=1)

tk.Label(root, text="📄 Fitxer JSON:").grid(row=4, column=0, sticky="e")
entry_json = tk.Entry(root, width=40)
entry_json.grid(row=4, column=1, sticky="w")
tk.Button(root, text="Seleccionar…", command=seleccionar_json).grid(row=4, column=2)

tk.Label(root, text="⚖️ Nom de l’escala:").grid(row=5, column=0, sticky="e")
entry_escala = tk.Entry(root, width=50)
entry_escala.insert(0, "Escala 0-10")
entry_escala.grid(row=5, column=1)

# === BOTONS PRINCIPALS ===
frame_botons = tk.Frame(root)
frame_botons.grid(row=6, column=0, columnspan=3, pady=10)

btn_executar = tk.Button(frame_botons, text="🚀 Executar", bg="#4CAF50", fg="white", width=12, command=executar_script)
btn_executar.pack(side=tk.LEFT, padx=5)

def eixir_programa():
    if messagebox.askyesno("Confirmació", "Segur que vols eixir del programa?"):
        root.destroy()

btn_eixir = tk.Button(frame_botons, text="❌ Eixir", bg="#e53935", fg="white", width=12, command=eixir_programa)
btn_eixir.pack(side=tk.LEFT, padx=5)
# ======================== ÀREA DE SORTIDA =============================
output = tk.Text(root, width=80, height=20)
output.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
