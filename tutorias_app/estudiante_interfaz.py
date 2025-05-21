import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar
from datetime import datetime

class InterfazEstudiante:
    def __init__(self, root, id_estudiante=None):
        self.root = root
        self.id_estudiante = id_estudiante if id_estudiante is not None else 1
        self.root.title(f"Gestión de Tutorías | Estudiante (ID: {self.id_estudiante})")
        self.root.geometry("650x520")
        self.root.configure(bg="#e9ecef")

        self.centrar_ventana(650, 520)

        # Estilo empresarial
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        font=("Segoe UI", 10),
                        padding=6,
                        background="#2c3e50",
                        foreground="white",
                        relief="flat")
        style.map("TButton",
                background=[("active", "#34495e")])

        style.configure("TLabel",
                        font=("Segoe UI", 11),
                        background="#ffffff",
                        foreground="#2c3e50")

        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"),
                        background="#34495e",
                        foreground="white")

        style.configure("Treeview", 
                        font=("Segoe UI", 10),
                        rowheight=28,
                        background="white",
                        fieldbackground="white")

        # ===== Frame superior para búsqueda =====
        frame_busqueda = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
        frame_busqueda.pack(padx=15, pady=15, fill="x")

        tk.Label(frame_busqueda, text="Área de Conocimiento:", bg="#ffffff", font=("Segoe UI", 11)).pack(side="left", padx=10, pady=10)

        self.area_var = tk.StringVar()
        self.combo_areas = ttk.Combobox(frame_busqueda, textvariable=self.area_var, state="readonly", width=30)
        self.combo_areas.pack(side="left", padx=5)

        ttk.Button(frame_busqueda, text="Cargar Áreas", command=self.cargar_areas).pack(side="left", padx=5)
        ttk.Button(frame_busqueda, text="Buscar Tutores", command=self.buscar_tutores).pack(side="left", padx=5)

        # ===== Frame para TreeView =====
        frame_lista = tk.Frame(root, bg="#e9ecef")
        frame_lista.pack(padx=15, pady=10, fill="both", expand=True)

        columns = ("ID", "Nombre", "Correo")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== Botón de solicitud =====
        frame_botones = tk.Frame(root, bg="#e9ecef")
        frame_botones.pack(padx=10, pady=15)

        ttk.Button(frame_botones, text="📅 Solicitar Tutoría", command=self.solicitar_tutoria).pack(ipadx=10, ipady=5)

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cargar_areas(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre_area FROM areas_conocimiento")
        areas = cursor.fetchall()
        conexion.close()
        self.combo_areas['values'] = [area[0] for area in areas]

    def buscar_tutores(self):
        area = self.area_var.get()
        if not area:
            messagebox.showwarning("Atención", "Selecciona un área de conocimiento.")
            return

        conexion = conectar()
        cursor = conexion.cursor()

        query = """
        SELECT t.id_tutor, t.nombre, t.correo
        FROM tutores t
        JOIN tutores_areas ta ON t.id_tutor = ta.id_tutor
        JOIN areas_conocimiento a ON ta.id_area = a.id_area
        WHERE a.nombre_area = %s
        """
        cursor.execute(query, (area,))
        tutores = cursor.fetchall()
        conexion.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for tutor in tutores:
            self.tree.insert("", "end", values=tutor)

    def solicitar_tutoria(self):
        area = self.area_var.get()
        if not area:
            messagebox.showwarning("Atención", "Selecciona un área de conocimiento.")
            return

        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT id_area FROM areas_conocimiento WHERE nombre_area = %s", (area,))
        resultado = cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", "Área no encontrada.")
            conexion.close()
            return

        id_area = resultado[0]

        insert_query = """
        INSERT INTO solicitudes (id_estudiante, id_area, fecha, estado)
        VALUES (%s, %s, %s, 'Pendiente')
        """
        cursor.execute(insert_query, (self.id_estudiante, id_area, fecha_actual))
        conexion.commit()
        conexion.close()

        messagebox.showinfo("Éxito", "Solicitud de tutoría creada correctamente.")
