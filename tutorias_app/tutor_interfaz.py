import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar

class InterfazTutor:
    def __init__(self, root, id_tutor=None, ventana_login=None):
        self.root = root
        self.id_tutor = id_tutor
        self.ventana_login = ventana_login 
        title = "Tutor - Gestión de Solicitudes" + (f" (ID: {id_tutor})" if id_tutor else " (Vista Administrador)")
        self.root.title(title)
        self.root.geometry("1100x600")
        self.root.configure(bg="#f0f0f0")

        # Frame superior para búsqueda
        frame_busqueda = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        frame_busqueda.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_busqueda, text="Área de Conocimiento:", bg="#ffffff", font=("Arial", 11)).pack(side="left", padx=5, pady=10)

        self.area_var = tk.StringVar()
        self.combo_areas = ttk.Combobox(frame_busqueda, textvariable=self.area_var, state="readonly", width=30)
        self.combo_areas.pack(side="left", padx=5)

        tk.Label(frame_busqueda, text="Estado:", bg="#ffffff", font=("Arial", 11)).pack(side="left", padx=5, pady=10)

        self.estado_var = tk.StringVar()
        self.combo_estados = ttk.Combobox(frame_busqueda, textvariable=self.estado_var, state="readonly", width=20)
        self.combo_estados["values"] = ["Todos", "Pendiente", "Aceptada", "Rechazada", "Completada", "Cancelada"]
        self.combo_estados.current(0)
        self.combo_estados.pack(side="left", padx=5)

        tk.Button(frame_busqueda, text="Cargar Áreas", command=self.cargar_areas, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_busqueda, text="Filtrar", command=self.filtrar_solicitudes, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_busqueda, text="Limpiar Filtros", command=self.limpiar_filtros, bg="#9e9e9e", fg="white").pack(side="left", padx=5)

        # Frame para Treeview
        frame_tree = tk.Frame(root)
        frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Configurar Treeview
        columns = ["ID", "Estudiante", "Área", "Fecha", "Estado"]
        if not id_tutor:
            columns.append("Tutor")
        
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Estudiante", text="Estudiante")
        self.tree.heading("Área", text="Área")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Estado", text="Estado")
        if not id_tutor:
            self.tree.heading("Tutor", text="Tutor")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Estudiante", width=180)
        self.tree.column("Área", width=150)
        self.tree.column("Fecha", width=150)
        self.tree.column("Estado", width=100, anchor="center")
        if not id_tutor:
            self.tree.column("Tutor", width=180)

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")

        scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side="bottom", fill="x")

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(fill="both", expand=True)

        # Frame para botones
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        if id_tutor:
            tk.Button(btn_frame, text="Aceptar Solicitud", command=self.aceptar_solicitud, bg="#4caf50", fg="white").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Rechazar Solicitud", command=self.rechazar_solicitud, bg="#f44336", fg="white").pack(side="left", padx=5)
            tk.Button(btn_frame, text="Marcar como Completada", command=self.completar_solicitud, bg="#ff9800", fg="white").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Actualizar", command=self.cargar_solicitudes, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#607d8b", fg="white").pack(side="left", padx=5)

        # Cargar datos iniciales
        self.cargar_areas()
        self.cargar_solicitudes()

    def cargar_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            if self.id_tutor:
                query = """
                    SELECT DISTINCT a.nombre_area
                    FROM areas_conocimiento a
                    JOIN tutores_areas ta ON a.id_area = ta.id_area
                    WHERE ta.id_tutor = %s
                    ORDER BY a.nombre_area
                """
                cursor.execute(query, (self.id_tutor,))
            else:
                query = "SELECT nombre_area FROM areas_conocimiento ORDER BY nombre_area"
                cursor.execute(query)
            
            self.combo_areas['values'] = [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def cargar_solicitudes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            if self.id_tutor:
                query = """
                    SELECT 
                        s.id_solicitud, 
                        CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                        a.nombre_area AS area,
                        DATE_FORMAT(s.fecha, '%Y-%m-%d %H:%i') AS fecha,
                        s.estado
                    FROM solicitudes s
                    JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    WHERE s.id_tutor = %s
                    ORDER BY s.fecha DESC
                """
                cursor.execute(query, (self.id_tutor,))
            else:
                query = """
                    SELECT 
                        s.id_solicitud,
                        CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                        a.nombre_area AS area,
                        DATE_FORMAT(s.fecha, '%Y-%m-%d %H:%i') AS fecha,
                        s.estado,
                        CONCAT(t.nombres, ' ', t.apellido_paterno) AS tutor
                    FROM solicitudes s
                    JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    LEFT JOIN tutores t ON s.id_tutor = t.id_tutor
                    WHERE s.id_tutor IS NOT NULL
                    ORDER BY s.fecha DESC
                """
                cursor.execute(query)

            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertar resultados
            for row in cursor.fetchall():
                if self.id_tutor:
                    self.tree.insert("", "end", values=(
                        row['id_solicitud'],
                        row['estudiante'],
                        row['area'],
                        row['fecha'],
                        row['estado']
                    ))
                else:
                    self.tree.insert("", "end", values=(
                        row['id_solicitud'],
                        row['estudiante'],
                        row['area'],
                        row['fecha'],
                        row['estado'],
                        row.get('tutor', '')
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las solicitudes: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def filtrar_solicitudes(self):
        try:
            area = self.area_var.get()
            estado = self.estado_var.get() if self.estado_var.get() != "Todos" else None

            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            if self.id_tutor:
                query = """
                    SELECT 
                        s.id_solicitud, 
                        CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                        a.nombre_area AS area,
                        DATE_FORMAT(s.fecha, '%Y-%m-%d %H:%i') AS fecha,
                        s.estado
                    FROM solicitudes s
                    JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    WHERE s.id_tutor = %s
                """
                params = [self.id_tutor]
            else:
                query = """
                    SELECT 
                        s.id_solicitud,
                        CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                        a.nombre_area AS area,
                        DATE_FORMAT(s.fecha, '%Y-%m-%d %H:%i') AS fecha,
                        s.estado,
                        CONCAT(t.nombres, ' ', t.apellido_paterno) AS tutor
                    FROM solicitudes s
                    JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    LEFT JOIN tutores t ON s.id_tutor = t.id_tutor
                    WHERE s.id_tutor IS NOT NULL
                """
                params = []

            # Aplicar filtros
            if area:
                query += " AND a.nombre_area = %s"
                params.append(area)
                
            if estado:
                query += " AND s.estado = %s"
                params.append(estado)
                
            query += " ORDER BY s.fecha DESC"
            
            cursor.execute(query, params)

            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertar resultados
            for row in cursor.fetchall():
                if self.id_tutor:
                    self.tree.insert("", "end", values=(
                        row['id_solicitud'],
                        row['estudiante'],
                        row['area'],
                        row['fecha'],
                        row['estado']
                    ))
                else:
                    self.tree.insert("", "end", values=(
                        row['id_solicitud'],
                        row['estudiante'],
                        row['area'],
                        row['fecha'],
                        row['estado'],
                        row.get('tutor', '')
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron filtrar las solicitudes: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def limpiar_filtros(self):
        self.area_var.set("")
        self.estado_var.set("Todos")
        self.cargar_solicitudes()

    def aceptar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]
        estado_actual = item['values'][4]

        if estado_actual != "Pendiente":
            messagebox.showwarning("Advertencia", f"No se puede aceptar una solicitud en estado: {estado_actual}")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            cursor.execute(
                "UPDATE solicitudes SET estado = 'Aceptada' WHERE id_solicitud = %s",
                (id_solicitud,)
            )
            conexion.commit()
            
            messagebox.showinfo("Éxito", "Solicitud aceptada correctamente")
            self.cargar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aceptar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def rechazar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]
        estado_actual = item['values'][4]

        if estado_actual != "Pendiente":
            messagebox.showwarning("Advertencia", f"No se puede rechazar una solicitud en estado: {estado_actual}")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar Rechazo", 
            "¿Está seguro que desea rechazar esta solicitud?"
        )
        
        if not confirmacion:
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            cursor.execute(
                "UPDATE solicitudes SET estado = 'Rechazada' WHERE id_solicitud = %s",
                (id_solicitud,)
            )
            conexion.commit()
            
            messagebox.showinfo("Éxito", "Solicitud rechazada correctamente")
            self.cargar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo rechazar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def completar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]
        estado_actual = item['values'][4]

        if estado_actual != "Aceptada":
            messagebox.showwarning("Advertencia", f"Solo se pueden completar solicitudes en estado 'Aceptada' (actual: {estado_actual})")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar Completado", 
            "¿Está seguro que desea marcar esta solicitud como completada?"
        )
        
        if not confirmacion:
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            cursor.execute(
                "UPDATE solicitudes SET estado = 'Completada' WHERE id_solicitud = %s",
                (id_solicitud,)
            )
            conexion.commit()
            
            messagebox.showinfo("Éxito", "Solicitud marcada como completada")
            self.cargar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def cerrar_sesion(self):
        self.root.destroy()
        if self.ventana_login:
            self.ventana_login.deiconify()