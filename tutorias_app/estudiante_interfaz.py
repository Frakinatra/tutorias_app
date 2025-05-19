import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from conexion import conectar

class InterfazEstudiante:
    def __init__(self, root, id_estudiante=None):
        self.root = root
        self.id_estudiante = id_estudiante if id_estudiante is not None else 1
        self.root.title(f"Gestión de Tutorías | Estudiante (ID: {self.id_estudiante})")
        self.root.geometry("750x600")
        self.root.configure(bg="#e9ecef")
        self.centrar_ventana(750, 600)

        # Configurar estilo
        self.configurar_estilos()
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar datos iniciales
        self.cargar_areas()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6, 
                       background="#2c3e50", foreground="white", relief="flat")
        style.map("TButton", background=[("active", "#34495e")])
        style.configure("TLabel", font=("Segoe UI", 11), background="#ffffff", foreground="#2c3e50")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#34495e", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white", fieldbackground="white")

    def crear_widgets(self):
        # Frame de búsqueda
        frame_busqueda = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        frame_busqueda.pack(padx=15, pady=15, fill="x")

        tk.Label(frame_busqueda, text="Área de Conocimiento:", bg="#ffffff", font=("Segoe UI", 11)).pack(side="left", padx=10, pady=10)

        self.area_var = tk.StringVar()
        self.combo_areas = ttk.Combobox(frame_busqueda, textvariable=self.area_var, state="readonly", width=30)
        self.combo_areas.pack(side="left", padx=5)

        ttk.Button(frame_busqueda, text="Cargar Áreas", command=self.cargar_areas).pack(side="left", padx=5)
        ttk.Button(frame_busqueda, text="Buscar Tutores", command=self.buscar_tutores).pack(side="left", padx=5)

        # Frame para lista de tutores
        frame_lista = tk.Frame(self.root, bg="#e9ecef")
        frame_lista.pack(padx=15, pady=10, fill="both", expand=True)

        columns = ("ID", "Nombre", "Correo", "Especialidad")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100 if col == "ID" else 150)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame para botones
        frame_botones = tk.Frame(self.root, bg="#e9ecef")
        frame_botones.pack(padx=10, pady=15)

        ttk.Button(frame_botones, text="📅 Solicitar Tutoría", command=self.solicitar_tutoria).pack(ipadx=10, ipady=5)
        
        # Frame para historial de solicitudes
        frame_historial = tk.LabelFrame(self.root, text="Mis Solicitudes", bg="#e9ecef")
        frame_historial.pack(padx=15, pady=10, fill="both", expand=True)

        columns_historial = ("ID", "Área", "Fecha", "Estado")
        self.tree_historial = ttk.Treeview(frame_historial, columns=columns_historial, show="headings")
        
        for col in columns_historial:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, anchor="center", width=100 if col == "ID" else 150)
        
        scrollbar_historial = ttk.Scrollbar(frame_historial, orient="vertical", command=self.tree_historial.yview)
        self.tree_historial.configure(yscroll=scrollbar_historial.set)
        self.tree_historial.pack(side="left", fill="both", expand=True)
        scrollbar_historial.pack(side="right", fill="y")

        # Cargar historial
        self.cargar_historial_solicitudes()

    def cargar_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento ORDER BY nombre_area")
            areas = cursor.fetchall()
            
            if not areas:
                messagebox.showinfo("Información", "No hay áreas de conocimiento registradas.")
                return
            
            self.combo_areas['values'] = [area['nombre_area'] for area in areas]
            messagebox.showinfo("Éxito", f"Se cargaron {len(areas)} áreas de conocimiento.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def buscar_tutores(self):
        area = self.area_var.get()
        if not area:
            messagebox.showwarning("Advertencia", "Selecciona un área de conocimiento.")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            query = """
            SELECT t.id_tutor, t.nombre, t.correo, t.especialidad
            FROM tutores t
            JOIN tutores_areas ta ON t.id_tutor = ta.id_tutor
            JOIN areas_conocimiento a ON ta.id_area = a.id_area
            WHERE a.nombre_area = %s
            ORDER BY t.nombre
            """
            cursor.execute(query, (area,))
            tutores = cursor.fetchall()

            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not tutores:
                messagebox.showinfo("Información", "No hay tutores disponibles para esta área.")
                return

            for tutor in tutores:
                self.tree.insert("", "end", values=(
                    tutor['id_tutor'],
                    tutor['nombre'],
                    tutor['correo'],
                    tutor['especialidad']
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tutores: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def cargar_historial_solicitudes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            query = """
            SELECT s.id_solicitud, a.nombre_area, s.fecha, s.estado
            FROM solicitudes s
            JOIN areas_conocimiento a ON s.id_area = a.id_area
            WHERE s.id_estudiante = %s
            ORDER BY s.fecha DESC
            """
            cursor.execute(query, (self.id_estudiante,))
            solicitudes = cursor.fetchall()

            # Limpiar treeview
            for item in self.tree_historial.get_children():
                self.tree_historial.delete(item)

            if not solicitudes:
                return

            for solicitud in solicitudes:
                self.tree_historial.insert("", "end", values=(
                    solicitud['id_solicitud'],
                    solicitud['nombre_area'],
                    solicitud['fecha'].strftime('%Y-%m-%d %H:%M'),
                    solicitud['estado']
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def solicitar_tutoria(self):
        area = self.area_var.get()
        if not area:
            messagebox.showwarning("Advertencia", "Selecciona un área de conocimiento.")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Verificar si ya existe una solicitud pendiente para esta área
            cursor.execute("""
                SELECT COUNT(*) 
                FROM solicitudes 
                WHERE id_estudiante = %s AND id_area = (
                    SELECT id_area FROM areas_conocimiento WHERE nombre_area = %s
                ) AND estado = 'Pendiente'
            """, (self.id_estudiante, area))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Advertencia", "Ya tienes una solicitud pendiente para esta área.")
                return

            # Obtener id_area
            cursor.execute("SELECT id_area FROM areas_conocimiento WHERE nombre_area = %s", (area,))
            resultado = cursor.fetchone()
            
            if not resultado:
                messagebox.showerror("Error", "Área no encontrada.")
                return

            id_area = resultado[0]
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insertar nueva solicitud
            insert_query = """
            INSERT INTO solicitudes (id_estudiante, id_area, fecha, estado)
            VALUES (%s, %s, %s, 'Pendiente')
            """
            cursor.execute(insert_query, (self.id_estudiante, id_area, fecha_actual))
            conexion.commit()

            messagebox.showinfo("Éxito", "Solicitud de tutoría creada correctamente.")
            self.cargar_historial_solicitudes()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la solicitud: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()