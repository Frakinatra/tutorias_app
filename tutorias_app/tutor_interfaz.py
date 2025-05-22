import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar
from tkcalendar import DateEntry
from tkinter import Toplevel, Label, Entry, Text, Button
from datetime import datetime

class InterfazTutor:
    def __init__(self, root, id_tutor=None, ventana_login=None):
        self.root = root
        self.id_tutor = id_tutor
        self.ventana_login = ventana_login 
        title = "Tutor - Gestión de Solicitudes" + (f" (ID: {id_tutor})" if id_tutor else " (Vista Administrador)")
        self.root.title(title)
        self.root.geometry("1100x600")
        self.root.configure(bg="#f0f0f0")

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

        frame_tree = tk.Frame(root)
        frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ["ID", "Estudiante", "Área", "Fecha", "Estado"]
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        scroll_y = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Aceptar Solicitud", command=self.aceptar_solicitud, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Rechazar Solicitud", command=self.rechazar_solicitud, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Marcar como Completada", command=self.completar_solicitud, bg="#ff9800", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", command=self.cargar_solicitudes, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Ver Sesiones", command=self.mostrar_sesiones, bg="#795548", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#607d8b", fg="white").pack(side="left", padx=5)

        self.cargar_areas()
        self.cargar_solicitudes()

    def cargar_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            query = """
                SELECT DISTINCT a.nombre_area
                FROM areas_conocimiento a
                JOIN tutores_areas ta ON a.id_area = ta.id_area
                WHERE ta.id_tutor = %s
                ORDER BY a.nombre_area
            """
            cursor.execute(query, (self.id_tutor,))
            self.combo_areas['values'] = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def cargar_solicitudes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT s.id_solicitud, CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                       a.nombre_area AS area, DATE_FORMAT(s.fecha, '%Y-%m-%d %H:%i') AS fecha, s.estado
                FROM solicitudes s
                JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                JOIN areas_conocimiento a ON s.id_area = a.id_area
                JOIN tutores_areas ta ON ta.id_area = a.id_area
                WHERE ta.id_tutor = %s AND (s.id_tutor IS NULL OR s.id_tutor = %s)
                ORDER BY s.fecha DESC
            """
            cursor.execute(query, (self.id_tutor, self.id_tutor))
            self.tree.delete(*self.tree.get_children())
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=(row['id_solicitud'], row['estudiante'], row['area'], row['fecha'], row['estado']))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las solicitudes: {str(e)}")
        finally:
            if conexion.is_connected():
                conexion.close()

    def aceptar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("UPDATE solicitudes SET estado = 'Aceptada', id_tutor = %s WHERE id_solicitud = %s", (self.id_tutor, id_solicitud))
            conexion.commit()

            def agendar():
                ventana = Toplevel(self.root)
                ventana.title("Agendar Sesión")
                ventana.geometry("400x400")

                Label(ventana, text="Fecha:").pack(pady=5)
                date_entry = DateEntry(ventana, width=20)
                date_entry.pack(pady=5)

                Label(ventana, text="Hora (HH:MM):").pack(pady=5)
                hora_entry = Entry(ventana)
                hora_entry.pack(pady=5)

                Label(ventana, text="Detalles:").pack(pady=5)
                detalles_text = Text(ventana, height=5, width=40)
                detalles_text.pack(pady=5)

                def guardar():
                    try:
                        conexion = conectar()
                        cursor = conexion.cursor()
                        fecha_hora = datetime.strptime(f"{date_entry.get_date()} {hora_entry.get()}", "%Y-%m-%d %H:%M")
                        cursor.execute("SELECT id_estudiante, id_area FROM solicitudes WHERE id_solicitud = %s", (id_solicitud,))
                        est, area = cursor.fetchone()
                        cursor.execute("""
                            INSERT INTO sesiones (id_solicitud, id_estudiante, id_tutor, id_area, fecha_hora, detalles)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (id_solicitud, est, self.id_tutor, area, fecha_hora.strftime('%Y-%m-%d %H:%M:%S'), detalles_text.get("1.0", "end").strip()))
                        conexion.commit()
                        messagebox.showinfo("Éxito", "Sesión agendada correctamente")
                        ventana.destroy()
                        self.cargar_solicitudes()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
                        conexion.rollback()
                    finally:
                        if conexion.is_connected():
                            conexion.close()
                Button(ventana, text="Guardar", command=guardar, bg="#4caf50", fg="white").pack(pady=10)

            agendar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aceptar la solicitud: {str(e)}")
            conexion.rollback()
        finally:
            if conexion.is_connected():
                conexion.close()

    def rechazar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("UPDATE solicitudes SET estado = 'Rechazada' WHERE id_solicitud = %s", (id_solicitud,))
            conexion.commit()
            self.cargar_solicitudes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo rechazar la solicitud: {str(e)}")
            conexion.rollback()
        finally:
            if conexion.is_connected():
                conexion.close()

    def completar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        item = self.tree.item(seleccionado[0])
        id_solicitud = item['values'][0]

        ventana = Toplevel(self.root)
        ventana.title("Retroalimentación")
        ventana.geometry("400x300")

        Label(ventana, text="Comentarios:").pack(pady=5)
        comentarios_text = Text(ventana, height=5, width=40)
        comentarios_text.pack(pady=5)

        Label(ventana, text="Calificación (1-5):").pack(pady=5)
        calif_entry = Entry(ventana)
        calif_entry.pack(pady=5)

        def guardar():
            comentarios = comentarios_text.get("1.0", "end").strip()
            try:
                calif = int(calif_entry.get())
                if not (1 <= calif <= 5): raise ValueError
            except:
                messagebox.showerror("Error", "Calificación inválida")
                return

            try:
                conexion = conectar()
                cursor = conexion.cursor()
                cursor.execute("UPDATE solicitudes SET estado = 'Completada' WHERE id_solicitud = %s", (id_solicitud,))
                cursor.execute("UPDATE sesiones SET estado = 'Realizada', calificacion = %s, comentarios = %s WHERE id_solicitud = %s", (calif, comentarios, id_solicitud))
                conexion.commit()
                messagebox.showinfo("Éxito", "Retroalimentación guardada")
                ventana.destroy()
                self.cargar_solicitudes()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                conexion.rollback()
            finally:
                if conexion.is_connected():
                    conexion.close()

        Button(ventana, text="Guardar", command=guardar, bg="#4caf50", fg="white").pack(pady=10)

    def filtrar_solicitudes(self):
        self.cargar_solicitudes()

    def limpiar_filtros(self):
        self.area_var.set("")
        self.estado_var.set("Todos")
        self.cargar_solicitudes()

    def cerrar_sesion(self):
        self.root.destroy()
        if self.ventana_login:
            self.ventana_login.deiconify()
            
    def mostrar_sesiones(self):
        ventana = Toplevel(self.root)
        ventana.title("Mis Sesiones")
        ventana.geometry("900x400")

        columnas = ("ID", "Área", "Fecha y Hora", "Estado", "Duración", "Calificación", "Comentarios")
        tree = ttk.Treeview(ventana, columns=columnas, show="headings")
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        scroll_y = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            if hasattr(self, 'id_estudiante'):  # desde interfaz de estudiante
                cursor.execute("""
                    SELECT s.id_sesion, a.nombre_area, s.fecha_hora, s.estado,
                        s.duracion_minutos, s.calificacion, s.comentarios
                    FROM sesiones s
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    WHERE s.id_estudiante = %s
                    ORDER BY s.fecha_hora DESC
                """, (self.id_estudiante,))
            elif hasattr(self, 'id_tutor'):  # desde interfaz de tutor
                cursor.execute("""
                    SELECT s.id_sesion, a.nombre_area, s.fecha_hora, s.estado,
                        s.duracion_minutos, s.calificacion, s.comentarios
                    FROM sesiones s
                    JOIN areas_conocimiento a ON s.id_area = a.id_area
                    WHERE s.id_tutor = %s
                    ORDER BY s.fecha_hora DESC
                """, (self.id_tutor,))
            else:
                return

            for row in cursor.fetchall():
                tree.insert("", "end", values=(
                    row["id_sesion"],
                    row["nombre_area"],
                    row["fecha_hora"].strftime("%Y-%m-%d %H:%M"),
                    row["estado"],
                    row["duracion_minutos"],
                    row["calificacion"] if row["calificacion"] else "-",
                    row["comentarios"] if row["comentarios"] else "-"
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()