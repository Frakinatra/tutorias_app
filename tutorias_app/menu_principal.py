import tkinter as tk
from alta_usuario import AltaUsuario
from estudiante_interfaz import InterfazEstudiante
from tutor_interfaz import InterfazTutor
from gestion_areas import GestionAreas
from gestion_sesiones import GestionSesiones
from gestion_usuarios import GestionUsuarios

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Gestión de Tutorías Académicas - Administrador")
        self.root.configure(bg="#e3f2fd")
        self.centrar_ventana(450, 600)

        # Título
        titulo = tk.Label(self.root, text="📚 Tutorías Académicas", font=("Helvetica", 22, "bold"),
                        bg="#e3f2fd", fg="#0d47a1")
        titulo.pack(pady=30)

        # Botones del menú
        botones = [
            ("➕ Alta de Usuarios", self.abrir_alta_usuario, "#4caf50"),
            ("🎓 Interfaz de Estudiantes", self.abrir_estudiante_interfaz, "#2196f3"),
            ("👨‍🏫 Interfaz de Tutores", self.abrir_tutor_interfaz, "#ff9800"),
            ("📖 Gestión de Áreas", self.abrir_gestion_areas, "#8bc34a"),
            ("📆 Gestión de Sesiones", self.abrir_gestion_sesiones, "#9c27b0"),
            ("👥 Gestión de Usuarios", self.abrir_gestion_usuarios, "#e91e63"),
            ("❌ Salir", self.root.quit, "#f44336"),
        ]

        for texto, comando, color in botones:
            boton = tk.Button(self.root, text=texto, command=comando, width=30, height=2,
                            bg=color, fg="white", font=("Helvetica", 12))
            boton.pack(pady=8)

    def abrir_alta_usuario(self):
        ventana = tk.Toplevel(self.root)
        AltaUsuario(ventana)

    def abrir_estudiante_interfaz(self):
        ventana = tk.Toplevel(self.root)
        InterfazEstudiante(ventana, id_estudiante=1)  # ID de prueba para tests desde administrador

    def abrir_tutor_interfaz(self):
        ventana = tk.Toplevel(self.root)
        InterfazTutor(ventana)

    def abrir_gestion_areas(self):
        ventana = tk.Toplevel(self.root)
        GestionAreas(ventana)

    def abrir_gestion_sesiones(self):
        ventana = tk.Toplevel(self.root)
        GestionSesiones(ventana)

    def abrir_gestion_usuarios(self):
        ventana = tk.Toplevel(self.root)
        GestionUsuarios(ventana)

    def centrar_ventana(self, ancho, alto):
        self.root.update_idletasks()
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

# Ejemplo de uso
if __name__ == '__main__':
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()
