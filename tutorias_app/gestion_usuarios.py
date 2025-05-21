import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from conexion import conectar

class GestionUsuarios:
    def __init__(self, root):
        self.root = root
        self.root.title("👥 Gestión de Usuarios")
        self.root.geometry("750x500")
        self.root.configure(bg="#f0f0f0")

        self.centrar_ventana(750, 500)

        notebook = ttk.Notebook(root)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        self.frame_estudiantes = tk.Frame(notebook, bg="#f0f0f0")
        self.frame_tutores = tk.Frame(notebook, bg="#f0f0f0")

        notebook.add(self.frame_estudiantes, text="📘 Estudiantes")
        notebook.add(self.frame_tutores, text="📗 Tutores")

        self.estudiantes_ui()
        self.tutores_ui()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    # CRUD Estudiantes
    def estudiantes_ui(self):
        columns = ("ID", "Nombre", "Correo", "Carrera", "Semestre", "Contraseña")
        self.tree_estudiantes = ttk.Treeview(self.frame_estudiantes, columns=columns, show="headings")
        anchos = {
            "ID": 50,
            "Nombre": 130,
            "Correo": 200,
            "Carrera": 115,
            "Semestre": 70,
            "Contraseña": 110   
        }
        for col in columns:

            self.tree_estudiantes.heading(col, text=col)
            self.tree_estudiantes.column(col, anchor="center", width=anchos.get(col, 100))
        self.tree_estudiantes.pack(fill="both", expand=True, padx=10, pady=5)

        frame_botones = tk.Frame(self.frame_estudiantes, bg="#f0f0f0")
        frame_botones.pack(pady=5)

        tk.Button(frame_botones, text="➕ Añadir", command=self.agregar_estudiante, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="✏️ Modificar", command=self.modificar_estudiante, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_estudiante, bg="#f44336", fg="white").pack(side="left", padx=5)

        self.cargar_estudiantes()

    def cargar_estudiantes(self):
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT e.id_estudiante, e.nombre, e.correo, e.carrera, e.semestre, u.password
            FROM estudiantes e
            JOIN usuarios u ON e.correo = u.username
        """)

        resultados = cursor.fetchall()
        conexion.close()

        # Limpia la tabla actual
        for item in self.tree_estudiantes.get_children():
            self.tree_estudiantes.delete(item)

        # Inserta los nuevos datos
        for fila in resultados:
            self.tree_estudiantes.insert("", "end", values=fila)


    def agregar_estudiante(self):
        nombre = simpledialog.askstring("Nuevo Estudiante", "Nombre completo:")
        if not nombre:
            return

        carrera = simpledialog.askstring("Nuevo Estudiante", "Carrera:")
        if not carrera:
            return

        try:
            semestre = simpledialog.askinteger("Nuevo Estudiante", "Semestre:")
            if semestre is None or semestre <= 0:
                messagebox.showwarning("Datos inválidos", "El semestre debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showwarning("Datos inválidos", "El semestre debe ser un número.")
            return

        # Generar correo automático
        correo = f"{nombre.lower().replace(' ', '.')}@alumno.edu"

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "INSERT INTO estudiantes (nombre, correo, carrera, semestre) VALUES (%s, %s, %s, %s)",
                (nombre, correo, carrera, semestre)
            )
            id_estudiante = cursor.lastrowid

            # Insertar también en la tabla usuarios
            cursor.execute(
                "INSERT INTO usuarios (username, password, id_relacion) VALUES (%s, %s, %s)",
                (correo, "alumno123", id_estudiante)
            )

            conexion.commit()
            messagebox.showinfo("Éxito", f"Estudiante agregado.\nCorreo: {correo}\nContraseña temporal: alumno123")
            self.cargar_estudiantes()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo agregar: {err}")
        finally:
            conexion.close()


    def modificar_estudiante(self):
        seleccionado = self.tree_estudiantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un estudiante para modificar.")
            return

        item = self.tree_estudiantes.item(seleccionado)
        datos = item["values"]
        id_estudiante = datos[0]
        nombre_actual = datos[1]
        correo = datos[2]

        ventana = tk.Toplevel()
        ventana.title("Modificar Estudiante")
        ventana.geometry("350x250")

        tk.Label(ventana, text="Nuevo nombre:").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack()

        tk.Label(ventana, text="Nueva contraseña:").pack(pady=5)
        entry_contrasena = tk.Entry(ventana, show="*")
        entry_contrasena.pack()

        tk.Label(ventana, text="Repetir contraseña:").pack(pady=5)
        entry_repetir = tk.Entry(ventana, show="*")
        entry_repetir.pack()

        def guardar_cambios():
            nuevo_nombre = entry_nombre.get().strip()
            nueva_contrasena = entry_contrasena.get().strip()
            repetir_contrasena = entry_repetir.get().strip()
            

            if not nuevo_nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                return

            conexion = conectar()
            cursor = conexion.cursor()

            nvo_correo = f"{nuevo_nombre.lower().replace(' ', '.')}@alumno.edu"
            # Actualiza el nombre
            cursor.execute("UPDATE estudiantes SET nombre = %s, correo = %s WHERE id_estudiante = %s", (nuevo_nombre, nvo_correo, id_estudiante))

            # Si se ingresó nueva contraseña
            if nueva_contrasena or repetir_contrasena:
                if nueva_contrasena != repetir_contrasena:
                    messagebox.showerror("Error", "Las contraseñas no coinciden.")
                    conexion.close()
                    return
                
                cursor.execute("UPDATE usuarios SET password = %s, username = %s WHERE username = %s", (nueva_contrasena, nvo_correo, correo))

            conexion.commit()
            conexion.close()
            self.cargar_estudiantes()
            ventana.destroy()
            messagebox.showinfo("Éxito", "Estudiante actualizado correctamente.")

        tk.Button(ventana, text="Guardar cambios", command=guardar_cambios, bg="#2196f3", fg="white").pack(pady=10)


    def eliminar_estudiante(self):
        seleccionado = self.tree_estudiantes.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un estudiante.")
            return
            
        id_estudiante = self.tree_estudiantes.item(seleccionado[0])['values'][0]
        
        confirmacion = messagebox.askyesno("Confirmar", "¿Eliminar este estudiante y su usuario?")
        if not confirmacion:
            return
            
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            # Obtener correo para eliminar usuario
            cursor.execute("SELECT correo FROM estudiantes WHERE id_estudiante = %s", (id_estudiante,))
            correo = cursor.fetchone()[0]
            
            # Eliminar usuario primero
            cursor.execute("DELETE FROM usuarios WHERE username = %s", (correo,))
            
            # Luego eliminar estudiante
            cursor.execute("DELETE FROM estudiantes WHERE id_estudiante = %s", (id_estudiante,))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Estudiante eliminado")
            self.cargar_estudiantes()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar: {err}")
        finally:
            conexion.close()

        

    # CRUD Tutores (similar a estudiantes)
    def tutores_ui(self):
        columns = ("ID", "Nombre", "Correo", "Contraseña", "Especialidad", "Área")
        self.tree_tutores = ttk.Treeview(self.frame_tutores, columns=columns, show="headings")
        anchos = {
            "ID": 20,
            "Nombre": 115,
            "Correo": 170,
            "Contraseña": 80,
            "Especialidad": 125,
            "Área": 100   
        }
        for col in columns:
            self.tree_tutores.heading(col, text=col)
            self.tree_tutores.column(col, anchor="center", width=anchos.get(col, 100))
        self.tree_tutores.pack(fill="both", expand=True, padx=10, pady=5)

        frame_botones = tk.Frame(self.frame_tutores, bg="#f0f0f0")
        frame_botones.pack(pady=5)

        tk.Button(frame_botones, text="➕ Añadir", command=self.agregar_tutor, bg="#4caf50", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="✏️ Modificar", command=self.modificar_tutor, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_tutor, bg="#f44336", fg="white").pack(side="left", padx=5)

        self.cargar_tutores()



    def cargar_tutores(self):
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT a.id_tutor, a.nombre, a.correo, b.password, a.especialidad, c.nombre_area
            FROM tutores_areas d
            JOIN tutores a ON a.id_tutor = d.id_tutor
            JOIN usuarios b ON a.correo = b.username
            JOIN areas_conocimiento c ON c.id_area = d.id_area
        """)

        resultados = cursor.fetchall()
        conexion.close()

        for item in self.tree_tutores.get_children():
            self.tree_tutores.delete(item)
        for fila in resultados:
            self.tree_tutores.insert("", "end", values=fila)


    def obtener_areas(self):
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='tutorias_db'
            )
            cursor = conexion.cursor()
            cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento")
            resultados = cursor.fetchall()
            conexion.close()
            return resultados

    def agregar_tutor(self):
        areas = self.obtener_areas()
        if not areas:
            messagebox.showerror("Error", "No hay áreas registradas.")
            return

        nombre = simpledialog.askstring("Nuevo Tutor", "Nombre completo:")
        if not nombre:
            return

        self.ventana = tk.Toplevel()
        self.ventana.title("Agregar Tutor")
        ancho_ventana = 350
        alto_ventana = 250

        # Obtener dimensiones de la pantalla
        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()

        # Calcular coordenadas para centrar la ventana
        x = (pantalla_ancho // 2) - (ancho_ventana // 2)
        y = (pantalla_alto // 2) - (alto_ventana // 2)

        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        tk.Label(self.ventana, text="Selecciona un área de conocimiento:").pack(pady=5)
        area_var = tk.StringVar()
        combo_areas = ttk.Combobox(self.ventana, textvariable=area_var, values=[a[1] for a in areas], state="readonly")
        combo_areas.pack()

        tk.Label(self.ventana, text="Nombre de la especialidad:").pack(pady=5)
        entry_especialidad = tk.Entry(self.ventana)
        entry_especialidad.pack()

        def confirmar():
            indice = combo_areas.current()
            if indice == -1:
                messagebox.showwarning("Error", "Selecciona un área válida.")
                return

            especialidad = entry_especialidad.get()
            if not especialidad:
                messagebox.showwarning("Error", "Ingresa una especialidad.")
                return

            id_area = areas[indice][0]
            correo = f"{nombre.lower().replace(' ', '.')}@tutor.edu"

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("INSERT INTO tutores (nombre, correo, especialidad) VALUES (%s, %s, %s)",
                            (nombre, correo, especialidad))
                id_tutor = cursor.lastrowid

                cursor.execute("INSERT INTO usuarios (username, password, id_relacion) VALUES (%s, %s, %s)",
                            (correo, "tutor123", id_tutor))

                cursor.execute("INSERT INTO tutores_areas (id_tutor, id_area) VALUES (%s, %s)", (id_tutor, id_area))
                conexion.commit()

                messagebox.showinfo("Éxito", f"Tutor agregado.\nCorreo: {correo}\nContraseña temporal: tutor123")
                self.ventana.destroy()
                self.cargar_tutores()

            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo agregar: {err}")
            finally:
                conexion.close()

        tk.Button(self.ventana, text="Guardar Tutor", command=confirmar).pack(pady=10)



    def modificar_tutor(self):
        seleccionado = self.tree_tutores.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un tutor para modificar.")
            return

        item = self.tree_tutores.item(seleccionado)
        datos = item["values"]
        id_tutor = datos[0]
        nombre_actual = datos[1]
        correo_actual = datos[2]
        especialidad_actual = datos[4]
        area_actual = datos[5]

        areas = self.obtener_areas()

        ventana = tk.Toplevel()
        ventana.title("Modificar Tutor")
        ancho, alto = 400, 300
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(ventana, text="Nuevo nombre:").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack()

        tk.Label(ventana, text="Nueva especialidad:").pack(pady=5)
        entry_especialidad = tk.Entry(ventana)
        entry_especialidad.insert(0, especialidad_actual)
        entry_especialidad.pack()

        tk.Label(ventana, text="Nueva contraseña:").pack(pady=5)
        entry_contrasena = tk.Entry(ventana, show="*")
        entry_contrasena.pack()

        tk.Label(ventana, text="Confirmar contraseña:").pack(pady=5)
        entry_confirmar = tk.Entry(ventana, show="*")
        entry_confirmar.pack()

        tk.Label(ventana, text="Área de conocimiento:").pack(pady=5)
        area_var = tk.StringVar()
        combo_area = ttk.Combobox(ventana, textvariable=area_var, values=[a[1] for a in areas], state="readonly")
        combo_area.pack()
        combo_area.set(area_actual)

        def guardar_cambios():
            nuevo_nombre = entry_nombre.get().strip()
            nueva_especialidad = entry_especialidad.get().strip()
            contrasena = entry_contrasena.get().strip()
            confirmar = entry_confirmar.get().strip()
            indice_area = combo_area.current()

            if not nuevo_nombre or not nueva_especialidad or indice_area == -1:
                messagebox.showerror("Error", "Completa todos los campos obligatorios.")
                return

            if contrasena and contrasena != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return

            nuevo_correo = f"{nuevo_nombre.lower().replace(' ', '.')}@tutor.edu"
            id_area = areas[indice_area][0]

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                cursor.execute("UPDATE tutores SET nombre = %s, correo = %s, especialidad = %s WHERE id_tutor = %s",
                            (nuevo_nombre, nuevo_correo, nueva_especialidad, id_tutor))
                
                if contrasena:
                    cursor.execute("UPDATE usuarios SET username = %s, password = %s WHERE username = %s",
                                (nuevo_correo, contrasena, correo_actual))
                else:
                    cursor.execute("UPDATE usuarios SET username = %s WHERE username = %s",
                                (nuevo_correo, correo_actual))

                cursor.execute("UPDATE tutores_areas SET id_area = %s WHERE id_tutor = %s", (id_area, id_tutor))

                conexion.commit()
                ventana.destroy()
                self.cargar_tutores()
                messagebox.showinfo("Éxito", "Tutor actualizado correctamente.")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo actualizar: {err}")
            finally:
                conexion.close()

        tk.Button(ventana, text="Guardar cambios", command=guardar_cambios, bg="#2196f3", fg="white").pack(pady=10)

    def eliminar_tutor(self):
        seleccionado = self.tree_tutores.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un tutor.")
            return

        id_tutor = self.tree_tutores.item(seleccionado[0])['values'][0]

        confirmacion = messagebox.askyesno("Confirmar", "¿Eliminar este tutor y sus registros relacionados?")
        if not confirmacion:
            return

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            # Obtener el correo del tutor
            cursor.execute("SELECT correo FROM tutores WHERE id_tutor = %s", (id_tutor,))
            resultado = cursor.fetchone()
            if not resultado:
                messagebox.showerror("Error", "No se encontró el tutor.")
                return
            correo = resultado[0]

            # Eliminar de tutores_areas
            cursor.execute("DELETE FROM tutores_areas WHERE id_tutor = %s", (id_tutor,))

            # Eliminar de usuarios
            cursor.execute("DELETE FROM usuarios WHERE username = %s", (correo,))

            # Eliminar de tutores
            cursor.execute("DELETE FROM tutores WHERE id_tutor = %s", (id_tutor,))

            conexion.commit()
            messagebox.showinfo("Éxito", "Tutor eliminado correctamente.")
            self.cargar_tutores()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar: {err}")
        finally:
            conexion.close()

    def asignar_areas_tutor(self):
        seleccionado = self.tree_tutores.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un tutor.")
            return
        id_tutor = self.tree_tutores.item(seleccionado[0])['values'][0]
        
        # Crear ventana para asignar áreas
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Asignar Áreas al Tutor ID: {id_tutor}")
        ventana.geometry("400x300")
        
        # Lista de áreas disponibles
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento")
        areas = cursor.fetchall()
        
        # Lista de áreas asignadas
        cursor.execute("SELECT id_area FROM tutores_areas WHERE id_tutor = %s", (id_tutor,))
        asignadas = [row[0] for row in cursor.fetchall()]
        
        # Listbox para mostrar áreas
        listbox = tk.Listbox(ventana, selectmode=tk.MULTIPLE)
        for area in areas:
            listbox.insert(tk.END, area[1])
            if area[0] in asignadas:
                listbox.selection_set(tk.END)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def guardar_asignaciones():
            seleccionados = listbox.curselection()
            
            # Eliminar todas las asignaciones actuales
            cursor.execute("DELETE FROM tutores_areas WHERE id_tutor = %s", (id_tutor,))
            
            # Agregar las nuevas asignaciones
            for index in seleccionados:
                area_id = areas[index][0]
                cursor.execute("INSERT INTO tutores_areas (id_tutor, id_area) VALUES (%s, %s)", 
                             (id_tutor, area_id))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Áreas asignadas correctamente")
            ventana.destroy()
        
        tk.Button(ventana, text="Guardar", command=guardar_asignaciones).pack(pady=10)