import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from conexion import conectar
import mysql.connector

class GestionAreas:
    def __init__(self, root):
        self.root = root
        self.root.title("📖 Gestión de Áreas de Conocimiento")
        self.root.geometry("800x500")
        self.root.configure(bg="#f0f0f0")
        
        self.centrar_ventana(800, 500)
        self.configurar_estilos()
        self.crear_widgets()
        self.cargar_areas()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 10), padding=6)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Frame para agregar áreas
        add_frame = tk.Frame(main_frame, bg="#f0f0f0")
        add_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(add_frame, text="Nueva Área:", bg="#f0f0f0").pack(side="left", padx=(0, 10))
        
        self.area_entry = tk.Entry(add_frame, width=40)
        self.area_entry.pack(side="left", padx=(0, 10))
        
        add_btn = tk.Button(add_frame, text="➕ Agregar", command=self.agregar_area, 
                           bg="#4caf50", fg="white", padx=10)
        add_btn.pack(side="left")

        # Treeview para mostrar áreas
        tree_frame = tk.Frame(main_frame, bg="#f0f0f0")
        tree_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Área"), show="headings")
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Área", text="Área de Conocimiento", anchor="center")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Área", width=400, anchor="w")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame para botones de acción
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        edit_btn = tk.Button(btn_frame, text="✏️ Modificar", command=self.modificar_area,
                            bg="#2196f3", fg="white", padx=10)
        edit_btn.pack(side="left", padx=(0, 10))
        
        delete_btn = tk.Button(btn_frame, text="🗑️ Eliminar", command=self.eliminar_area,
                              bg="#f44336", fg="white", padx=10)
        delete_btn.pack(side="left")

    def cargar_areas(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_area, nombre_area FROM areas_conocimiento ORDER BY nombre_area")
            areas = cursor.fetchall()
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Agregar áreas al treeview
            for area in areas:
                self.tree.insert("", "end", values=area)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudieron cargar las áreas: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def agregar_area(self):
        nombre_area = self.area_entry.get().strip()
        
        if not nombre_area:
            messagebox.showwarning("Advertencia", "Debes ingresar un nombre para el área")
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Verificar si el área ya existe
            cursor.execute("SELECT nombre_area FROM areas_conocimiento WHERE nombre_area = %s", (nombre_area,))
            if cursor.fetchone():
                messagebox.showwarning("Advertencia", f"El área '{nombre_area}' ya existe")
                return
                
            # Insertar nueva área
            cursor.execute("INSERT INTO areas_conocimiento (nombre_area) VALUES (%s)", (nombre_area,))
            conexion.commit()
            
            messagebox.showinfo("Éxito", f"Área '{nombre_area}' creada correctamente")
            self.area_entry.delete(0, tk.END)
            self.cargar_areas()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo crear el área: {err}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def eliminar_area(self):
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Debes seleccionar un área para eliminar")
            return
            
        id_area, nombre_area = self.tree.item(seleccion[0])['values']
        
        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el área '{nombre_area}'?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if not confirmacion:
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Verificar si el área está en uso
            cursor.execute("SELECT COUNT(*) FROM tutores_areas WHERE id_area = %s", (id_area,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Advertencia",
                    f"No se puede eliminar el área '{nombre_area}'\n\n"
                    "Está asignada a uno o más tutores."
                )
                return
                
            # Eliminar el área
            cursor.execute("DELETE FROM areas_conocimiento WHERE id_area = %s", (id_area,))
            conexion.commit()
            
            messagebox.showinfo("Éxito", f"Área '{nombre_area}' eliminada correctamente")
            self.cargar_areas()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar el área: {err}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

    def modificar_area(self):
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Debes seleccionar un área para modificar")
            return
            
        id_area, nombre_actual = self.tree.item(seleccion[0])['values']
        
        nuevo_nombre = simpledialog.askstring(
            "Modificar Área",
            "Ingrese el nuevo nombre para el área:",
            initialvalue=nombre_actual
        )
        
        if not nuevo_nombre or nuevo_nombre == nombre_actual:
            return
            
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            # Verificar si el nuevo nombre ya existe
            cursor.execute("SELECT nombre_area FROM areas_conocimiento WHERE nombre_area = %s AND id_area != %s", 
                          (nuevo_nombre, id_area))
            if cursor.fetchone():
                messagebox.showwarning("Advertencia", f"El área '{nuevo_nombre}' ya existe")
                return
                
            # Actualizar el área
            cursor.execute("UPDATE areas_conocimiento SET nombre_area = %s WHERE id_area = %s", 
                         (nuevo_nombre, id_area))
            conexion.commit()
            
            messagebox.showinfo("Éxito", f"Área actualizada correctamente:\n\n"
                                      f"Antes: {nombre_actual}\n"
                                      f"Ahora: {nuevo_nombre}")
            self.cargar_areas()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo modificar el área: {err}")
            if 'conexion' in locals() and conexion.is_connected():
                conexion.rollback()
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionAreas(root)
    root.mainloop()