import tkinter as tk
from tkinter import messagebox
import mysql.connector
import re
from menu_principal import MenuPrincipal
from estudiante_interfaz import InterfazEstudiante
from tutor_interfaz import InterfazTutor

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Tutorías Académicas - Login")
        self.root.geometry("400x350")
        self.root.configure(bg="#f0f0f0")
        
        self.centrar_ventana(400, 350)
        
        # Frame principal
        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(pady=30)
        
        # Logo o título
        tk.Label(frame, text="🔐 Inicio de Sesión", font=("Helvetica", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Campos de usuario y contraseña
        tk.Label(frame, text="Correo electrónico:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.usuario_entry = tk.Entry(frame, width=25)
        self.usuario_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame, text="Contraseña:", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(frame, show="*", width=25)
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Botón de login
        login_btn = tk.Button(frame, text="Iniciar Sesión", command=self.validar_login, bg="#4caf50", fg="white", width=15)
        login_btn.grid(row=3, columnspan=2, pady=15)
        
    
        # Versión
        tk.Label(root, text="Sistema de Tutorías v2.0", bg="#f0f0f0", fg="gray").pack(side="bottom", pady=10)
    
    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def validar_login(self):
        username = self.usuario_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return
        
        # Validar formato de correo
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            messagebox.showerror("Error", "Formato de correo electrónico inválido")
            return
        
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="tutorias_db"
            )
            cursor = conexion.cursor()
            
            query = "SELECT id_usuario, id_relacion FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            resultado = cursor.fetchone()
            
            if resultado:
                id_usuario, id_relacion = resultado
                
                # Determinar tipo de usuario por el dominio del correo
                if "@admin.edu" in username:
                    tipo = "admin"
                elif "@alumno.edu" in username:
                    tipo = "alumno"
                elif "@tutor.edu" in username:
                    tipo = "tutor"
                else:
                    messagebox.showerror("Error", "Dominio de correo no reconocido")
                    return
                
                # Cerrar ventana de login
                self.root.withdraw()
                
                # Abrir ventana según tipo de usuario
                if tipo == "admin":
                    ventana = tk.Toplevel()
                    MenuPrincipal(ventana)
                elif tipo == "alumno":
                    ventana = tk.Toplevel()
                    InterfazEstudiante(ventana, id_relacion)
                elif tipo == "tutor":
                    ventana = tk.Toplevel()
                    InterfazTutor(ventana, id_relacion,self.root)
            else:
                messagebox.showerror("Error", "Credenciales incorrectas")
            
            conexion.close()
        
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {err}")
    
    def cambiar_contrasena(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Cambiar Contraseña")
        ventana.geometry("300x200")
        ventana.configure(bg="#f0f0f0")
        
        tk.Label(ventana, text="Correo electrónico:", bg="#f0f0f0").pack(pady=5)
        correo_entry = tk.Entry(ventana, width=25)
        correo_entry.pack(pady=5)
        
        tk.Label(ventana, text="Nueva contraseña:", bg="#f0f0f0").pack(pady=5)
        nueva_pass_entry = tk.Entry(ventana, show="*", width=25)
        nueva_pass_entry.pack(pady=5)
        
        def guardar_nueva_pass():
            correo = correo_entry.get()
            nueva_pass = nueva_pass_entry.get()
            
            if not correo or not nueva_pass:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
                
            try:
                conexion = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="tutorias_db"
                )
                cursor = conexion.cursor()
                
                cursor.execute("UPDATE usuarios SET password = %s WHERE username = %s", (nueva_pass, correo))
                
                if cursor.rowcount > 0:
                    conexion.commit()
                    messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "Correo no encontrado")
                
                conexion.close()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"No se pudo actualizar: {err}")
        
        tk.Button(ventana, text="Guardar", command=guardar_nueva_pass, bg="#4caf50", fg="white").pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = Login(root)
    root.mainloop()