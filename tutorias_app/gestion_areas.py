import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar

class GestionAreas:
    def __init__(self, root):
        self.root = root
        self.root.title("📖 Gestión de Áreas de Conocimiento")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        self.centrar_ventana(600, 400)

        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(pady=10)

        self.area_entry = tk.Entry(frame, width=30)
        self.area_entry.grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Agregar", command=self.agregar_area, bg="#4caf50", fg="white").grid(row=0, column=1, padx=5)

        self.tree = ttk.Treeview(root, columns=("ID", "Área"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Área", text="Área de Conocimiento")
        self.tree.pack(pady=10, fill="both", expand=True)

        botones = tk.Frame(root, bg="#f0f0f0")
        botones.pack(pady=5)
        tk.Button(botones, text="Eliminar", command=self.eliminar_area, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(botones, text="Modificar", command=self.modificar_area, bg="#ff9800", fg="white").pack(side="left", padx=5)

        self.cargar_areas()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cargar_areas(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento")
        rows = cursor.fetchall()
        conexion.close()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def agregar_area(self):
        area = self.area_entry.get()
        if not area:
            messagebox.showwarning("Atención", "Escribe un nombre de área.")
            return

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO areas_conocimiento (nombre_area) VALUES (%s)", (area,))
        conexion.commit()
        conexion.close()
        self.area_entry.delete(0, tk.END)
        self.cargar_areas()

    def eliminar_area(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un área para eliminar.")
            return

        id_area = self.tree.item(seleccionado[0])['values'][0]
        confirmacion = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de eliminar esta área?")
        if not confirmacion:
            return

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM areas_conocimiento WHERE id_area = %s", (id_area,))
        conexion.commit()
        conexion.close()
        self.cargar_areas()

    def modificar_area(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un área para modificar.")
            return

        id_area, nombre_actual = self.tree.item(seleccionado[0])['values']

        nuevo_nombre = simpledialog.askstring("Modificar Área", "Nuevo nombre:", initialvalue=nombre_actual)
        if not nuevo_nombre:
            return

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE areas_conocimiento SET nombre_area = %s WHERE id_area = %s", (nuevo_nombre, id_area))
        conexion.commit()
        conexion.close()
        self.cargar_areas()
