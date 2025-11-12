#!/usr/bin/env python3
# =============================================================================
# aules_manager_v2.py
# Gestor unificat d’Aules GVA: Importar/Llistar escales i crear outcomes RA–CE
# =============================================================================

import requests, re, json, csv, time, tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from bs4 import BeautifulSoup
from tkinter import PhotoImage

# ===================== FUNCIONS COMUNES =====================

def login(session, base_url, username, password, output=None):
    if output:
        output.insert(tk.END, "➡️ Iniciant sessió a Aules...\n")
    r = session.get(f"{base_url}/login/index.php")
    token = re.search(r'name="logintoken" value="(\w{32})"', r.text)
    if not token:
        if output:
            output.insert(tk.END, "❌ No s’ha trobat logintoken.\n")
        return None, None
    payload = {"username": username, "password": password, "logintoken": token.group(1)}
    r = session.post(f"{base_url}/login/index.php", data=payload)
    sesskey = re.search(r"sesskey=(\w+)", r.text)
    if not sesskey:
        if output:
            output.insert(tk.END, "❌ Error d’autenticació. Revisa usuari/contrasenya.\n")
        return None, None
    if output:
        output.insert(tk.END, f"✅ Sessió iniciada correctament (sesskey={sesskey.group(1)})\n")
    return session.cookies.get_dict(), sesskey.group(1)


# -------------------------------------------------------------------------
# OBTAIN SCALES
def obtenir_escalas_existents(session, cookie, base_url, course_id, output=None):
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
        escalas[nom] = escala_id
        if output:
            output.insert(tk.END, f"  - {nom} (ID {escala_id})\n")

    if output:
        output.insert(tk.END, f"✅ Total escales trobades: {len(escalas)}\n")
    return escalas


# -------------------------------------------------------------------------
# IMPORT SCALES
def importar_escalas_des_de_csv(session, cookie, base_url, sesskey, course_id, fitxer_csv, output):
    output.insert(tk.END, f"📥 Important escales des de: {fitxer_csv}\n")
    with open(fitxer_csv, 'r', encoding='utf-8') as ftest:
        primera = ftest.readline()
        delimiter = ';' if ';' in primera and ',' not in primera else ','
    with open(fitxer_csv, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f, delimiter=delimiter)
        total = 0
        for fila in lector:
            nom = fila.get('Nom') or fila.get('name')
            valors = fila.get('Valors') or fila.get('scale')
            descripcio = fila.get('Descripció') or fila.get('description')
            if not nom or not valors:
                output.insert(tk.END, f"⚠️ Fila incompleta: {fila}\n")
                continue
            output.insert(tk.END, f"➕ Creant escala: {nom}\n")
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
            r = session.post(f"{base_url}/grade/edit/scale/edit.php", cookies=cookie, data=form)
            if any(w in r.text.lower() for w in ['guardat', 'saved', 'creat', 'created']):
                output.insert(tk.END, f"✅ Escala '{nom}' creada.\n")
            else:
                time.sleep(1)
                check = session.get(f"{base_url}/grade/edit/scale/index.php?id={course_id}", cookies=cookie)
                if nom.lower() in check.text.lower():
                    output.insert(tk.END, f"ℹ️ Escala '{nom}' detectada després del reintent.\n")
                else:
                    output.insert(tk.END, f"⚠️ No s’ha pogut verificar '{nom}'.\n")
            total += 1
    output.insert(tk.END, f"\n📊 Procés completat. Escales processades: {total}\n")

# -------------------------------------------------------------------------
# CREATE OUTCOMES RA–CE
def crear_outcome(session, cookie, base_url, sesskey, course_id, shortname, fullname, scaleid, description, output):
    form = {
        'id': 0, 'courseid': course_id, 'sesskey': sesskey,
        '_qf__edit_outcome_form': 1,
        'fullname': fullname, 'shortname': shortname,
        'scaleid': scaleid, 'description[text]': description, 'description[format]': 1,
        'submitbutton': 'Guardar canvis'
    }
    r = session.post(f"{base_url}/grade/edit/outcome/edit.php", cookies=cookie, data=form)
    if any(s in r.text.lower() for s in ["guardat", "creat", "saved", "created"]):
        output.insert(tk.END, f"✅ Outcome '{shortname}' creat correctament.\n")
        return True
    time.sleep(2)
    check = session.get(f"{base_url}/grade/edit/outcome/index.php?id={course_id}", cookies=cookie)
    if shortname.lower() in check.text.lower():
        output.insert(tk.END, f"ℹ️ Outcome '{shortname}' detectat després del reintent.\n")
        return True
    output.insert(tk.END, f"⚠️ No s’ha pogut crear '{shortname}'.\n")
    return False


def crear_outcomes_des_de_json(session, cookie, base_url, sesskey, course_id, fitxer_json, escala_nom, output):
    with open(fitxer_json, encoding="utf-8") as f:
        data = json.load(f)
    escalas = obtenir_escalas_existents(session, cookie, base_url, course_id)
    escala_id = None
    for nom, eid in escalas.items():
        if escala_nom.lower() in nom.lower():
            escala_id = eid
            break
    if not escala_id:
        output.insert(tk.END, f"❌ No s’ha trobat cap escala amb el nom '{escala_nom}'.\n")
        return
    output.insert(tk.END, f"✅ Escala trobada ({escala_nom}) ID={escala_id}\n")

    for cat in data.get("resultados", []):
        ra_full = cat["nombre"].strip()
        for elem in cat.get("criterios", []):
            nom = elem["nombre"]
            desc = nom.split(":", 1)[-1].strip()
            short = re.findall(r"RA\d+\.\w+", nom)[0] if re.findall(r"RA\d+\.\w+", nom) else nom[:15]
            crear_outcome(session, cookie, base_url, sesskey, course_id, short, desc, escala_id, desc, output)
    output.insert(tk.END, "\n📊 Procés de creació d’outcomes complet.\n")

# ===================== CLASSE GUI PRINCIPAL =====================

class AulesManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestor Aules GVA - Escales i Outcomes")
        self.root.geometry("850x650")
        self.session = None
        self.cookie = None
        self.sesskey = None
        self.base_url = None
        self.course_id = None
        self._pantalla_connexio()
        self.root.mainloop()

    def _netejar(self):
        for w in self.root.winfo_children():
            w.destroy()

    # Pantalla de connexió
    def _pantalla_connexio(self):
        self._netejar()
        self.root.configure(bg="#e9ecef")

        # Marc central
        frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove", padx=30, pady=20)
        frame.pack(pady=40)

        # Títol
        tk.Label(frame, text="🧩 Gestor Aules GVA", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#007c91").grid(row=0, column=0, columnspan=2, pady=(0, 15))
        tk.Label(frame, text="Importa escales i crea resultats d’aprenentatge (RA–CE)\na partir d’arxius CSV i JSON de forma automàtica.", 
                font=("Helvetica", 10), bg="#ffffff", fg="#444").grid(row=1, column=0, columnspan=2, pady=(0, 15))

        # Advertència
        aviso = (
            "⚠️ Aquesta eina utilitza una connexió web a Aules (Moodle GVA) simulant la interfície docent.\n"
            "No emmagatzema dades ni contrasenyes. Utilitza-la amb un compte docent i un curs de prova.\n"
            "El procés pot tardar uns segons segons la connexió i el nombre d’elements a crear."
        )
        tk.Label(frame, text=aviso, wraplength=500, justify="left", bg="#f8f9fa", fg="#555", font=("Helvetica", 9), relief="solid", padx=10, pady=8).grid(row=2, column=0, columnspan=2, pady=(0, 20))

        # Camps d’entrada
        tk.Label(frame, text="🌐 URL base d’Aules:", bg="#ffffff", anchor="e").grid(row=3, column=0, sticky="e", pady=3)
        self.url = tk.Entry(frame, width=45)
        self.url.grid(row=3, column=1, pady=3)

        tk.Label(frame, text="👤 Usuari:", bg="#ffffff", anchor="e").grid(row=4, column=0, sticky="e", pady=3)
        self.user = tk.Entry(frame, width=45)
        self.user.grid(row=4, column=1, pady=3)

        tk.Label(frame, text="🔑 Contrasenya:", bg="#ffffff", anchor="e").grid(row=5, column=0, sticky="e", pady=3)
        self.pwd = tk.Entry(frame, width=45, show="*")
        self.pwd.grid(row=5, column=1, pady=3)

        tk.Label(frame, text="📘 ID del curs:", bg="#ffffff", anchor="e").grid(row=6, column=0, sticky="e", pady=3)
        self.course = tk.Entry(frame, width=45)
        self.course.grid(row=6, column=1, pady=3)

        # Botons
        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(15, 0))

        tk.Button(btn_frame, text="🚀 Entrar", bg="#007c91", fg="white", width=15, font=("Helvetica", 10, "bold"),
                relief="raised", command=self._connectar).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="❌ Eixir", bg="#e53935", fg="white", width=10, font=("Helvetica", 10),
                command=self.root.destroy).pack(side=tk.LEFT, padx=5)

        # Peu informatiu
        tk.Label(
            self.root,
            text=(
                "© 2025 jbtalens · Llicència GPL-3.0\n"
                "Basat parcialment en idees de GestionCalificacionesAules (Martínez Peña i J. García)"
            ),
            font=("Helvetica", 8),
            bg="#e9ecef",
            fg="#666",
            justify="center"
        ).pack(side=tk.BOTTOM, pady=5)

        
        logo = PhotoImage(file="icons/gestor-aules.png")
        tk.Label(frame, image=logo, bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=(0,10))
        self.root.logo = logo  # evitar que s’esborre del garbage collector





    def _connectar(self):
        self.log.delete(1.0, tk.END)
        self.base_url = self.url.get().strip()
        username = self.user.get().strip()
        password = self.pwd.get().strip()
        self.course_id = self.course.get().strip()
        if not all([self.base_url, username, password, self.course_id]):
            messagebox.showerror("Error", "Falten camps obligatoris.")
            return
        self.session = requests.Session()
        self.cookie, self.sesskey = login(self.session, self.base_url, username, password, self.log)
        if self.sesskey:
            self._pantalla_menu()

    # Menú principal
    def _pantalla_menu(self):
        self._netejar()
        tk.Label(self.root, text=f"Connexió activa a {self.base_url} (Curs {self.course_id})", fg="#007c91", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(self.root, text="📈 Importar escales des de CSV", width=40, bg="#2196F3", fg="white", command=self._pantalla_importar).pack(pady=5)
        tk.Button(self.root, text="📋 Llistar escales existents", width=40, bg="#4CAF50", fg="white", command=self._pantalla_llistar).pack(pady=5)
        tk.Button(self.root, text="🧾 Crear outcomes RA–CE", width=40, bg="#9C27B0", fg="white", command=self._pantalla_outcomes).pack(pady=5)
        tk.Button(self.root, text="⬅️ Tornar a Connexió", width=40, command=self._pantalla_connexio).pack(pady=5)
        tk.Button(self.root, text="❌ Eixir", width=40, bg="#e53935", fg="white", command=self.root.destroy).pack(pady=5)

    # Subpantalla Importar
    def _pantalla_importar(self):
        self._netejar()
        tk.Label(self.root, text="Selecciona un fitxer CSV d’escales per importar").pack(pady=10)
        self.entry_csv = tk.Entry(self.root, width=60)
        self.entry_csv.pack()
        tk.Button(self.root, text="Seleccionar…", command=self._triar_csv).pack(pady=5)
        tk.Button(self.root, text="Iniciar importació", bg="#2196F3", fg="white", command=self._executar_importacio).pack(pady=5)
        tk.Button(self.root, text="⬅️ Tornar", command=self._pantalla_menu).pack(pady=5)
        self.output = ScrolledText(self.root, width=100, height=25)
        self.output.pack(padx=10, pady=10)

    def _triar_csv(self):
        fitxer = filedialog.askopenfilename(filetypes=[("Fitxers CSV", "*.csv")])
        if fitxer:
            self.entry_csv.delete(0, tk.END)
            self.entry_csv.insert(0, fitxer)

    def _executar_importacio(self):
        fitxer_csv = self.entry_csv.get().strip()
        if not fitxer_csv:
            messagebox.showerror("Error", "Selecciona un fitxer CSV.")
            return
        self.output.delete(1.0, tk.END)
        importar_escalas_des_de_csv(self.session, self.cookie, self.base_url, self.sesskey, self.course_id, fitxer_csv, self.output)

    # Subpantalla Llistar escales
    def _pantalla_llistar(self):
        self._netejar()
        tk.Button(self.root, text="⬅️ Tornar", command=self._pantalla_menu).pack(pady=5)
        self.output = ScrolledText(self.root, width=100, height=25)
        self.output.pack(padx=10, pady=10)
        obtenir_escalas_existents(self.session, self.cookie, self.base_url, self.course_id, self.output)

    # Subpantalla Crear outcomes
    def _pantalla_outcomes(self):
        self._netejar()
        tk.Label(self.root, text="Selecciona el fitxer JSON d’outcomes RA–CE:").pack(pady=10)
        self.entry_json = tk.Entry(self.root, width=60)
        self.entry_json.pack()
        tk.Button(self.root, text="Seleccionar…", command=self._triar_json).pack(pady=5)
        tk.Label(self.root, text="Nom (o part) de l’escala a utilitzar:").pack(pady=5)
        self.entry_escala = tk.Entry(self.root, width=60)
        self.entry_escala.insert(0, "Escala 0-10")
        self.entry_escala.pack()
        tk.Button(self.root, text="Iniciar creació d’outcomes", bg="#9C27B0", fg="white", command=self._executar_outcomes).pack(pady=5)
        tk.Button(self.root, text="⬅️ Tornar", command=self._pantalla_menu).pack(pady=5)
        self.output = ScrolledText(self.root, width=100, height=25)
        self.output.pack(padx=10, pady=10)

    def _triar_json(self):
        fitxer = filedialog.askopenfilename(filetypes=[("Fitxers JSON", "*.json")])
        if fitxer:
            self.entry_json.delete(0, tk.END)
            self.entry_json.insert(0, fitxer)

    def _executar_outcomes(self):
        fitxer_json = self.entry_json.get().strip()
        escala_nom = self.entry_escala.get().strip()
        if not fitxer_json or not escala_nom:
            messagebox.showerror("Error", "Selecciona fitxer JSON i indica una escala.")
            return
        self.output.delete(1.0, tk.END)
        crear_outcomes_des_de_json(self.session, self.cookie, self.base_url, self.sesskey, self.course_id, fitxer_json, escala_nom, self.output)


if __name__ == "__main__":
    AulesManager()
