#!/usr/bin/env python3
# =============================================================================
# importar_escalas.py
# Importa escales des d’un fitxer CSV a un curs d’Aules/Moodle sense accés backend
# També pot llistar totes les escales existents amb el seu contingut complet
# =============================================================================

import requests, re, csv, time, tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from bs4 import BeautifulSoup

# ========================== FUNCIONS PRINCIPALS ===========================

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

# -------------------------------------------------------------------------

def obtenir_escalas_existents(session, cookie, base_url, course_id, output=None):
    """
    Retorna un diccionari amb totes les escales visibles al curs:
      { nom_escala: {"id": id, "valors": "A, B, C", "descripcio": "text..."} }
    """
    if output:
        output.insert(tk.END, "🔍 Obtenint escales existents...\n")
    escalas = {}
    url = f"{base_url}/grade/edit/scale/index.php?id={course_id}"
    r = session.get(url, cookies=cookie)
    if r.status_code != 200:
        if output:
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
        escala_detall = {"id": escala_id, "valors": None, "descripcio": None}

        # ✨ Nova part: accedir a la pàgina d’edició per traure més info
        deturl = f"{base_url}/grade/edit/scale/edit.php?courseid={course_id}&id={escala_id}"
        det = session.get(deturl, cookies=cookie)
        if det.status_code == 200:
            detsoup = BeautifulSoup(det.text, "html.parser")
            nom_field = detsoup.find("input", {"name": "name"})
            valors_field = detsoup.find("textarea", {"name": "scale"})
            desc_field = detsoup.find("textarea", {"name": "description[text]"})

            if valors_field:
                escala_detall["valors"] = valors_field.get_text(strip=True)
            if desc_field:
                escala_detall["descripcio"] = desc_field.get_text(strip=True)
            if nom_field:
                nom = nom_field.get("value", nom)

        escalas[nom] = escala_detall
        if output:
            output.insert(tk.END, f"  - {nom} (ID {escala_id})\n")

    if not escalas and output:
        output.insert(tk.END, "⚠️ No s’han detectat escales a la taula HTML.\n")
    else:
        output.insert(tk.END, f"✅ Total escales trobades: {len(escalas)}\n")

    return escalas

# -------------------------------------------------------------------------

def importar_escalas_des_de_csv(session, cookie, base_url, sesskey, course_id, fitxer_csv, output):
    output.insert(tk.END, f"📥 Important escales des de: {fitxer_csv}\n")

    # Detecta automàticament el separador
    with open(fitxer_csv, 'r', encoding='utf-8') as ftest:
        primera_linia = ftest.readline()
        delimiter = ';' if ';' in primera_linia and ',' not in primera_linia else ','
    output.insert(tk.END, f"ℹ️ Separador detectat: '{delimiter}'\n")

    with open(fitxer_csv, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f, delimiter=delimiter)
        total = 0
        for fila in lector:
            # Admet tant capçaleres en valencià com en anglès
            nom = fila.get('Nom') or fila.get('name') or fila.get('Name')
            valors = fila.get('Valors') or fila.get('scale') or fila.get('Values')
            descripcio = fila.get('Descripció') or fila.get('description') or fila.get('Description')

            if not nom or not valors:
                output.insert(tk.END, f"⚠️ Fila incompleta, s’omet: {fila}\n")
                continue

            output.insert(tk.END, f"➕ Creant escala: {nom}\n")
            form = {
                'id': 0,
                'courseid': course_id,
                'sesskey': sesskey,
                '_qf__edit_scale_form': 1,
                'name': nom.strip(),
                'scale': valors.strip(),
                'description[text]': (descripcio or '').strip(),
                'description[format]': 1,
                'standard': 1,
                'submitbutton': 'Guardar canvis'
            }

            r = session.post(f"{base_url}/grade/edit/scale/edit.php", cookies=cookie, data=form)
            if any(w in r.text.lower() for w in ['guardat', 'saved', 'creat', 'created']):
                output.insert(tk.END, f"✅ Escala '{nom}' creada correctament.\n")
            else:
                time.sleep(1)
                check = session.get(f"{base_url}/grade/edit/scale/index.php?id={course_id}", cookies=cookie)
                if nom.lower() in check.text.lower():
                    output.insert(tk.END, f"ℹ️ Escala '{nom}' detectada després del reintent.\n")
                else:
                    output.insert(tk.END, f"⚠️ No s’ha pogut verificar la creació de '{nom}'.\n")
            total += 1

    output.insert(tk.END, f"\n📊 Procés completat. Escales processades: {total}\n")

# ========================== INTERFÍCIE TKINTER ===========================

def executar_importacio():
    base_url = entry_url.get().strip()
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    course_id = entry_course.get().strip()
    fitxer_csv = entry_csv.get().strip()

    if not all([base_url, username, password, course_id, fitxer_csv]):
        messagebox.showerror("Error", "Falten camps obligatoris.")
        return

    output.delete(1.0, tk.END)
    s = requests.Session()
    cookie, sesskey = login(s, base_url, username, password, output)
    if sesskey:
        importar_escalas_des_de_csv(s, cookie, base_url, sesskey, course_id, fitxer_csv, output)
        messagebox.showinfo("Finalitzat", "Procés completat correctament!")

def llistar_escalas_existents():
    base_url = entry_url.get().strip()
    username = entry_user.get().strip()
    password = entry_pass.get().strip()
    course_id = entry_course.get().strip()

    if not all([base_url, username, password, course_id]):
        messagebox.showerror("Error", "Cal indicar URL, usuari, contrasenya i ID del curs.")
        return

    output.delete(1.0, tk.END)
    s = requests.Session()
    cookie, sesskey = login(s, base_url, username, password, output)
    if sesskey:
        escalas = obtenir_escalas_existents(s, cookie, base_url, course_id, output)
        output.insert(tk.END, "\n📄 Dades completes de cada escala:\n")
        for nom, info in escalas.items():
            output.insert(tk.END, f"\n➡️ {nom}\n   ID: {info['id']}\n   Valors: {info['valors']}\n   Descripció: {info['descripcio']}\n")

def seleccionar_csv():
    fitxer = filedialog.askopenfilename(filetypes=[("Fitxers CSV", "*.csv")])
    if fitxer:
        entry_csv.delete(0, tk.END)
        entry_csv.insert(0, fitxer)

def eixir_programa():
    if messagebox.askyesno("Confirmació", "Segur que vols eixir del programa?"):
        root.destroy()

# ========================== FINESTRA PRINCIPAL ===========================

root = tk.Tk()
root.title("Importador d’Escales - Aules GVA")
root.resizable(True, True)
root.minsize(800, 600)

tk.Label(root, text="🌐 URL base d’Aules:").grid(row=0, column=0, sticky="e")
entry_url = tk.Entry(root, width=50)
entry_url.grid(row=0, column=1)
entry_url.insert(0, "https://aules.edu.gva.es/docent")

tk.Label(root, text="👤 Usuari:").grid(row=1, column=0, sticky="e")
entry_user = tk.Entry(root, width=50)
entry_user.grid(row=1, column=1)

tk.Label(root, text="🔑 Contrasenya:").grid(row=2, column=0, sticky="e")
entry_pass = tk.Entry(root, width=50, show="*")
entry_pass.grid(row=2, column=1)

tk.Label(root, text="📘 ID del curs:").grid(row=3, column=0, sticky="e")
entry_course = tk.Entry(root, width=50)
entry_course.grid(row=3, column=1)

tk.Label(root, text="📈 Fitxer d’escales CSV:").grid(row=4, column=0, sticky="e")
entry_csv = tk.Entry(root, width=40)
entry_csv.grid(row=4, column=1, sticky="w")
tk.Button(root, text="Seleccionar…", command=seleccionar_csv).grid(row=4, column=2)

frame_botons = tk.Frame(root)
frame_botons.grid(row=5, column=0, columnspan=3, pady=10)

tk.Button(frame_botons, text="📥 Importar escales", bg="#2196F3", fg="white", width=17, command=executar_importacio).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botons, text="📋 Llistar escales existents", bg="#4CAF50", fg="white", width=22, command=llistar_escalas_existents).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botons, text="❌ Eixir", bg="#e53935", fg="white", width=10, command=eixir_programa).pack(side=tk.LEFT, padx=5)

output = ScrolledText(root, width=100, height=25, wrap=tk.WORD)
output.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
