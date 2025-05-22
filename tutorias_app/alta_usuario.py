import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import re
from conexion import conectar

class AltaUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("Alta de Usuario")
        self.root.geometry("450x550")  # Aumentamos el tamaño para los nuevos campos
        self.root.configure(bg="#f0f0f0")
        self.centrar_ventana(450, 550)
        
        # Variable para tipo de usuario
        self.tipo_usuario = tk.StringVar()
        self.campos_especificos = None

        # Configurar estilo
        self.configurar_estilos()

        # Frame principal
        self.frame_principal = tk.Frame(root, bg="#f0f0f0")
        self.frame_principal.pack(pady=15)

        # Frame para selección de tipo de usuario
        self.frame_tipo = tk.Frame(self.frame_principal, bg="#f0f0f0")
        self.frame_tipo.pack(pady=10)

        tk.Label(self.frame_tipo, text="Tipo de usuario:", bg="#f0f0f0").grid(row=0, column=0, padx=5, sticky="w")
        
        self.alumno_radio = ttk.Radiobutton(
            self.frame_tipo, text="Alumno", variable=self.tipo_usuario, 
            value="alumno", command=self.mostrar_campos_especificos
        )
        self.alumno_radio.grid(row=0, column=1, padx=5, sticky="w")
        
        self.tutor_radio = ttk.Radiobutton(
            self.frame_tipo, text="Tutor", variable=self.tipo_usuario, 
            value="tutor", command=self.mostrar_campos_especificos
        )
        self.tutor_radio.grid(row=0, column=2, padx=5, sticky="w")

        # Frame para campos comunes
        self.frame_comun = tk.Frame(self.frame_principal, bg="#f0f0f0")
        self.frame_comun.pack(pady=10)

        # Campos comunes para todos los usuarios
        tk.Label(self.frame_comun, text="Nombres:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.nombre_entry = tk.Entry(self.frame_comun, width=25)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.frame_comun, text="Apellido Paterno:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.apellido_paterno_entry = tk.Entry(self.frame_comun, width=25)
        self.apellido_paterno_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.frame_comun, text="Apellido Materno:", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.apellido_materno_entry = tk.Entry(self.frame_comun, width=25)
        self.apellido_materno_entry.grid(row=2, column=1, padx=5, pady=5)

        # Correo (se completará automáticamente según el tipo)
        tk.Label(self.frame_comun, text="Correo electrónico:", bg="#f0f0f0").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.correo_entry = tk.Entry(self.frame_comun, width=25)
        self.correo_entry.grid(row=3, column=1, padx=5, pady=5)

        # Contraseña
        tk.Label(self.frame_comun, text="Contraseña:", bg="#f0f0f0").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.frame_comun, show="*", width=25)
        self.password_entry.grid(row=4, column=1, padx=5, pady=5)

        # Confirmar Contraseña
        tk.Label(self.frame_comun, text="Confirmar Contraseña:", bg="#f0f0f0").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.confirm_password_entry = tk.Entry(self.frame_comun, show="*", width=25)
        self.confirm_password_entry.grid(row=5, column=1, padx=5, pady=5)

        # Frame para campos específicos (se llenará dinámicamente)
        self.frame_especifico = tk.Frame(self.frame_principal, bg="#f0f0f0")
        self.frame_especifico.pack(pady=10)

        # Botón para guardar
        self.guardar_btn = ttk.Button(self.frame_principal, text="Registrar Usuario", command=self.guardar_usuario)
        self.guardar_btn.pack(pady=15)

    def mostrar_campos_especificos(self):
        # Limpiar frame de campos específicos
        for widget in self.frame_especifico.winfo_children():
            widget.destroy()

        tipo = self.tipo_usuario.get()
        
        if tipo == "alumno":
            # Campos específicos para alumno
            tk.Label(self.frame_especifico, text="Carrera:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.carrera_entry = tk.Entry(self.frame_especifico, width=25)
            self.carrera_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(self.frame_especifico, text="Semestre:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.semestre_entry = tk.Entry(self.frame_especifico, width=25)
            self.semestre_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(self.frame_especifico, text="Teléfono:", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            self.telefono_entry = tk.Entry(self.frame_especifico, width=25)
            self.telefono_entry.grid(row=2, column=1, padx=5, pady=5)

            # Actualizar correo sugerido
            nombre = self.nombre_entry.get().strip()
            apellido = self.apellido_paterno_entry.get().strip()
            if nombre and apellido:
                correo_sugerido = f"{nombre.lower()}.{apellido.lower()}@alumno.edu"
                self.correo_entry.delete(0, tk.END)
                self.correo_entry.insert(0, correo_sugerido)

        elif tipo == "tutor":
            # Campos específicos para tutor
            tk.Label(self.frame_especifico, text="Especialidad:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.especialidad_entry = tk.Entry(self.frame_especifico, width=25)
            self.especialidad_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(self.frame_especifico, text="Experiencia:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.experiencia_entry = tk.Text(self.frame_especifico, width=25, height=4)
            self.experiencia_entry.grid(row=1, column=1, padx=5, pady=5)

            # Actualizar correo sugerido
            nombre = self.nombre_entry.get().strip()
            apellido = self.apellido_paterno_entry.get().strip()
            if nombre and apellido:
                correo_sugerido = f"profesor.{apellido.lower()}@tutor.edu"
                self.correo_entry.delete(0, tk.END)
                self.correo_entry.insert(0, correo_sugerido)

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6, 
                       background="#4caf50", foreground="white", relief="flat")
        style.map("TButton", background=[("active", "#45a049")])
        style.configure("TRadiobutton", background="#f0f0f0")

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def validar_correo(self, correo, tipo):
        """Valida el formato del correo electrónico según el tipo de usuario"""
        if tipo == "alumno" and not correo.endswith("@alumno.edu"):
            messagebox.showerror("Error", "El correo de alumno debe terminar con @alumno.edu")
            return False
        elif tipo == "tutor" and not correo.endswith("@tutor.edu"):
            messagebox.showerror("Error", "El correo de tutor debe terminar con @tutor.edu")
            return False
        
        if not re.match(r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", correo):
            messagebox.showerror("Error", "Formato de correo inválido")
            return False
        return True

    def validar_password(self, password, confirm_password):
        """Valida que las contraseñas coincidan y cumplan con requisitos mínimos"""
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return False
        
        if len(password) < 8:
            messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres")
            return False
            
        if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
            messagebox.showerror("Error", "La contraseña debe contener al menos una letra y un número")
            return False
            
        return True

    def validar_nombre_completo(self, nombre, apellido_paterno):
        """Valida que al menos nombre y apellido paterno estén completos"""
        if not nombre.strip() or not apellido_paterno.strip():
            messagebox.showerror("Error", "Debe ingresar al menos nombre y apellido paterno")
            return False
        return True

    def obtener_nombre_completo(self):
        """Combina los componentes del nombre en un solo string"""
        nombre = self.nombre_entry.get().strip()
        apellido_paterno = self.apellido_paterno_entry.get().strip()
        apellido_materno = self.apellido_materno_entry.get().strip()
        
        nombre_completo = f"{nombre} {apellido_paterno}"
        if apellido_materno:
            nombre_completo += f" {apellido_materno}"
            
        return nombre_completo

    def guardar_usuario(self):
        # Obtener tipo de usuario
        tipo = self.tipo_usuario.get()
        if not tipo:
            messagebox.showerror("Error", "Debe seleccionar un tipo de usuario (alumno o tutor)")
            return

        # Obtener datos del formulario
        nombre = self.nombre_entry.get().strip()
        apellido_paterno = self.apellido_paterno_entry.get().strip()
        apellido_materno = self.apellido_materno_entry.get().strip()
        correo = self.correo_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validaciones básicas
        if not self.validar_nombre_completo(nombre, apellido_paterno):
            return

        if not self.validar_correo(correo, tipo):
            return

        if not self.validar_password(password, confirm_password):
            return

        # Validaciones específicas según tipo
        if tipo == "alumno":
            carrera = self.carrera_entry.get().strip()
            semestre = self.semestre_entry.get().strip()
            telefono = self.telefono_entry.get().strip()
            
            if not carrera or not semestre:
                messagebox.showerror("Error", "Debe completar carrera y semestre para alumnos")
                return
                
            try:
                semestre = int(semestre)
                if semestre <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "El semestre debe ser un número positivo")
                return
                
        elif tipo == "tutor":
            especialidad = self.especialidad_entry.get().strip()
            experiencia = self.experiencia_entry.get("1.0", tk.END).strip()
            
            if not especialidad:
                messagebox.showerror("Error", "Debe especificar una especialidad para tutores")
                return

        nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}".strip()

        conexion = None
        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Verificar si el correo ya existe
            cursor.execute("SELECT username FROM usuarios WHERE username = %s", (correo,))
            if cursor.fetchone():
                messagebox.showerror("Error", "El correo electrónico ya está registrado")
                return

            # Insertar en la tabla correspondiente
            if tipo == "alumno":
                cursor.execute(
                    "INSERT INTO estudiantes (nombres, apellido_paterno, apellido_materno, correo, carrera, semestre, telefono) " 
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (nombre, apellido_paterno, apellido_materno, correo, carrera, semestre, telefono)
                )
                id_relacion = cursor.lastrowid
            elif tipo == "tutor":
                cursor.execute(
                    "INSERT INTO tutores (nombres, apellido_paterno, apellido_materno, correo, especialidad, experiencia) " 
                    "VALUES (%s, %s, %s, %s, %s, %s)", 
                    (nombre, apellido_paterno, apellido_materno, correo, especialidad, experiencia)
                )
                id_relacion = cursor.lastrowid
            
            # Insertar en tabla de usuarios
            cursor.execute(
                "INSERT INTO usuarios (username, password, tipo, id_relacion) VALUES (%s, %s, %s, %s)",
                (correo, password, tipo, id_relacion)
            )

            conexion.commit()

            # Limpiar campos
            self.nombre_entry.delete(0, tk.END)
            self.apellido_paterno_entry.delete(0, tk.END)
            self.apellido_materno_entry.delete(0, tk.END)
            self.correo_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
            
            if tipo == "alumno":
                self.carrera_entry.delete(0, tk.END)
                self.semestre_entry.delete(0, tk.END)
                self.telefono_entry.delete(0, tk.END)
            elif tipo == "tutor":
                self.especialidad_entry.delete(0, tk.END)
                self.experiencia_entry.delete("1.0", tk.END)

            messagebox.showinfo(
                "Éxito", 
                f"Usuario {tipo} registrado correctamente:\n"
                f"Nombre: {nombre_completo}\n"
                f"Correo: {correo}"
            )

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo crear el usuario: {err}")
            if conexion:
                conexion.rollback()
        finally:
            if conexion and conexion.is_connected():
                cursor.close()
                conexion.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AltaUsuario(root)
    root.mainloop()