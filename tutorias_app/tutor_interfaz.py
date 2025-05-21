
import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar

class InterfazTutor:
    def __init__(self, root, id_tutor,ventana_login):
        self.root = root
        self.id_tutor = id_tutor
        self.ventana_login = ventana_login 
        self.root.title(f"Tutor - Gestión de Solicitudes (ID: {id_tutor})")
        self.root.geometry("1000x400")
        self.root.configure(bg="#f0f0f0")

        # ===== Frame superior para búsqueda =====
        frame_busqueda = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        frame_busqueda.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_busqueda, text="Área de Conocimiento:", bg="#ffffff", font=("Arial", 11)).pack(side="left", padx=5, pady=10)

        self.area_var = tk.StringVar()
        self.combo_areas = ttk.Combobox(frame_busqueda, textvariable=self.area_var, state="readonly", width=30)
        self.combo_areas.pack(side="left", padx=5)

        tk.Label(frame_busqueda, text="Estado:", bg="#ffffff", font=("Arial", 11)).pack(side="left", padx=5, pady=10)

        self.estado_var = tk.StringVar()
        self.combo_estados = ttk.Combobox(frame_busqueda, textvariable=self.estado_var, state="readonly", width=20)
        self.combo_estados["values"] = ["Pendiente", "Aceptada", "Rechazada"]
        self.combo_estados.pack(side="left", padx=5)

        tk.Button(frame_busqueda, text=" Cargar Áreas", command=self.cargar_areas, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_busqueda, text=" Filtrar", command=self.filtrar_solicitudes, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_busqueda, text=" Limpiar Filtros", command=self.limpiar_filtros, bg="#9e9e9e", fg="white").pack(side="left", padx=5)

        # ===== Frame para Treeview con Scrollbars =====
        frame_tree = tk.Frame(root)
        frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(frame_tree, columns=("ID", "Estudiante", "Área", "Fecha", "Estado"),
                                show="headings", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        for col in ("ID", "Estudiante", "Área", "Fecha", "Estado"):
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=100)  # Ajusta el ancho si es necesario

        self.tree.pack(fill="both", expand=True)

        # Configuración del scrollbar
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        
        # ===== Botones para aceptar/rechazar =====
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Aceptar Solicitud", command=self.aceptar_solicitud, bg="#4caf50", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Rechazar Solicitud", command=self.rechazar_solicitud, bg="#f44336", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Marcar como Completada", command=self.completar_solicitud, bg="#ff9800", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#607d8b", fg="white").pack(side="left", padx=10)

        # ===== Cargar datos iniciales =====
        self.cargar_areas()
        self.cargar_solicitudes()

    def cargar_areas(self):
        conexion = conectar()
        cursor = conexion.cursor()
        query = """
            SELECT DISTINCT a.nombre_area
            FROM areas_conocimiento a
            JOIN tutores_areas ta ON a.id_area = ta.id_area
            WHERE ta.id_tutor = %s
        """
        cursor.execute(query, (self.id_tutor,))
        areas = [fila[0] for fila in cursor.fetchall()]
        conexion.close()
        self.combo_areas["values"] = areas

    def cargar_solicitudes(self):
        conexion = conectar()
        cursor = conexion.cursor()
        query = """
            SELECT s.id_solicitud, e.nombre, a.nombre_area, s.fecha, s.estado
            FROM solicitudes s
            JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
            JOIN areas_conocimiento a ON s.id_area = a.id_area
            WHERE s.id_tutor = %s

        """
        cursor.execute(query, (self.id_tutor,))
        resultados = cursor.fetchall()
        conexion.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for fila in resultados:
            self.tree.insert("", "end", values=fila)



    def filtrar_solicitudes(self):
        area = self.area_var.get()
        estado = self.estado_var.get()

        conexion = conectar()
        cursor = conexion.cursor()
        query = """
            SELECT s.id_solicitud, e.nombre, a.nombre_area, s.fecha, s.estado
            FROM solicitudes s
            JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
            JOIN areas_conocimiento a ON s.id_area = a.id_area
            WHERE s.id_tutor = %s
        """
        params = [self.id_tutor]

        if area:
            query += " AND a.nombre_area = %s"
            params.append(area)

        if estado:
            query += " AND s.estado = %s"
            params.append(estado)

        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conexion.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for fila in resultados:
            self.tree.insert("", "end", values=fila)

    def limpiar_filtros(self):
        self.area_var.set("")  # Limpiar selección del combo
        self.estado_var.set("")  # Si tienes estado también
        self.cargar_solicitudes()  # Recargar todo sin filtros


    def aceptar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud.")
            return

        item = self.tree.item(seleccionado)
        id_solicitud = item["values"][0]
        estado_actual = item["values"][4]

        if estado_actual == "Completada":
            messagebox.showwarning("Advertencia", "No se puede aceptar una solicitud que ya fue completada.")
            return
        if estado_actual == "Rechazada":
            messagebox.showwarning("Advertencia", "No se puede aceptar una solicitud que ya fue rechazada.")
            return
        if estado_actual == "Aceptada":
            messagebox.showinfo("Información", "La solicitud ya fue aceptada.")
            return
        
        
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE solicitudes SET estado = 'Aceptada' WHERE id_solicitud = %s", (id_solicitud,))
        conexion.commit()
        conexion.close()
        self.filtrar_solicitudes()
        messagebox.showinfo("Éxito", "Solicitud aceptada.")


    def rechazar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud.")
            return

        item = self.tree.item(seleccionado)
        id_solicitud = item["values"][0]
        estado_actual = item["values"][4]

        if estado_actual == "Rechazada":
            messagebox.showinfo("Información", "La solicitud ya fue rechazada.")
            return
    
        elif estado_actual == "Completada":
            messagebox.showwarning("Advertencia", "No se puede rechazar una solicitud que ya fue completada.")
            return


        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE solicitudes SET estado = 'Rechazada' WHERE id_solicitud = %s", (id_solicitud,))
        conexion.commit()
        conexion.close()
        self.filtrar_solicitudes()
        messagebox.showinfo("Éxito", "Solicitud rechazada.")


    def completar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud.")
            return

        item = self.tree.item(seleccionado)
        id_solicitud = item["values"][0]
        estado_actual = item["values"][4]


        if estado_actual == "Completada":
            messagebox.showinfo("Información", "La solicitud ya fue completada.")
            return
        elif estado_actual != "Aceptada":
            messagebox.showwarning("Advertencia", "Solo puede completar solicitudes que ya fueron aceptadas.")
            return
        
        

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE solicitudes SET estado = 'Completada' WHERE id_solicitud = %s", (id_solicitud,))
        conexion.commit()
        conexion.close()
        self.filtrar_solicitudes()
        messagebox.showinfo("Éxito", "Solicitud marcada como completada.")


    def cerrar_sesion(self):
        self.root.destroy()  # cerrar ventana tutor
        self.ventana_login.deiconify()  # mostrar ventana login