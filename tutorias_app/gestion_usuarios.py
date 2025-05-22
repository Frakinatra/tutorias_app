import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from conexion import conectar

class GestionUsuarios:
    def __init__(self, root):
        self.root = root
        self.root.title("👥 Gestión de Usuarios")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        self.centrar_ventana(1000, 600)

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
        columns = ("ID", "Nombres", "Apellido Paterno", "Apellido Materno", "Correo", "Carrera", "Semestre", "Contraseña")
        self.tree_estudiantes = ttk.Treeview(self.frame_estudiantes, columns=columns, show="headings")
        
        anchos = {
            "ID": 50,
            "Nombres": 100,
            "Apellido Paterno": 100,
            "Apellido Materno": 100,
            "Correo": 150,
            "Carrera": 100,
            "Semestre": 70,
            "Contraseña": 100   
        }
        
        for col in columns:
            self.tree_estudiantes.heading(col, text=col)
            self.tree_estudiantes.column(col, anchor="center", width=anchos.get(col, 100))
        
        scroll_y = ttk.Scrollbar(self.frame_estudiantes, orient="vertical", command=self.tree_estudiantes.yview)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(self.frame_estudiantes, orient="horizontal", command=self.tree_estudiantes.xview)
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree_estudiantes.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree_estudiantes.pack(fill="both", expand=True, padx=10, pady=5)

        frame_botones = tk.Frame(self.frame_estudiantes, bg="#f0f0f0")
        frame_botones.pack(pady=5)

        tk.Button(frame_botones, text="✏️ Modificar", command=self.modificar_estudiante, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_estudiante, bg="#f44336", fg="white").pack(side="left", padx=5)

        self.cargar_estudiantes()

    def cargar_estudiantes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT e.id_estudiante, e.nombres, e.apellido_paterno, e.apellido_materno, 
                       e.correo, e.carrera, e.semestre, u.password
                FROM estudiantes e
                JOIN usuarios u ON e.correo = u.username
            """)

            # Limpia la tabla actual
            for item in self.tree_estudiantes.get_children():
                self.tree_estudiantes.delete(item)

            # Inserta los nuevos datos
            for estudiante in cursor.fetchall():
                self.tree_estudiantes.insert("", "end", values=(
                    estudiante['id_estudiante'],
                    estudiante['nombres'],
                    estudiante['apellido_paterno'],
                    estudiante['apellido_materno'],
                    estudiante['correo'],
                    estudiante['carrera'],
                    estudiante['semestre'],
                    estudiante['password']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los estudiantes: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def modificar_estudiante(self):
        seleccionado = self.tree_estudiantes.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un estudiante para modificar.")
            return

        item = self.tree_estudiantes.item(seleccionado)
        datos = item["values"]
        id_estudiante = datos[0]
        correo_actual = datos[4]

        ventana = tk.Toplevel()
        ventana.title("Modificar Estudiante")
        ventana.geometry("400x450")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="Nombres:", bg="#f0f0f0").pack(pady=5)
        entry_nombres = tk.Entry(ventana)
        entry_nombres.insert(0, datos[1])
        entry_nombres.pack()

        tk.Label(ventana, text="Apellido Paterno:", bg="#f0f0f0").pack(pady=5)
        entry_apellido_p = tk.Entry(ventana)
        entry_apellido_p.insert(0, datos[2])
        entry_apellido_p.pack()

        tk.Label(ventana, text="Apellido Materno:", bg="#f0f0f0").pack(pady=5)
        entry_apellido_m = tk.Entry(ventana)
        entry_apellido_m.insert(0, datos[3])
        entry_apellido_m.pack()

        tk.Label(ventana, text="Carrera:", bg="#f0f0f0").pack(pady=5)
        entry_carrera = tk.Entry(ventana)
        entry_carrera.insert(0, datos[5])
        entry_carrera.pack()

        tk.Label(ventana, text="Semestre:", bg="#f0f0f0").pack(pady=5)
        entry_semestre = tk.Entry(ventana)
        entry_semestre.insert(0, datos[6])
        entry_semestre.pack()

        tk.Label(ventana, text="Nueva contraseña (dejar vacío para no cambiar):", bg="#f0f0f0").pack(pady=5)
        entry_password = tk.Entry(ventana, show="*")
        entry_password.pack()

        def guardar_cambios():
            nombres = entry_nombres.get().strip()
            apellido_p = entry_apellido_p.get().strip()
            apellido_m = entry_apellido_m.get().strip()
            carrera = entry_carrera.get().strip()
            semestre = entry_semestre.get().strip()
            password = entry_password.get().strip()

            if not nombres or not apellido_p or not carrera or not semestre:
                messagebox.showwarning("Error", "Los campos obligatorios no pueden estar vacíos")
                return

            try:
                semestre = int(semestre)
                if semestre <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Error", "El semestre debe ser un número positivo")
                return

            nuevo_correo = f"{nombres.lower().split()[0]}.{apellido_p.lower()}@alumno.edu"

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                # Actualizar estudiante
                cursor.execute(
                    "UPDATE estudiantes SET nombres=%s, apellido_paterno=%s, apellido_materno=%s, "
                    "carrera=%s, semestre=%s, correo=%s WHERE id_estudiante=%s",
                    (nombres, apellido_p, apellido_m, carrera, semestre, nuevo_correo, id_estudiante)
                )

                # Actualizar usuario
                if password:
                    cursor.execute(
                        "UPDATE usuarios SET username=%s, password=%s WHERE username=%s",
                        (nuevo_correo, password, correo_actual)
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET username=%s WHERE username=%s",
                        (nuevo_correo, correo_actual)
                    )

                conexion.commit()
                messagebox.showinfo("Éxito", "Estudiante actualizado correctamente")
                ventana.destroy()
                self.cargar_estudiantes()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo actualizar: {err}")
                conexion.rollback()
            finally:
                conexion.close()

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
            resultado = cursor.fetchone()
            
            if not resultado:
                messagebox.showerror("Error", "No se encontró el estudiante")
                return
                
            correo = resultado[0]
            
            # Eliminar usuario primero
            cursor.execute("DELETE FROM usuarios WHERE username = %s", (correo,))
            
            # Luego eliminar estudiante
            cursor.execute("DELETE FROM estudiantes WHERE id_estudiante = %s", (id_estudiante,))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Estudiante eliminado")
            self.cargar_estudiantes()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar: {err}")
            conexion.rollback()
        finally:
            conexion.close()

    # CRUD Tutores
    def tutores_ui(self):
        columns = ("ID", "Nombres", "Apellido Paterno", "Apellido Materno", "Correo", "Especialidad", "Área", "Contraseña")
        self.tree_tutores = ttk.Treeview(self.frame_tutores, columns=columns, show="headings")
        
        anchos = {
            "ID": 50,
            "Nombres": 100,
            "Apellido Paterno": 100,
            "Apellido Materno": 100,
            "Correo": 150,
            "Especialidad": 120,
            "Área": 100,
            "Contraseña": 100   
        }
        
        for col in columns:
            self.tree_tutores.heading(col, text=col)
            self.tree_tutores.column(col, anchor="center", width=anchos.get(col, 100))
        
        scroll_y = ttk.Scrollbar(self.frame_tutores, orient="vertical", command=self.tree_tutores.yview)
        scroll_y.pack(side="right", fill="y")
        
        scroll_x = ttk.Scrollbar(self.frame_tutores, orient="horizontal", command=self.tree_tutores.xview)
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree_tutores.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree_tutores.pack(fill="both", expand=True, padx=10, pady=5)

        frame_botones = tk.Frame(self.frame_tutores, bg="#f0f0f0")
        frame_botones.pack(pady=5)

        
        tk.Button(frame_botones, text="✏️ Modificar", command=self.modificar_tutor, bg="#2196f3", fg="white").pack(side="left", padx=5)
        tk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_tutor, bg="#f44336", fg="white").pack(side="left", padx=5)

        self.cargar_tutores()

    def obtener_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento ORDER BY nombre_area")
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {str(e)}")
            return []
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def cargar_tutores(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute("""
                SELECT t.id_tutor, t.nombres, t.apellido_paterno, t.apellido_materno, 
                       t.correo, t.especialidad, a.nombre_area AS area, u.password
                FROM tutores t
                JOIN usuarios u ON t.correo = u.username
                JOIN tutores_areas ta ON t.id_tutor = ta.id_tutor
                JOIN areas_conocimiento a ON ta.id_area = a.id_area
            """)

            # Limpia la tabla actual
            for item in self.tree_tutores.get_children():
                self.tree_tutores.delete(item)

            # Inserta los nuevos datos
            for tutor in cursor.fetchall():
                self.tree_tutores.insert("", "end", values=(
                    tutor['id_tutor'],
                    tutor['nombres'],
                    tutor['apellido_paterno'],
                    tutor['apellido_materno'],
                    tutor['correo'],
                    tutor['especialidad'],
                    tutor['area'],
                    tutor['password']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tutores: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()


    def modificar_tutor(self):
        seleccionado = self.tree_tutores.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un tutor para modificar.")
            return

        item = self.tree_tutores.item(seleccionado)
        datos = item["values"]
        id_tutor = datos[0]
        correo_actual = datos[4]
        area_actual = datos[6]

        areas = self.obtener_areas()
        if not areas:
            return

        ventana = tk.Toplevel()
        ventana.title("Modificar Tutor")
        ventana.geometry("400x500")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="Nombres:", bg="#f0f0f0").pack(pady=5)
        entry_nombres = tk.Entry(ventana)
        entry_nombres.insert(0, datos[1])
        entry_nombres.pack()

        tk.Label(ventana, text="Apellido Paterno:", bg="#f0f0f0").pack(pady=5)
        entry_apellido_p = tk.Entry(ventana)
        entry_apellido_p.insert(0, datos[2])
        entry_apellido_p.pack()

        tk.Label(ventana, text="Apellido Materno:", bg="#f0f0f0").pack(pady=5)
        entry_apellido_m = tk.Entry(ventana)
        entry_apellido_m.insert(0, datos[3])
        entry_apellido_m.pack()

        tk.Label(ventana, text="Especialidad:", bg="#f0f0f0").pack(pady=5)
        entry_especialidad = tk.Entry(ventana)
        entry_especialidad.insert(0, datos[5])
        entry_especialidad.pack()

        tk.Label(ventana, text="Área de conocimiento:", bg="#f0f0f0").pack(pady=5)
        area_var = tk.StringVar()
        combo_area = ttk.Combobox(ventana, textvariable=area_var, 
                                 values=[a[1] for a in areas], state="readonly")
        combo_area.pack()
        combo_area.set(area_actual)

        tk.Label(ventana, text="Nueva contraseña (dejar vacío para no cambiar):", bg="#f0f0f0").pack(pady=5)
        entry_password = tk.Entry(ventana, show="*")
        entry_password.pack()

        def guardar_cambios():
            nombres = entry_nombres.get().strip()
            apellido_p = entry_apellido_p.get().strip()
            apellido_m = entry_apellido_m.get().strip()
            especialidad = entry_especialidad.get().strip()
            area_idx = combo_area.current()
            password = entry_password.get().strip()

            if not nombres or not apellido_p or not especialidad or area_idx == -1:
                messagebox.showwarning("Error", "Los campos obligatorios no pueden estar vacíos")
                return

            id_area = areas[area_idx][0]
            nuevo_correo = f"profesor.{apellido_p.lower()}@tutor.edu"

            conexion = conectar()
            cursor = conexion.cursor()
            try:
                # Actualizar tutor
                cursor.execute(
                    "UPDATE tutores SET nombres=%s, apellido_paterno=%s, apellido_materno=%s, "
                    "especialidad=%s, correo=%s WHERE id_tutor=%s",
                    (nombres, apellido_p, apellido_m, especialidad, nuevo_correo, id_tutor)
                )

                # Actualizar área
                cursor.execute(
                    "UPDATE tutores_areas SET id_area=%s WHERE id_tutor=%s",
                    (id_area, id_tutor)
                )

                # Actualizar usuario
                if password:
                    cursor.execute(
                        "UPDATE usuarios SET username=%s, password=%s WHERE username=%s",
                        (nuevo_correo, password, correo_actual)
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET username=%s WHERE username=%s",
                        (nuevo_correo, correo_actual)
                    )

                conexion.commit()
                messagebox.showinfo("Éxito", "Tutor actualizado correctamente")
                ventana.destroy()
                self.cargar_tutores()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo actualizar: {err}")
                conexion.rollback()
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
                messagebox.showerror("Error", "No se encontró el tutor")
                return
                
            correo = resultado[0]
            
            # Eliminar de tutores_areas
            cursor.execute("DELETE FROM tutores_areas WHERE id_tutor = %s", (id_tutor,))
            
            # Eliminar de usuarios
            cursor.execute("DELETE FROM usuarios WHERE username = %s", (correo,))
            
            # Eliminar de tutores
            cursor.execute("DELETE FROM tutores WHERE id_tutor = %s", (id_tutor,))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Tutor eliminado correctamente")
            self.cargar_tutores()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar: {err}")
            conexion.rollback()
        finally:
            conexion.close()