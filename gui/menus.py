import tkinter as tk

class GestorMenus:
    def __init__(self, menu_parent, app):
        """
        Construye la barra de menús principal y delega los comandos a la app.
        """
        self.app = app
        
        self.menu_archivo = tk.Menu(menu_parent, tearoff=0)
        self.menu_archivo.add_command(label="Abrir Imagen...", command=self.app.cargar)
        self.menu_archivo.add_command(label="Guardar Imagen Como...", command=self.app.guardar)
        self.menu_archivo.add_command(label="Cerrar Imagen", command=self.app.cerrar_imagen)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=self.app.root.quit)
        menu_parent.add_cascade(label="Archivo", menu=self.menu_archivo)

        # Menú TP0
        self.menu_tp0 = tk.Menu(menu_parent, tearoff=0)
        self.menu_tp0.add_command(label="Ver Píxel", command=lambda: self.app._set_modo("ver_pixel"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Modificar Píxel", command=lambda: self.app._set_modo("mod_pixel"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Seleccionar Región", command=lambda: self.app._set_modo("selector"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Copiar Región", command=self.app.copiar, state=tk.DISABLED)
        self.menu_tp0.add_command(label="Promedio Región", command=self.app.promedio, state=tk.DISABLED)
        self.menu_tp0.add_command(label="Restar Imágenes", command=self.app.restar, state=tk.DISABLED)
        menu_parent.add_cascade(label="TP0", menu=self.menu_tp0)

        # Menú TP1
        self.menu_tp1 = tk.Menu(menu_parent, tearoff=0)
        self.menu_tp1.add_command(label="Ver Histograma", command=self.app.mostrar_histograma, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Transformación Potencia", command=self.app.transformacion_potencia, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Obtener Negativo", command=self.app.negativo, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Ecualizar Histograma", command=self.app.ecualizacion, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Umbralización", command=self.app.umbralizacion, state=tk.DISABLED)
        
        # Submenú Ruidos
        self.menu_ruidos = tk.Menu(self.menu_tp1, tearoff=0)
        self.menu_ruidos.add_command(label="Gaussiano", command=self.app.ruido_gaussiano, state=tk.DISABLED)
        self.menu_ruidos.add_command(label="Exponencial", command=self.app.ruido_exponencial, state=tk.DISABLED)
        self.menu_ruidos.add_command(label="Sal y Pimienta", command=self.app.ruido_sal_pimienta, state=tk.DISABLED)
        self.menu_tp1.add_cascade(label="Ruidos", menu=self.menu_ruidos, state=tk.DISABLED)
        
        # Submenú Filtros
        self.menu_filtros = tk.Menu(self.menu_tp1, tearoff=0)
        self.menu_filtros.add_command(label="Media", command=self.app.filtro_media, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Mediana", command=self.app.filtro_mediana, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Mediana Ponderada", command=self.app.filtro_mediana_ponderada, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Gaussiano", command=self.app.filtro_gaussiano, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Realce de Bordes", command=self.app.filtro_bordes, state=tk.DISABLED)
        self.menu_tp1.add_cascade(label="Filtros", menu=self.menu_filtros, state=tk.DISABLED)

        menu_parent.add_cascade(label="TP1", menu=self.menu_tp1)

    def cambiar_estado(self, estado):
        """Habilita o deshabilita las opciones principales según el estado."""
        opciones_tp0 = ["Ver Píxel", "Modificar Píxel", "Seleccionar Región", "Restar Imágenes"]
        for op in opciones_tp0:
            self.menu_tp0.entryconfig(op, state=estado)
        
        opciones_tp1 = ["Ver Histograma", "Transformación Potencia", "Obtener Negativo", "Ecualizar Histograma", "Umbralización", "Ruidos", "Filtros"]
        for op in opciones_tp1:
            self.menu_tp1.entryconfig(op, state=estado)
        
        for op in ["Gaussiano", "Exponencial", "Sal y Pimienta"]:
            self.menu_ruidos.entryconfig(op, state=estado)
            
        for op in ["Media", "Mediana", "Mediana Ponderada", "Gaussiano", "Realce de Bordes"]:
            self.menu_filtros.entryconfig(op, state=estado)
            
    def cambiar_estado_roi(self, estado):
        """Habilita o deshabilita herramientas que dependen de la selección."""
        self.menu_tp0.entryconfig("Copiar Región", state=estado)
        self.menu_tp0.entryconfig("Promedio Región", state=estado)
