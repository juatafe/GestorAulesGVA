# gestor_aules_gva/gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, ttk
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import re 
from .aules_api import (
    login,
    obtenir_escalas_existents,
    importar_escalas_des_de_csv 
)


class AulesManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gestor Aules GVA – Escales i Outcomes")
        self.root.geometry("880x680")
        self.root.configure(bg="#e9ecef")

        # Intentar carregar icono
        self._carregar_icono()

        # Estat intern
        self.session = None
        self.cookie = None
        self.sesskey = None
        self.base_url = None
        self.course_id = None
        
        self._pantalla_connexio()
        self.root.mainloop()

    def _carregar_icono(self):
        """Intenta carregar l'icono des de diverses rutes possibles"""
        import os
        
        # En Linux utilitzem PNG, en Windows ICO
        rutes_prova = [
            # Primer intentem amb PNG (Linux)
            "icons/gestor-aules.png",
            "icons/gestor-aules-256.png", 
            "../icons/gestor-aules.png",
            "../icons/gestor-aules-256.png",
            os.path.join(os.path.dirname(__file__), "..", "icons", "gestor-aules.png"),
            os.path.join(os.path.dirname(__file__), "..", "icons", "gestor-aules-256.png"),
            # Després amb ICO (Windows)
            "icons/gestor-aules.ico",
            "../icons/gestor-aules.ico",
            os.path.join(os.path.dirname(__file__), "..", "icons", "gestor-aules.ico"),
        ]
        
        for ruta in rutes_prova:
            try:
                if os.path.exists(ruta):
                    if ruta.lower().endswith('.png'):
                        # Per a Linux: PNG amb PhotoImage
                        img = tk.PhotoImage(file=ruta)
                        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
                        print(f"✅ Icono PNG carregat des de: {ruta}")
                        self.icon_img = img  # Guardar referència
                        return True
                    elif ruta.lower().endswith('.ico'):
                        # Per a Windows: ICO amb iconbitmap
                        self.root.iconbitmap(ruta)
                        print(f"✅ Icono ICO carregat des de: {ruta}")
                        return True
            except Exception as e:
                print(f"⚠️ Error carregant {ruta}: {e}")
                continue
        
        print("❌ No s'ha pogut carregar cap icono")
        return False
    # ------------------------------------------------------------
    # UTILITATS
    # ------------------------------------------------------------
    def _netejar(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _add_hover(self, btn, normal_bg=None, hover_bg=None):
        btn.configure(cursor="hand2")
        if normal_bg and hover_bg:
            btn.configure(bg=normal_bg, activebackground=normal_bg)
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
            btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

    def _insert(self, msg, tag=None):
        """Inserta text al log amb color segons etiqueta."""
        self.output.insert(tk.END, msg)
        if tag:
            self.output.tag_add(tag, "end-%dc" % (len(msg) + 1), "end-1c")
        self.output.see(tk.END)
        self.output.update_idletasks()

    # ------------------------------------------------------------
    # PANTALLA CONNEXIÓ
    # ------------------------------------------------------------
    def _pantalla_connexio(self):
        self._netejar()
        self.root.configure(bg="#e9ecef")

        # Marc central
        frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove", padx=30, pady=20)
        frame.pack(pady=40)

        # Logo — cal guardar la referència per evitar que Tkinter l'esborre
        try:
            img = PhotoImage(file="icons/gestor-aules-256.png")
            # Redueix la imatge a la meitat (prova 2, 3, 4 segons et convinga)
            img = img.subsample(2, 2)
            self.logo_img = img  # guarda referència per evitar GC
            logo_label = tk.Label(frame, image=self.logo_img, bg="#ffffff")
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        except Exception as e:
            print(f"[⚠️ Logo no carregat: {e}]")
            tk.Label(
                frame,
                text="Gestor Aules GVA",
                font=("Helvetica", 14, "bold"),
                bg="#ffffff",
                fg="#007c91"
            ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Títol i subtítol
        tk.Label(frame, text="🧩 Gestor Aules GVA", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#007c91").grid(row=1, column=0, columnspan=2, pady=(0, 15))
        tk.Label(frame, text="Importa escales i crea resultats d’aprenentatge (RA–CE)\na partir d’arxius CSV i JSON de forma automàtica.", 
                font=("Helvetica", 10), bg="#ffffff", fg="#444").grid(row=2, column=0, columnspan=2, pady=(0, 15))

        # Advertència
        aviso = (
            "⚠️ Aquesta eina utilitza una connexió web a Aules (Moodle GVA) o altre moodle simulant la interfície docent.\n"
            "No emmagatzema dades ni contrasenyes. Utilitza-la amb el sabor docent i/ o un curs de prova abans de passar a producció.\n"
            "El procés pot tardar uns segons segons la connexió i el nombre d’elements a crear."
        )
        tk.Label(frame, text=aviso, wraplength=500, justify="left", bg="#f8f9fa", fg="#555", font=("Helvetica", 9), relief="solid", padx=10, pady=8).grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # Camps d’entrada
        tk.Label(frame, text="🌐 URL base d’Aules:", bg="#ffffff", anchor="e").grid(row=4, column=0, sticky="e", pady=3)
        self.url = tk.Entry(frame, width=45)
        self.url.grid(row=4, column=1, pady=3)

        tk.Label(frame, text="👤 Usuari:", bg="#ffffff", anchor="e").grid(row=5, column=0, sticky="e", pady=3)
        self.user = tk.Entry(frame, width=45)
        self.user.grid(row=5, column=1, pady=3)

        tk.Label(frame, text="🔑 Contrasenya:", bg="#ffffff", anchor="e").grid(row=6, column=0, sticky="e", pady=3)
        self.pwd = tk.Entry(frame, width=45, show="*")
        self.pwd.grid(row=6, column=1, pady=3)

        tk.Label(frame, text="📘 ID del curs:", bg="#ffffff", anchor="e").grid(row=7, column=0, sticky="e", pady=3)
        self.course = tk.Entry(frame, width=45)
        self.course.grid(row=7, column=1, pady=3)

        # Separador i botons
        separator = tk.Frame(frame, bg="#dee2e6", height=1, width=400)
        separator.grid(row=8, column=0, columnspan=2, pady=(10, 15))

        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(5, 15))


        btn_entrar = tk.Button(
            btn_frame, text="🚀 Entrar",
            bg="#007c91", fg="white",
            width=15, font=("Helvetica", 10, "bold"),
            relief="raised", command=self._connectar
        )
        self._add_hover(btn_entrar, "#007c91", "#0096b0")
        btn_entrar.pack(side=tk.LEFT, padx=5)

        btn_eixir = tk.Button(
            btn_frame, text="❌ Eixir",
            bg="#e53935", fg="white",
            width=10, font=("Helvetica", 10),
            command=self.root.destroy
        )
        self._add_hover(btn_eixir, "#e53935", "#d32f2f")
        btn_eixir.pack(side=tk.LEFT, padx=5)

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

    # ------------------------------------------------------------
    # CONNEXIÓ I MENÚ PRINCIPAL
    # ------------------------------------------------------------
    def _connectar(self):
        if not all([self.url.get(), self.user.get(), self.pwd.get(), self.course.get()]):
            messagebox.showerror("Error", "Falten camps obligatoris.")
            return

        self.session = requests.Session()
        base_url = self.url.get().strip()
        username = self.user.get().strip()
        password = self.pwd.get().strip()
        course_id = self.course.get().strip()

        log_window = tk.Toplevel(self.root)
        log_window.title("Connexió a Aules GVA")
        log_window.geometry("500x300")
        output = ScrolledText(log_window, width=60, height=15)
        output.pack(padx=10, pady=10)
        cookie, sesskey = login(self.session, base_url, username, password, output)

        if sesskey:
            self.cookie, self.sesskey, self.base_url, self.course_id = cookie, sesskey, base_url, course_id
            log_window.destroy()
            self._pantalla_menu()
        else:
            messagebox.showerror("Error d’autenticació", "No s’ha pogut iniciar sessió correctament.")

    def _pantalla_menu(self):
        self._netejar()
        tk.Label(self.root, text=f"Connexió activa a {self.base_url} (Curs {self.course_id})", fg="#007c91", font=("Arial", 12, "bold")).pack(pady=10)

        #tk.Checkbutton(self.root, text="🔍 Mode simulació (no enviar canvis a Moodle)", variable=self.simular, bg="#e9ecef").pack()

        b1 = tk.Button(self.root, text="📈 Importar escales des de CSV", width=40, bg="#2196F3", fg="white", command=self._pantalla_importar)
        self._add_hover(b1, "#2196F3", "#1e88e5")
        b1.pack(pady=5)

        b2 = tk.Button(self.root, text="📋 Llistar escales existents", width=40, bg="#4CAF50", fg="white", command=self._pantalla_llistar)
        self._add_hover(b2, "#4CAF50", "#43a047")
        b2.pack(pady=5)

        b3 = tk.Button(self.root, text="🧾 Crear outcomes RA–CE", width=40, bg="#9C27B0", fg="white", command=self._pantalla_outcomes)
        self._add_hover(b3, "#9C27B0", "#8e24aa")
        b3.pack(pady=5)

        tk.Button(self.root, text="⬅️ Tornar a Connexió", width=40, command=self._pantalla_connexio).pack(pady=5)
        tk.Button(self.root, text="❌ Eixir", width=40, bg="#e53935", fg="white", command=self.root.destroy).pack(pady=5)

    # ------------------------------------------------------------
    # SUBPANTALLES
    # ------------------------------------------------------------
    def _pantalla_importar(self):
        self._netejar()
        frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove", padx=30, pady=20)
        frame.pack(pady=25)

        tk.Label(frame, text="📈 Importar escales des de CSV(Cal ser admin)", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#007c91").pack(pady=(0, 15))
        file_frame = tk.Frame(frame, bg="#ffffff")
        file_frame.pack(pady=(5, 10))
        self.entry_csv = tk.Entry(file_frame, width=60)
        self.entry_csv.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(file_frame, text="📂 Seleccionar…", bg="#6c757d", fg="white", command=self._triar_csv).pack(side=tk.LEFT)

        tk.Button(frame, text="🚀 Iniciar importació", bg="#2196F3", fg="white", command=self._executar_importacio).pack(pady=5)
        tk.Button(frame, text="⬅️ Tornar al menú", bg="#f1f3f5", fg="#333", command=self._pantalla_menu).pack(pady=5)

        self.output = ScrolledText(frame, width=90, height=20)
        self.output.pack(fill="both", expand=True, pady=10)
        self._config_tags()

    def _pantalla_llistar(self):
        self._netejar()
        tk.Button(self.root, text="⬅️ Tornar", command=self._pantalla_menu).pack(pady=5)
        self.output = ScrolledText(self.root, width=100, height=25)
        self.output.pack(padx=10, pady=10)
        self._config_tags()
        obtenir_escalas_existents(self.session, self.cookie, self.base_url, self.course_id, self.output)

    def _pantalla_outcomes(self):
        self._netejar()
        self.root.configure(bg="#e9ecef")

        frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove", padx=30, pady=20)
        frame.pack(pady=30)

        # Títol
        tk.Label(
            frame,
            text="🧾 Crear outcomes RA–CE des de JSON",
            font=("Helvetica", 14, "bold"),
            bg="#ffffff",
            fg="#007c91"
        ).pack(pady=(0, 15))

        # Fitxer JSON
        tk.Label(
            frame,
            text="Selecciona el fitxer JSON d’outcomes:",
            font=("Helvetica", 10),
            bg="#ffffff"
        ).pack(pady=(0, 5))

        file_frame = tk.Frame(frame, bg="#ffffff")
        file_frame.pack(pady=(0, 10))

        self.entry_json = tk.Entry(file_frame, width=50)
        self.entry_json.pack(side=tk.LEFT, padx=(0, 5))

        b_sel = tk.Button(
            file_frame,
            text="📂 Seleccionar…",
            bg="#6c757d",
            fg="white",
            command=self._triar_json
        )
        self._add_hover(b_sel, "#6c757d", "#5a6268")
        b_sel.pack(side=tk.LEFT)

        # Escala
        tk.Label(
            frame,
            text="Nom (o part) de l’escala a utilitzar:",
            font=("Helvetica", 10),
            bg="#ffffff"
        ).pack(pady=(10, 5))

        self.entry_escala = tk.Entry(frame, width=60)
        self.entry_escala.insert(0, "Escala 0-10")
        self.entry_escala.pack(pady=5)

        # Botons
        btn_frame = tk.Frame(frame, bg="#ffffff")
        btn_frame.pack(pady=(15, 10))

        b_create = tk.Button(
            btn_frame,
            text="🚀 Crear outcomes",
            bg="#9C27B0",
            fg="white",
            command=self._executar_outcomes
        )
        self._add_hover(b_create, "#9C27B0", "#8e24aa")
        b_create.pack(side=tk.LEFT, padx=5)

        b_back = tk.Button(
            btn_frame,
            text="⬅️ Tornar al menú",
            bg="#f1f3f5",
            fg="#333",
            command=self._pantalla_menu
        )
        self._add_hover(b_back)
        b_back.pack(side=tk.LEFT, padx=5)

        # Log d’eixida
        output_frame = tk.Frame(frame, bg="#ffffff")
        output_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.output = ScrolledText(output_frame, width=90, height=18, wrap="word")
        self.output.pack(fill="both", expand=True, padx=10, pady=10)
        self._config_tags()

        # Barra de progrés real
        self.progress = ttk.Progressbar(frame, length=350, mode="determinate")
        self.progress.pack(pady=10)

    # ------------------------------------------------------------
    # FUNCIONS AUXILIARS
    # ------------------------------------------------------------
    def _config_tags(self):
        self.output.tag_config("error", foreground="#d32f2f")
        self.output.tag_config("warning", foreground="#ff9800")
        self.output.tag_config("success", foreground="#388e3c")
        self.output.tag_config("info", foreground="#1976d2")

    def _triar_csv(self):
        fitxer = filedialog.askopenfilename(title="Selecciona fitxer CSV", filetypes=[("Arxius CSV", "*.csv")])
        if fitxer:
            self.entry_csv.delete(0, tk.END)
            self.entry_csv.insert(0, fitxer)

    def _triar_json(self):
        fitxer = filedialog.askopenfilename(title="Selecciona fitxer JSON", filetypes=[("Arxius JSON", "*.json")])
        if fitxer:
            self.entry_json.delete(0, tk.END)
            self.entry_json.insert(0, fitxer)

    def _executar_importacio(self):
        fitxer = self.entry_csv.get().strip()
        if not fitxer:
            messagebox.showwarning("Atenció", "Has de seleccionar un fitxer CSV.")
            return

        self.output.delete("1.0", tk.END)
        threading.Thread(target=self._importar_worker, args=(fitxer,), daemon=True).start()

    def _importar_worker(self, fitxer):
        self.progress = ttk.Progressbar(self.root, length=300, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start(10)
        importar_escalas_des_de_csv(self.session, self.cookie, self.base_url, self.sesskey, self.course_id, fitxer, self.output)
        self.progress.stop()

    def _executar_outcomes(self):
        import json
        import threading
        from .aules_api import obtenir_escalas_existents, obtenir_categories_existents, crear_categoria_ra, crear_outcome

        fitxer_json = self.entry_json.get().strip()
        escala_nom = self.entry_escala.get().strip()

        if not fitxer_json:
            messagebox.showwarning("Atenció", "Selecciona un fitxer JSON.")
            return

        # Carregar JSON i comptar outcomes CE
        try:
            with open(fitxer_json, encoding="utf-8") as f:
                data = json.load(f)
            total = sum(len(ra["criterios"]) for ra in data.get("resultados", []))
        except Exception as e:
            messagebox.showerror("Error", f"Error llegint JSON: {e}")
            return

        if total == 0:
            messagebox.showwarning("Atenció", "El JSON no conté criteris CE.")
            return

        # Netejar log
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"📁 Fitxer: {fitxer_json}\n")
        self.output.insert(tk.END, f"🔢 Total d'outcomes CE: {total}\n\n")
        self.output.update_idletasks()

        # Configurar barra real
        self.progress["value"] = 0
        self.progress["maximum"] = total

        def progress_callback():
            """Incrementa la barra 1 pas."""
            self.progress["value"] += 1
            self.progress.update_idletasks()

        def worker():
            try:
                # Obtenir escales existents
                escalas = obtenir_escalas_existents(self.session, self.cookie, self.base_url, self.course_id, self.output)
                if not escalas:
                    self.output.insert(tk.END, "❌ No s'han pogut obtenir les escales.\n", "error")
                    return

                # Trobar l'escala especificada
                escala_id = None
                for nom, eid in escalas.items():
                    if escala_nom.lower() in nom.lower():
                        escala_id = eid
                        self.output.insert(tk.END, f"✅ Escala trobada: {nom} (ID {eid})\n")
                        break
                
                if not escala_id:
                    self.output.insert(tk.END, f"❌ No s'ha trobat cap escala amb el nom '{escala_nom}'.\n", "error")
                    return

                # Obtenir categories existents
                categories_existents = obtenir_categories_existents(self.session, self.cookie, self.base_url, self.course_id, self.output)
                
                # Processar cada RA del JSON
                for cat in data.get("resultados", []):
                    ra_full = cat["nombre"].strip()
                    
                    # Verificar si la categoria existeix
                    categoria_existeix = any(ra_full.lower() == c.lower() for c in categories_existents)
                    
                    if categoria_existeix:
                        self.output.insert(tk.END, f"✓ Categoria '{ra_full}' ja existeix.\n")
                    else:
                        # Crear la categoria RA
                        if crear_categoria_ra(self.session, self.cookie, self.base_url, self.sesskey, self.course_id, ra_full, self.output):
                            categories_existents.add(ra_full)
                        else:
                            self.output.insert(tk.END, f"⚠️ Saltant outcomes per a '{ra_full}' per error en crear categoria\n", "warning")
                            continue

                        # Crear els outcomes (CE) d'aquest RA
                        criteris = cat.get("criterios", [])

                        for elem in criteris:
                            nom = elem["nombre"]
                            
                            # ⚠️ COMPATIBILITAT COMPLETA: CE5.b, RA5.b, R5.b, CE5-b, RA5-b, etc.
                            # Patterns acceptats:
                            # - CE5.b, CE5-b, CE5b
                            # - RA5.b, RA5-b, RA5b  
                            # - R5.b, R5-b, R5b
                            patterns = [
                                r"(CE|RA|R)(\d+)[\.\-]?(\w+)",  # CE5.b, RA5-b, R5.b
                                r"(CE|RA|R)(\d+)(\w+)"          # CE5b, RA5b, R5b
                            ]
                            
                            match = None
                            for pattern in patterns:
                                match = re.match(pattern, nom.strip())
                                if match:
                                    break
                            
                            if not match:
                                self.output.insert(tk.END, f"⚠️ Format de nom incorrecte: {nom}\n", "warning")
                                continue
                                
                            # Processar el match
                            if len(match.groups()) == 3:
                                tipus, numero, lletra = match.groups()
                            else:
                                # Si el pattern no captura correctament, intentar extraure manualment
                                tipus = re.search(r'(CE|RA|R)', nom)
                                if tipus:
                                    tipus = tipus.group(1)
                                    # Extreure número i lletra
                                    rest = nom[len(tipus):]
                                    nums = re.search(r'(\d+)', rest)
                                    lets = re.search(r'[\.\-]?([a-zA-Z])', rest)
                                    if nums and lets:
                                        numero, lletra = nums.group(1), lets.group(1)
                                    else:
                                        self.output.insert(tk.END, f"⚠️ No s'ha pogut extreure número/lletra de: {nom}\n", "warning")
                                        continue
                                else:
                                    self.output.insert(tk.END, f"⚠️ Format desconegut: {nom}\n", "warning")
                                    continue
                            
                            # Normalitzar a format RA (Resultat Aprenentatge)
                            short = f"RA{numero}.{lletra.lower()}"
                            
                            # Extreure descripció completa
                            if ":" in nom:
                                desc = nom.split(":", 1)[-1].strip()
                            else:
                                # Si no hi ha dos punts, buscar després del patró
                                desc_match = re.search(r'(CE|RA|R)\d+[\.\-]?\w+\s*[:-]?\s*(.+)', nom)
                                desc = desc_match.group(2).strip() if desc_match else nom
                            
                            full = f"{short}: {desc}"
                            
                            # Debug info (opcional)
                            self.output.insert(tk.END, f"   🔍 Processant: '{nom}' → '{short}'\n")
                            
                            # Crear outcome
                            crear_outcome(
                                session=self.session, 
                                cookie=self.cookie, 
                                base_url=self.base_url, 
                                sesskey=self.sesskey, 
                                course_id=self.course_id,
                                shortname=short, 
                                fullname=full, 
                                scaleid=escala_id,
                                output=self.output
                            )
                            
                            # Incrementar barra de progrés
                            progress_callback()

                self.output.insert(tk.END, "\n✅ Procés completat correctament!\n", "success")
                
            except Exception as e:
                self.output.insert(tk.END, f"❌ Error durant el procés: {e}\n", "error")

        threading.Thread(target=worker, daemon=True).start()

    def _outcomes_worker(self, fitxer_json, escala_nom):
        count = 0

        def _increment():
            nonlocal count
            count += 1
            self.progress["value"] = count
            self.progress.update_idletasks()

        # Passar funció increment al core
        crear_outcomes_des_de_json(
            self.session,
            self.cookie,
            self.base_url,
            self.sesskey,
            self.course_id,
            fitxer_json,
            escala_nom,
            self.output,
            progress_callback=_increment
        )

        self.output.insert(tk.END, "\n✔ Operació finalitzada!\n", "success")


