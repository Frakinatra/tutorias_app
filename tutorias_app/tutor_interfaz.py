import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar
from datetime import datetime

class InterfazTutor:
    def __init__(self, root, id_tutor):
        self.root = root
        self.id_tutor = id_tutor
        self.root.title(f"📚 Tutor - Gestión de Solicitudes (ID: {id_tutor})")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        self.id_tutor = 1  # Aquí pondrías el ID del tutor logueado

        self.centrar_ventana(700, 500)

        tk.Label(root, text="Solicitudes Pendientes", bg="#f0f0f0", font=("Arial", 14, "bold")).pack(pady=10)

        columns = ("ID Solicitud", "Estudiante", "Área", "Fecha", "Estado")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        frame_botones = tk.Frame(root, bg="#f0f0f0")
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="✅ Aceptar Solicitud", bg="#4caf50", fg="white", command=self.aceptar_solicitud).pack(padx=5, pady=5)
        tk.Button(frame_botones, text="❌ Rechazar Solicitud", bg="#f44336", fg="white", command=self.rechazar_solicitud).pack(padx=5, pady=5)
        tk.Button(frame_botones, text="📝 Completar Sesión", bg="#ff9800", fg="white", command=self.completar_sesion).pack(padx=5, pady=5)

        self.cargar_solicitudes()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cargar_solicitudes(self):
        conexion = conectar()
        cursor = conexion.cursor()
        query = """
        SELECT s.id_solicitud, e.nombre, a.nombre_area, s.fecha, s.estado
        FROM solicitudes s
        JOIN estudiantes e ON s.id_estudiante = e.id_estudiante
        JOIN areas_conocimiento a ON s.id_area = a.id_area
        WHERE s.estado = 'Pendiente'
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        conexion.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for fila in resultados:
            self.tree.insert("", "end", values=fila)

    def aceptar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona una solicitud.")
            return
        id_solicitud = self.tree.item(seleccionado[0])['values'][0]
        conexion = conectar()
        cursor = conexion.cursor()

        # Cambiar estado
        cursor.execute("UPDATE solicitudes SET estado = 'Aceptada' WHERE id_solicitud = %s", (id_solicitud,))

        # Crear sesión
        cursor.execute("""
        INSERT INTO sesiones (id_solicitud, id_tutor, fecha, estado)
        VALUES (%s, %s, %s, 'Programada')
        """, (id_solicitud, self.id_tutor, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conexion.commit()
        conexion.close()
        messagebox.showinfo("Éxito", "Solicitud aceptada y sesión programada.")
        self.cargar_solicitudes()

    def rechazar_solicitud(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona una solicitud.")
            return
        id_solicitud = self.tree.item(seleccionado[0])['values'][0]
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE solicitudes SET estado = 'Rechazada' WHERE id_solicitud = %s", (id_solicitud,))
        conexion.commit()
        conexion.close()
        messagebox.showinfo("Listo", "Solicitud rechazada.")
        self.cargar_solicitudes()

    def completar_sesion(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona una solicitud aceptada.")
            return
        id_solicitud = self.tree.item(seleccionado[0])['values'][0]

        detalle = simpledialog.askstring("Detalle de Sesión", "Escribe los detalles de la sesión:")
        if not detalle:
            return

        conexion = conectar()
        cursor = conexion.cursor()

        # Actualizar sesión
        cursor.execute("""
        UPDATE sesiones
        SET detalles = %s, estado = 'Completada'
        WHERE id_solicitud = %s AND id_tutor = %s
        """, (detalle, id_solicitud, self.id_tutor))

        conexion.commit()
        conexion.close()
        messagebox.showinfo("Listo", "Sesión completada.")
        self.cargar_solicitudes()
