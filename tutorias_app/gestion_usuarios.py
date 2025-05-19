import tkinter as tk
from tkinter import ttk, messagebox
from conexion import conectar

class GestionUsuarios:
    def __init__(self, root):
        self.root = root
        self.root.title("👥 Gestión de Usuarios")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar datos iniciales
        self.cargar_usuarios()

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

        tk.Label(frame_busqueda, text="Tipo de Usuario:", bg="#ffffff", 
                font=("Segoe UI", 11)).pack(side="left", padx=5, pady=5)

        self.tipo_var = tk.StringVar()
        self.combo_tipos = ttk.Combobox(frame_busqueda, textvariable=self.tipo_var, 
                                      state="readonly", width=15)
        self.combo_tipos['values'] = ['Todos', 'Estudiante', 'Tutor', 'Admin']
        self.combo_tipos.current(0)
        self.combo_tipos.pack(side="left", padx=5)

        tk.Label(frame_busqueda, text="Buscar:", bg="#ffffff", 
                font=("Segoe UI", 11)).pack(side="left", padx=5, pady=5)

        self.busqueda_var = tk.StringVar()
        self.entry_busqueda = ttk.Entry(frame_busqueda, textvariable=self.busqueda_var, width=30)
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind('<Return>', lambda event: self.filtrar_usuarios())

        ttk.Button(frame_busqueda, text="🔍 Filtrar", command=self.filtrar_usuarios).pack(side="left", padx=5)
        ttk.Button(frame_busqueda, text="🧹 Limpiar", command=self.limpiar_filtros).pack(side="left", padx=5)

        # Treeview para usuarios
        frame_tree = tk.Frame(self.root, bg="#f0f0f0")
        frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("ID", "Usuario", "Tipo", "Nombre", "Correo", "Detalles")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        col_widths = [50, 150, 100, 150, 200, 200]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame para botones de acción
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="➕ Nuevo Usuario", command=self.nuevo_usuario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Editar", command=self.editar_usuario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Eliminar", command=self.eliminar_usuario).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Actualizar", command=self.cargar_usuarios).pack(side="left", padx=5)

    def cargar_usuarios(self, tipo=None, busqueda=None):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            
            query = """
                SELECT 
                    u.id_usuario, 
                    u.username AS usuario,
                    CASE 
                        WHEN u.username LIKE '%@admin.edu%' THEN 'Admin'
                        WHEN u.username LIKE '%@tutor.edu%' THEN 'Tutor'
                        WHEN u.username LIKE '%@alumno.edu%' THEN 'Estudiante'
                        ELSE 'Desconocido'
                    END AS tipo,
                    COALESCE(e.nombre, t.nombre, 'Administrador') AS nombre,
                    u.username AS correo,
                    CASE 
                        WHEN u.username LIKE '%@alumno.edu%' THEN CONCAT('Carrera: ', e.carrera, ', Semestre: ', e.semestre)
                        WHEN u.username LIKE '%@tutor.edu%' THEN CONCAT('Especialidad: ', t.especialidad)
                        ELSE 'Usuario administrativo'
                    END AS detalles
                FROM usuarios u
                LEFT JOIN estudiantes e ON u.id_relacion = e.id_estudiante AND u.username LIKE '%@alumno.edu%'
                LEFT JOIN tutores t ON u.id_relacion = t.id_tutor AND u.username LIKE '%@tutor.edu%'
            """
            params = []
            
            # Aplicar filtros si existen
            if tipo and tipo != "Todos":
                query += " WHERE u.username LIKE %s"
                if tipo == "Estudiante":
                    params.append("%@alumno.edu%")
                elif tipo == "Tutor":
                    params.append("%@tutor.edu%")
                elif tipo == "Admin":
                    params.append("%@admin.edu%")
                    
            if busqueda:
                if "WHERE" in query:
                    query += " AND (u.username LIKE %s OR e.nombre LIKE %s OR t.nombre LIKE %s)"
                else:
                    query += " WHERE (u.username LIKE %s OR e.nombre LIKE %s OR t.nombre LIKE %s)"
                params.extend([f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"])
                
            query += " ORDER BY tipo, nombre"
            
            cursor.execute(query, params)
            usuarios = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            if not usuarios:
                messagebox.showinfo("Información", "No hay usuarios con los criterios seleccionados.")
                return
                
            for usuario in usuarios:
                self.tree.insert("", "end", values=(
                    usuario['id_usuario'],
                    usuario['usuario'],
                    usuario['tipo'],
                    usuario['nombre'],
                    usuario['correo'],
                    usuario['detalles']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def filtrar_usuarios(self):
        tipo = self.tipo_var.get()
        busqueda = self.busqueda_var.get()
        self.cargar_usuarios(tipo, busqueda)

    def limpiar_filtros(self):
        self.tipo_var.set('Todos')
        self.busqueda_var.set('')
        self.cargar_usuarios()

    def obtener_usuario_seleccionado(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un usuario primero.")
            return None
            
        item = self.tree.item(seleccionado[0])
        return {
            'id_usuario': item['values'][0],
            'usuario': item['values'][1],
            'tipo': item['values'][2],
            'nombre': item['values'][3],
            'correo': item['values'][4],
            'detalles': item['values'][5]
        }

    def nuevo_usuario(self):
        # Implementar lógica para crear nuevo usuario
        # Podría abrir una ventana similar a alta_usuario.py pero con más opciones
        messagebox.showinfo("Información", "Funcionalidad para agregar nuevo usuario.")

    def editar_usuario(self):
        usuario = self.obtener_usuario_seleccionado()
        if not usuario:
            return
            
        # Implementar lógica para editar usuario
        messagebox.showinfo("Información", f"Editar usuario: {usuario['nombre']}")

    def eliminar_usuario(self):
        usuario = self.obtener_usuario_seleccionado()
        if not usuario:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Estás seguro de eliminar al usuario {usuario['nombre']} ({usuario['tipo']})?"
        )
        
        if not confirmacion:
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Eliminar usuario según su tipo
            if usuario['tipo'] == "Estudiante":
                cursor.execute("DELETE FROM estudiantes WHERE id_estudiante = (SELECT id_relacion FROM usuarios WHERE id_usuario = %s)", 
                             (usuario['id_usuario'],))
            elif usuario['tipo'] == "Tutor":
                # Primero eliminar relaciones en tutores_areas
                cursor.execute("DELETE FROM tutores_areas WHERE id_tutor = (SELECT id_relacion FROM usuarios WHERE id_usuario = %s)", 
                             (usuario['id_usuario'],))
                cursor.execute("DELETE FROM tutores WHERE id_tutor = (SELECT id_relacion FROM usuarios WHERE id_usuario = %s)", 
                             (usuario['id_usuario'],))
            
            # Finalmente eliminar el usuario
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (usuario['id_usuario'],))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            self.cargar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()