import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar

class GestionSesiones:
    def __init__(self, root):
        self.root = root
        self.root.title("📆 Gestión de Sesiones de Tutoría")
        self.root.geometry("800x500")
        self.root.configure(bg="#f0f0f0")

        self.centrar_ventana(800, 500)

        frame_filtros = tk.Frame(root, bg="#f0f0f0")
        frame_filtros.pack(pady=10)

        tk.Label(frame_filtros, text="Filtrar por ID Estudiante:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.filtro_est = tk.Entry(frame_filtros, width=10)
        self.filtro_est.grid(row=0, column=1, padx=5)

        tk.Label(frame_filtros, text="o ID Tutor:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.filtro_tut = tk.Entry(frame_filtros, width=10)
        self.filtro_tut.grid(row=0, column=3, padx=5)

        tk.Button(frame_filtros, text="Buscar", command=self.buscar_sesiones, bg="#2196f3", fg="white").grid(row=0, column=4, padx=5)
        tk.Button(frame_filtros, text="Mostrar Todas", command=self.cargar_sesiones, bg="#4caf50", fg="white").grid(row=0, column=5, padx=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Estudiante", "Tutor", "Área", "Fecha", "Estado"), show="headings")
        for col in ("ID", "Estudiante", "Tutor", "Área", "Fecha", "Estado"):
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10, fill="both", expand=True)

        botones = tk.Frame(root, bg="#f0f0f0")
        botones.pack(pady=5)
        tk.Button(botones, text="Marcar como Completada", command=self.marcar_completada, bg="#ff9800", fg="white").pack(side="left", padx=5)

        self.cargar_sesiones()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cargar_sesiones(self):
        conexion = conectar()
        cursor = conexion.cursor()
        consulta = """
        SELECT s.id_sesion, e.nombre, t.nombre, a.nombre_area, s.fecha_hora, s.estado
        FROM sesiones s
        JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
        JOIN tutores t ON s.id_tutor = t.id_tutor
        JOIN areas_conocimiento a ON s.id_area = a.id_area
        ORDER BY s.fecha_hora DESC
        """
        cursor.execute(consulta)
        rows = cursor.fetchall()
        conexion.close()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def buscar_sesiones(self):
        id_est = self.filtro_est.get()
        id_tut = self.filtro_tut.get()

        if not id_est and not id_tut:
            messagebox.showinfo("Filtro vacío", "Ingresa un ID para buscar.")
            return

        conexion = conectar()
        cursor = conexion.cursor()

        consulta = """
        SELECT s.id_sesion, e.nombre, t.nombre, a.nombre_area, s.fecha_hora, s.estado
        FROM sesiones s
        JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
        JOIN tutores t ON s.id_tutor = t.id_tutor
        JOIN areas_conocimiento a ON s.id_area = a.id_area
        WHERE 1=1
        """
        params = []

        if id_est:
            consulta += " AND s.id_estudiante = %s"
            params.append(id_est)
        if id_tut:
            consulta += " AND s.id_tutor = %s"
            params.append(id_tut)

        consulta += " ORDER BY s.fecha_hora DESC"
        cursor.execute(consulta, params)
        rows = cursor.fetchall()
        conexion.close()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def marcar_completada(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showinfo("Selecciona una sesión", "Selecciona una sesión para marcarla como completada.")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]
        confirmacion = messagebox.askyesno("Confirmar acción", "¿Estás seguro de marcar esta sesión como completada?")
        
        if not confirmacion:
            return

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE sesiones SET estado = 'completada' WHERE id_sesion = %s", (id_sesion,))
        conexion.commit()
        conexion.close()

        self.cargar_sesiones()
        messagebox.showinfo("✅ Sesión completada", "La sesión se marcó como completada.")
