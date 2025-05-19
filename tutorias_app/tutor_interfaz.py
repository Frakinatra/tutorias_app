import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from conexion import conectar
import mysql.connector

class InterfazTutor:
    def __init__(self, root, id_tutor):
        self.root = root
        self.id_tutor = id_tutor
        self.root.title(f"📚 Tutor - Gestión de Solicitudes (ID: {id_tutor})")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Configuración inicial
        self.configurar_estilos()
        self.crear_widgets()
        
        # Cargar datos iniciales
        self.cargar_areas()
        self.cargar_solicitudes()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6, 
                       background="#2c3e50", foreground="white", relief="flat")
        style.map("TButton", background=[("active", "#34495e")])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                       background="#34495e", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, 
                       background="white", fieldbackground="white")

    def crear_widgets(self):
        # Frame de búsqueda
        frame_busqueda = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove")
        frame_busqueda.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_busqueda, text="Área de Conocimiento:", bg="#ffffff", 
                font=("Segoe UI", 11)).pack(side="left", padx=5, pady=10)

        self.area_var = tk.StringVar()
        self.combo_areas = ttk.Combobox(frame_busqueda, textvariable=self.area_var, 
                                      state="readonly", width=30)
        self.combo_areas.pack(side="left", padx=5)

        tk.Label(frame_busqueda, text="Estado:", bg="#ffffff", 
                font=("Segoe UI", 11)).pack(side="left", padx=5, pady=10)

        self.estado_var = tk.StringVar()
        self.combo_estados = ttk.Combobox(frame_busqueda, textvariable=self.estado_var, 
                                        state="readonly", width=20)
        self.combo_estados["values"] = ["Todos", "Pendiente", "Aceptada", "Rechazada", "Completada", "Cancelada"]
        self.combo_estados.current(0)
        self.combo_estados.pack(side="left", padx=5)

        ttk.Button(frame_busqueda, text="🔄 Cargar Áreas", command=self.cargar_areas).pack(side="left", padx=5)
        ttk.Button(frame_busqueda, text="🔍 Filtrar", command=self.filtrar_solicitudes).pack(side="left", padx=5)
        ttk.Button(frame_busqueda, text="🧹 Limpiar", command=self.limpiar_filtros).pack(side="left", padx=5)

        # Treeview para solicitudes
        frame_tree = tk.Frame(self.root, bg="#f0f0f0")
        frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("ID", "Estudiante", "Área", "Fecha", "Estado", "Detalles", "Urgencia")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        col_widths = [50, 150, 150, 120, 100, 200, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame para botones de acción
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="👁️ Ver Detalles", command=self.ver_detalles).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✅ Aceptar", command=self.aceptar_solicitud).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Rechazar", command=self.rechazar_solicitud).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✔️ Completar", command=self.completar_solicitud).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📝 Agregar Notas", command=self.agregar_notas).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗓️ Programar Sesión", command=self.programar_sesion).pack(side="left", padx=5)

    def cargar_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            query = """
                SELECT DISTINCT a.id_area, a.nombre_area
                FROM areas_conocimiento a
                JOIN tutores_areas ta ON a.id_area = ta.id_area
                WHERE ta.id_tutor = %s
                ORDER BY a.nombre_area
            """
            cursor.execute(query, (self.id_tutor,))
            areas = cursor.fetchall()
            
            if not areas:
                messagebox.showwarning("Advertencia", "No tienes áreas asignadas.")
                return
            
            self.combo_areas['values'] = [area['nombre_area'] for area in areas]
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def cargar_solicitudes(self, area=None, estado=None):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.id_solicitud, 
                    CONCAT(e.nombres, ' ', e.apellido_paterno) AS estudiante,
                    a.nombre_area, 
                    s.fecha, 
                    s.estado,
                    IFNULL(s.detalles, '') AS detalles,
                    s.urgencia
                FROM solicitudes s
                JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
                JOIN areas_conocimiento a ON s.id_area = a.id_area
                WHERE (s.id_tutor = %s OR s.id_tutor IS NULL)
                AND a.id_area IN (
                    SELECT ta.id_area 
                    FROM tutores_areas ta 
                    WHERE ta.id_tutor = %s
                )
            """
            params = [self.id_tutor, self.id_tutor]
            
            if area and area != "Todos":
                query += " AND a.nombre_area = %s"
                params.append(area)
                
            if estado and estado != "Todos":
                query += " AND s.estado = %s"
                params.append(estado)
                
            query += " ORDER BY s.fecha DESC"
            
            cursor.execute(query, params)
            solicitudes = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            if not solicitudes:
                messagebox.showinfo("Información", "No hay solicitudes con los criterios seleccionados.")
                return
                
            for solicitud in solicitudes:
                self.tree.insert("", "end", values=(
                    solicitud['id_solicitud'],
                    solicitud['estudiante'],
                    solicitud['nombre_area'],
                    solicitud['fecha'].strftime('%Y-%m-%d %H:%M'),
                    solicitud['estado'],
                    solicitud['detalles'],
                    solicitud['urgencia'].capitalize() if solicitud['urgencia'] else "Media"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las solicitudes: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def filtrar_solicitudes(self):
        area = self.area_var.get()
        estado = self.estado_var.get() if self.estado_var.get() != "Todos" else None
        self.cargar_solicitudes(area, estado)

    def limpiar_filtros(self):
        self.area_var.set('')
        self.estado_var.set('Todos')
        self.cargar_solicitudes()

    def obtener_solicitud_seleccionada(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona una solicitud primero.")
            return None
            
        item = self.tree.item(seleccionado[0])
        return {
            'id_solicitud': item['values'][0],
            'estudiante': item['values'][1],
            'area': item['values'][2],
            'fecha': item['values'][3],
            'estado': item['values'][4],
            'detalles': item['values'][5],
            'urgencia': item['values'][6]
        }

    def ver_detalles(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        detalles = (
            f"ID: {solicitud['id_solicitud']}\n"
            f"Estudiante: {solicitud['estudiante']}\n"
            f"Área: {solicitud['area']}\n"
            f"Fecha: {solicitud['fecha']}\n"
            f"Estado: {solicitud['estado']}\n"
            f"Urgencia: {solicitud['urgencia']}\n"
            f"Detalles: {solicitud['detalles'] if solicitud['detalles'] else 'No hay detalles adicionales'}"
        )
        messagebox.showinfo("Detalles de Solicitud", detalles)

    def aceptar_solicitud(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        if solicitud['estado'] != 'Pendiente':
            messagebox.showwarning("Advertencia", "Solo puedes aceptar solicitudes en estado 'Pendiente'.")
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Actualizar estado y asignar tutor
            cursor.execute("""
                UPDATE solicitudes 
                SET estado = 'Aceptada', id_tutor = %s 
                WHERE id_solicitud = %s
            """, (self.id_tutor, solicitud['id_solicitud']))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Solicitud aceptada correctamente.")
            self.filtrar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aceptar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def rechazar_solicitud(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        if solicitud['estado'] != 'Pendiente':
            messagebox.showwarning("Advertencia", "Solo puedes rechazar solicitudes en estado 'Pendiente'.")
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Actualizar estado
            cursor.execute("""
                UPDATE solicitudes 
                SET estado = 'Rechazada' 
                WHERE id_solicitud = %s
            """, (solicitud['id_solicitud'],))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Solicitud rechazada correctamente.")
            self.filtrar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo rechazar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def completar_solicitud(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        if solicitud['estado'] != 'Aceptada':
            messagebox.showwarning("Advertencia", "Solo puedes completar solicitudes en estado 'Aceptada'.")
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener información de la solicitud
            cursor.execute("""
                SELECT id_estudiante, id_area 
                FROM solicitudes 
                WHERE id_solicitud = %s
            """, (solicitud['id_solicitud'],))
            info_solicitud = cursor.fetchone()
            
            if not info_solicitud:
                messagebox.showerror("Error", "No se encontró la información de la solicitud.")
                return
            
            # Actualizar estado de la solicitud
            cursor.execute("""
                UPDATE solicitudes 
                SET estado = 'Completada' 
                WHERE id_solicitud = %s
            """, (solicitud['id_solicitud'],))
            
            # Insertar en tabla de sesiones
            cursor.execute("""
                INSERT INTO sesiones (
                    id_solicitud, 
                    id_estudiante, 
                    id_tutor, 
                    id_area, 
                    fecha_hora, 
                    estado
                ) VALUES (%s, %s, %s, %s, NOW(), 'Realizada')
            """, (
                solicitud['id_solicitud'],
                info_solicitud['id_estudiante'],
                self.id_tutor,
                info_solicitud['id_area']
            ))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Solicitud marcada como completada y registrada en sesiones.")
            self.filtrar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def agregar_notas(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        notas = simpledialog.askstring(
            "Agregar Notas", 
            "Ingresa las notas de la tutoría:",
            initialvalue=solicitud['detalles'] if solicitud['detalles'] else ""
        )
        
        if notas is None:  # Usuario canceló
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            cursor.execute("""
                UPDATE solicitudes 
                SET detalles = %s 
                WHERE id_solicitud = %s
            """, (notas, solicitud['id_solicitud']))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Notas agregadas correctamente.")
            self.cargar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron agregar las notas: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def programar_sesion(self):
        solicitud = self.obtener_solicitud_seleccionada()
        if not solicitud:
            return
            
        if solicitud['estado'] != 'Aceptada':
            messagebox.showwarning("Advertencia", "Solo puedes programar sesiones para solicitudes en estado 'Aceptada'.")
            return
            
        try:
            # Obtener disponibilidad del tutor
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT dia_semana, hora_inicio, hora_fin 
                FROM disponibilidad_tutores 
                WHERE id_tutor = %s
            """, (self.id_tutor,))
            disponibilidad = cursor.fetchall()
            
            if not disponibilidad:
                messagebox.showwarning("Advertencia", "No tienes horarios de disponibilidad configurados.")
                conexion.close()
                return
            
            # Crear mensaje de disponibilidad
            mensaje_disponibilidad = "Tu disponibilidad:\n"
            for d in disponibilidad:
                mensaje_disponibilidad += f"{d['dia_semana']}: {d['hora_inicio']} - {d['hora_fin']}\n"
            
            # Mostrar diálogo para seleccionar fecha y hora
            fecha_hora = simpledialog.askstring(
                "Programar Sesión",
                "Ingresa fecha y hora para la sesión (YYYY-MM-DD HH:MM):\n\n" + mensaje_disponibilidad
            )
            
            if not fecha_hora:
                conexion.close()
                return
                
            # Validar formato de fecha
            try:
                fecha_hora_dt = datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Usa YYYY-MM-DD HH:MM")
                conexion.close()
                return
                
            # Verificar si la fecha programada está dentro de la disponibilidad del tutor
            dia_semana = fecha_hora_dt.strftime('%A')
            hora = fecha_hora_dt.time()
            
            disponible = False
            for d in disponibilidad:
                if d['dia_semana'].lower() == dia_semana.lower():
                    if d['hora_inicio'] <= hora <= d['hora_fin']:
                        disponible = True
                        break
            
            if not disponible:
                messagebox.showwarning("Advertencia", "La fecha/hora seleccionada no está dentro de tu horario de disponibilidad.")
                conexion.close()
                return
                
            # Obtener información de la solicitud
            cursor.execute("""
                SELECT id_estudiante, id_area 
                FROM solicitudes 
                WHERE id_solicitud = %s
            """, (solicitud['id_solicitud'],))
            info_solicitud = cursor.fetchone()
            
            if not info_solicitud:
                messagebox.showerror("Error", "No se pudo obtener información de la solicitud.")
                conexion.close()
                return
            
            # Insertar sesión programada
            cursor.execute("""
                INSERT INTO sesiones (
                    id_solicitud,
                    id_estudiante,
                    id_tutor,
                    id_area,
                    fecha_hora,
                    estado,
                    duracion_minutos,
                    detalles
                ) VALUES (%s, %s, %s, %s, %s, 'Programada', 60, %s)
            """, (
                solicitud['id_solicitud'],
                info_solicitud['id_estudiante'],
                self.id_tutor,
                info_solicitud['id_area'],
                fecha_hora_dt,
                f"Sesión programada para {fecha_hora}"
            ))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Sesión programada correctamente.")
            self.filtrar_solicitudes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo programar la sesión: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
if __name__ == '__main__':
    root = tk.Tk()
    app = InterfazTutor(root) 
    root.mainloop()