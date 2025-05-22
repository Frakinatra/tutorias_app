import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from conexion import conectar

class GestionSesiones:
    def __init__(self, root):
        self.root = root
        self.root.title("📆 Gestión de Sesiones de Tutoría")
        self.root.geometry("1200x600")
        self.root.configure(bg="#f0f0f0")
        
        self.centrar_ventana(1200, 600)
        self.crear_widgets()
        self.cargar_sesiones()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_widgets(self):
        # Frame de filtros
        frame_filtros = tk.Frame(self.root, bg="#f0f0f0")
        frame_filtros.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_filtros, text="Filtrar por:", bg="#f0f0f0").pack(side="left", padx=5)

        # Filtro por estado
        tk.Label(frame_filtros, text="Estado:", bg="#f0f0f0").pack(side="left", padx=5)
        self.estado_var = tk.StringVar()
        estados = ["Todas", "Programada", "Realizada", "Cancelada", "No asistió"]
        self.combo_estado = ttk.Combobox(frame_filtros, textvariable=self.estado_var, values=estados, state="readonly")
        self.combo_estado.current(0)
        self.combo_estado.pack(side="left", padx=5)

        # Filtro por fecha
        tk.Label(frame_filtros, text="Fecha desde:", bg="#f0f0f0").pack(side="left", padx=5)
        self.fecha_desde = tk.Entry(frame_filtros, width=10)
        self.fecha_desde.pack(side="left", padx=5)
        
        tk.Label(frame_filtros, text="hasta:", bg="#f0f0f0").pack(side="left", padx=5)
        self.fecha_hasta = tk.Entry(frame_filtros, width=10)
        self.fecha_hasta.pack(side="left", padx=5)

        # Botones de acción
        tk.Button(frame_filtros, text="Filtrar", command=self.filtrar_sesiones, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Limpiar", command=self.limpiar_filtros, bg="#9e9e9e", fg="white").pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Nueva Sesión", command=self.crear_sesion, bg="#4caf50", fg="white").pack(side="left", padx=5)

        # Treeview para mostrar sesiones
        frame_tree = tk.Frame(self.root)
        frame_tree.pack(padx=10, pady=5, fill="both", expand=True)

        columns = ("ID", "Estudiante", "Tutor", "Área", "Fecha/Hora", "Duración", "Estado", "Calificación")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
        
        # Configurar columnas
        col_widths = {
            "ID": 50, 
            "Estudiante": 150,
            "Tutor": 150,
            "Área": 120,
            "Fecha/Hora": 150,
            "Duración": 80,
            "Estado": 100,
            "Calificación": 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.pack(fill="both", expand=True)

        # Frame para botones de acción
        frame_acciones = tk.Frame(self.root, bg="#f0f0f0")
        frame_acciones.pack(pady=10)

        tk.Button(frame_acciones, text="Marcar como Realizada", command=self.marcar_realizada, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Cancelar Sesión", command=self.cancelar_sesion, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Registrar No Asistencia", command=self.registrar_no_asistencia, bg="#ff9800", fg="white").pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Agregar Calificación", command=self.agregar_calificacion, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Ver Detalles", command=self.ver_detalles, bg="#607d8b", fg="white").pack(side="left", padx=5)

    def cargar_sesiones(self, filtros=None):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            query = """
                SELECT 
                    s.id_sesion,
                    CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                    CONCAT(t.nombres, ' ', t.apellido_paterno) AS tutor,
                    a.nombre_area AS area,
                    DATE_FORMAT(s.fecha_hora, '%Y-%m-%d %H:%i') AS fecha_hora,
                    s.duracion_minutos,
                    s.estado,
                    s.calificacion
                FROM sesiones s
                JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                JOIN tutores t ON s.id_tutor = t.id_tutor
                JOIN areas_conocimiento a ON s.id_area = a.id_area
            """

            params = []
            where_clauses = []

            if filtros:
                if filtros.get('estado') and filtros['estado'] != "Todas":
                    where_clauses.append("s.estado = %s")
                    params.append(filtros['estado'])

                if filtros.get('fecha_desde'):
                    where_clauses.append("DATE(s.fecha_hora) >= %s")
                    params.append(filtros['fecha_desde'])

                if filtros.get('fecha_hasta'):
                    where_clauses.append("DATE(s.fecha_hora) <= %s")
                    params.append(filtros['fecha_hasta'])

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY s.fecha_hora DESC"
            cursor.execute(query, params)

            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insertar resultados
            for sesion in cursor.fetchall():
                self.tree.insert("", "end", values=(
                    sesion['id_sesion'],
                    sesion['estudiante'],
                    sesion['tutor'],
                    sesion['area'],
                    sesion['fecha_hora'],
                    f"{sesion['duracion_minutos']} min",
                    sesion['estado'],
                    sesion['calificacion'] or "-"
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las sesiones: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def filtrar_sesiones(self):
        estado = self.estado_var.get()
        fecha_desde = self.fecha_desde.get()
        fecha_hasta = self.fecha_hasta.get()

        filtros = {}
        if estado != "Todas":
            filtros['estado'] = estado
        if fecha_desde:
            filtros['fecha_desde'] = fecha_desde
        if fecha_hasta:
            filtros['fecha_hasta'] = fecha_hasta

        self.cargar_sesiones(filtros)

    def limpiar_filtros(self):
        self.estado_var.set("Todas")
        self.fecha_desde.delete(0, tk.END)
        self.fecha_hasta.delete(0, tk.END)
        self.cargar_sesiones()

    def crear_sesion(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nueva Sesión de Tutoría")
        ventana.geometry("500x400")
        ventana.configure(bg="#f0f0f0")

        # Obtener datos necesarios para el formulario
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            # Obtener estudiantes
            cursor.execute("SELECT id_estudiante, CONCAT(nombres, ' ', apellido_paterno) AS nombre FROM estudiantes")
            estudiantes = cursor.fetchall()

            # Obtener tutores
            cursor.execute("""
                SELECT t.id_tutor, CONCAT(t.nombres, ' ', t.apellido_paterno) AS nombre, a.nombre_area AS area
                FROM tutores t
                JOIN tutores_areas ta ON t.id_tutor = ta.id_tutor
                JOIN areas_conocimiento a ON ta.id_area = a.id_area
            """)
            tutores = cursor.fetchall()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {str(e)}")
            ventana.destroy()
            return
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

        if not estudiantes or not tutores:
            messagebox.showwarning("Advertencia", "No hay estudiantes o tutores registrados")
            ventana.destroy()
            return

        # Widgets del formulario
        tk.Label(ventana, text="Estudiante:", bg="#f0f0f0").pack(pady=5)
        self.estudiante_var = tk.StringVar()
        combo_estudiantes = ttk.Combobox(ventana, textvariable=self.estudiante_var, 
                                        values=[f"{e['id_estudiante']} - {e['nombre']}" for e in estudiantes],
                                        state="readonly")
        combo_estudiantes.pack()

        tk.Label(ventana, text="Tutor:", bg="#f0f0f0").pack(pady=5)
        self.tutor_var = tk.StringVar()
        combo_tutores = ttk.Combobox(ventana, textvariable=self.tutor_var, 
                                    values=[f"{t['id_tutor']} - {t['nombre']} ({t['area']})" for t in tutores],
                                    state="readonly")
        combo_tutores.pack()

        tk.Label(ventana, text="Fecha y Hora:", bg="#f0f0f0").pack(pady=5)
        self.fecha_hora_var = tk.StringVar()
        entry_fecha_hora = tk.Entry(ventana, textvariable=self.fecha_hora_var)
        entry_fecha_hora.pack()
        entry_fecha_hora.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

        tk.Label(ventana, text="Duración (minutos):", bg="#f0f0f0").pack(pady=5)
        self.duracion_var = tk.StringVar(value="60")
        entry_duracion = tk.Entry(ventana, textvariable=self.duracion_var)
        entry_duracion.pack()

        tk.Label(ventana, text="Detalles:", bg="#f0f0f0").pack(pady=5)
        self.detalles_text = tk.Text(ventana, height=5, width=50)
        self.detalles_text.pack()

        def guardar_sesion():
            try:
                # Validar y obtener datos
                estudiante_id = int(self.estudiante_var.get().split(" - ")[0])
                tutor_id = int(self.tutor_var.get().split(" - ")[0])
                fecha_hora = datetime.strptime(self.fecha_hora_var.get(), "%Y-%m-%d %H:%M")
                duracion = int(self.duracion_var.get())
                detalles = self.detalles_text.get("1.0", tk.END).strip()

                if duracion <= 0:
                    raise ValueError("La duración debe ser positiva")

                # Obtener el área del tutor
                conexion = conectar()
                cursor = conexion.cursor(dictionary=True)
                
                # Crear una solicitud automáticamente si no existe
                cursor.execute("""
                    INSERT INTO solicitudes (id_estudiante, id_area, fecha, estado)
                    SELECT %s, ta.id_area, NOW(), 'Aceptada'
                    FROM tutores_areas ta
                    WHERE ta.id_tutor = %s
                    LIMIT 1
                """, (estudiante_id, tutor_id))
                id_solicitud = cursor.lastrowid
                
                # Obtener el id_area del tutor
                cursor.execute("""
                    SELECT ta.id_area 
                    FROM tutores_areas ta
                    WHERE ta.id_tutor = %s 
                    LIMIT 1
                """, (tutor_id,))
                area = cursor.fetchone()
                
                if not area:
                    raise Exception("El tutor no tiene áreas asignadas")

                # Insertar sesión
                cursor.execute("""
                    INSERT INTO sesiones (
                        id_solicitud, id_estudiante, id_tutor, id_area, 
                        fecha_hora, duracion_minutos, detalles, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Programada')
                """, (id_solicitud, estudiante_id, tutor_id, area['id_area'], 
                      fecha_hora, duracion, detalles))

                conexion.commit()
                messagebox.showinfo("Éxito", "Sesión programada correctamente")
                ventana.destroy()
                self.cargar_sesiones()

            except ValueError as ve:
                messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo programar la sesión: {str(e)}")
                if 'conexion' in locals() and conexion.is_connected():
                    conexion.rollback()
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    conexion.close()

        tk.Button(ventana, text="Programar Sesión", command=guardar_sesion, 
                 bg="#4caf50", fg="white").pack(pady=10)

    def marcar_realizada(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una sesión")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]
        estado_actual = self.tree.item(seleccionado[0])['values'][6]

        if estado_actual != "Programada":
            messagebox.showwarning("Advertencia", f"No se puede marcar como realizada una sesión en estado: {estado_actual}")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Marcar Sesión como Realizada")
        ventana.geometry("400x300")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="Calificación (1-5):", bg="#f0f0f0").pack(pady=5)
        self.calificacion_var = tk.StringVar()
        combo_calificacion = ttk.Combobox(ventana, textvariable=self.calificacion_var, 
                                         values=[1, 2, 3, 4, 5], state="readonly")
        combo_calificacion.pack()

        tk.Label(ventana, text="Comentarios:", bg="#f0f0f0").pack(pady=5)
        self.comentarios_text = tk.Text(ventana, height=5, width=40)
        self.comentarios_text.pack()

        def guardar_cambios():
            try:
                calificacion = int(self.calificacion_var.get())
                comentarios = self.comentarios_text.get("1.0", tk.END).strip()

                if not 1 <= calificacion <= 5:
                    raise ValueError("La calificación debe estar entre 1 y 5")

                conexion = conectar()
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE sesiones 
                    SET estado = 'Realizada', 
                        calificacion = %s, 
                        comentarios = %s,
                        fecha_hora = NOW()
                    WHERE id_sesion = %s
                """, (calificacion, comentarios, id_sesion))

                # Actualizar calificación promedio del tutor
                cursor.execute("""
                    UPDATE tutores t
                    SET calificacion = (
                        SELECT AVG(s.calificacion) 
                        FROM sesiones s 
                        WHERE s.id_tutor = t.id_tutor AND s.estado = 'Realizada'
                    )
                    WHERE t.id_tutor = (
                        SELECT id_tutor FROM sesiones WHERE id_sesion = %s
                    )
                """, (id_sesion,))

                conexion.commit()
                messagebox.showinfo("Éxito", "Sesión marcada como realizada")
                ventana.destroy()
                self.cargar_sesiones()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    conexion.close()

        tk.Button(ventana, text="Guardar", command=guardar_cambios, 
                 bg="#4caf50", fg="white").pack(pady=10)

    def cancelar_sesion(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una sesión")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]
        estado_actual = self.tree.item(seleccionado[0])['values'][6]

        if estado_actual != "Programada":
            messagebox.showwarning("Advertencia", f"No se puede cancelar una sesión en estado: {estado_actual}")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de cancelar esta sesión?")
        if not confirmacion:
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE sesiones 
                SET estado = 'Cancelada' 
                WHERE id_sesion = %s
            """, (id_sesion,))
            conexion.commit()
            messagebox.showinfo("Éxito", "Sesión cancelada")
            self.cargar_sesiones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cancelar: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def registrar_no_asistencia(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una sesión")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]
        estado_actual = self.tree.item(seleccionado[0])['values'][6]

        if estado_actual != "Programada":
            messagebox.showwarning("Advertencia", f"No se puede registrar no asistencia a una sesión en estado: {estado_actual}")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Registrar como 'No asistió'?")
        if not confirmacion:
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE sesiones 
                SET estado = 'No asistió' 
                WHERE id_sesion = %s
            """, (id_sesion,))
            conexion.commit()
            messagebox.showinfo("Éxito", "No asistencia registrada")
            self.cargar_sesiones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def agregar_calificacion(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una sesión")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]
        estado_actual = self.tree.item(seleccionado[0])['values'][6]

        if estado_actual != "Realizada":
            messagebox.showwarning("Advertencia", "Solo se puede calificar sesiones realizadas")
            return

        calificacion = simpledialog.askinteger("Calificación", "Ingrese calificación (1-5):", 
                                             minvalue=1, maxvalue=5)
        if not calificacion:
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE sesiones 
                SET calificacion = %s 
                WHERE id_sesion = %s
            """, (calificacion, id_sesion))

            # Actualizar calificación promedio del tutor
            cursor.execute("""
                UPDATE tutores t
                SET calificacion = (
                    SELECT AVG(s.calificacion) 
                    FROM sesiones s 
                    WHERE s.id_tutor = t.id_tutor AND s.estado = 'Realizada'
                )
                WHERE t.id_tutor = (
                    SELECT id_tutor FROM sesiones WHERE id_sesion = %s
                )
            """, (id_sesion,))

            conexion.commit()
            messagebox.showinfo("Éxito", "Calificación registrada")
            self.cargar_sesiones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar calificación: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def ver_detalles(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una sesión")
            return

        id_sesion = self.tree.item(seleccionado[0])['values'][0]

        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    s.*,
                    CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                    CONCAT(t.nombres, ' ', t.apellido_paterno) AS tutor,
                    a.nombre_area AS area
                FROM sesiones s
                JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                JOIN tutores t ON s.id_tutor = t.id_tutor
                JOIN areas_conocimiento a ON s.id_area = a.id_area
                WHERE s.id_sesion = %s
            """, (id_sesion,))
            sesion = cursor.fetchone()

            if not sesion:
                messagebox.showerror("Error", "No se encontró la sesión")
                return

            ventana = tk.Toplevel(self.root)
            ventana.title(f"Detalles de Sesión #{id_sesion}")
            ventana.geometry("500x400")
            ventana.configure(bg="#f0f0f0")

            # Mostrar detalles
            frame_detalles = tk.Frame(ventana, bg="#f0f0f0")
            frame_detalles.pack(pady=10, padx=10, fill="both", expand=True)

            detalles = [
                ("ID Sesión:", sesion['id_sesion']),
                ("Estudiante:", sesion['estudiante']),
                ("Tutor:", sesion['tutor']),
                ("Área:", sesion['area']),
                ("Fecha/Hora:", sesion['fecha_hora'].strftime("%Y-%m-%d %H:%M") if sesion['fecha_hora'] else "-"),
                ("Duración:", f"{sesion['duracion_minutos']} minutos"),
                ("Estado:", sesion['estado']),
                ("Calificación:", sesion['calificacion'] or "-"),
                ("Detalles:", sesion['detalles'] or "-"),
                ("Comentarios:", sesion['comentarios'] or "-")
            ]

            for i, (label, value) in enumerate(detalles):
                tk.Label(frame_detalles, text=label, bg="#f0f0f0", anchor="e").grid(row=i, column=0, sticky="e", padx=5, pady=2)
                tk.Label(frame_detalles, text=value, bg="#f0f0f0", anchor="w").grid(row=i, column=1, sticky="w", padx=5, pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()