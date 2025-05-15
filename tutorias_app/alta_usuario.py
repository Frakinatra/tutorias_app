import tkinter as tk
from tkinter import messagebox
import mysql.connector
import re
from conexion import conectar

class AltaUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Alta de Usuario")
        self.root.geometry("400x250")
        self.root.configure(bg="#f0f0f0")

        self.centrar_ventana(400, 250)

        # Frame de formulario
        self.frame = tk.Frame(root, bg="#f0f0f0")
        self.frame.pack(pady=20)

        # Nombre
        tk.Label(self.frame, text="Nombre completo:", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.nombre_entry = tk.Entry(self.frame)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=5)

        # Correo
        tk.Label(self.frame, text="Correo electrónico:", bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.correo_entry = tk.Entry(self.frame)
        self.correo_entry.grid(row=1, column=1, padx=10, pady=5)

        # Botón para guardar
        self.guardar_btn = tk.Button(self.frame, text="Guardar", command=self.guardar_usuario, bg="#4caf50", fg="white")
        self.guardar_btn.grid(row=2, columnspan=2, pady=10)

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def guardar_usuario(self):
        nombre = self.nombre_entry.get()
        correo = self.correo_entry.get()

        if not nombre or not correo:
            messagebox.showwarning("Campos Vacíos", "Todos los campos son obligatorios.")
            return

        # Validar formato de correo
        if not re.match(r"[^@]+@(alumno|tutor|admin)\.edu$", correo):
            messagebox.showerror("Error", "Formato de correo inválido. Debe ser @alumno.edu, @tutor.edu o @admin.edu")
            return

        tipo = "alumno" if "@alumno.edu" in correo else "tutor" if "@tutor.edu" in correo else "admin"

        conexion = conectar()
        cursor = conexion.cursor()

        try:
            # Insertar en la tabla correspondiente
            if tipo == "alumno":
                cursor.execute("INSERT INTO estudiantes (nombre, correo) VALUES (%s, %s)", (nombre, correo))
                id_relacion = cursor.lastrowid
            elif tipo == "tutor":
                cursor.execute("INSERT INTO tutores (nombre, correo) VALUES (%s, %s)", (nombre, correo))
                id_relacion = cursor.lastrowid
            else:  # admin
                id_relacion = None
            
            # Insertar en tabla de usuarios
            cursor.execute("INSERT INTO usuarios (username, password, id_relacion) VALUES (%s, %s, %s)",
                         (correo, "password123", id_relacion))  # Contraseña temporal

            conexion.commit()

            # Limpiar campos
            self.nombre_entry.delete(0, tk.END)
            self.correo_entry.delete(0, tk.END)

            messagebox.showinfo("Éxito", f"Usuario {tipo} creado correctamente.\nCorreo: {correo}\nContraseña temporal: password123")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo crear el usuario: {err}")
        finally:
            conexion.close()