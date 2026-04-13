import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector

from core.funciones import (
    cargar_imagen,
    guardar_imagen,
    obtener_estadisticas_region,
    restar_imagenes,
    copiar_region,
    obtener_pixel,
    modificar_pixel
)


class AppProcesamiento:
    def __init__(self, root, matriz=None, titulo=None):
        self.root = root
        self.nombre_archivo = titulo
        self.root.title(f"Visualizador - {titulo}" if titulo else "Visualizador")
        self.matriz_actual = matriz
        self.modo_activo = None
        self.area_seleccionada = False
        
        self.root.geometry("800x600")
        self.root.bind_all(
            "<KP_Enter>", 
            lambda e: e.widget.event_generate("<Return>") if isinstance(e.widget, (tk.Entry, tk.Button)) else None
        )
        self.root.bind("<Escape>", lambda e: self._resetear())

        self.filtros = [
            ("Imágenes", "*.jpg *.JPG *.png *.PNG *.bmp *.BMP *.tif *.TIF *.pgm *.PGM *.raw *.RAW"), 
            ("Todos", "*")
        ]

        # --- Panel de Herramientas ---
        tb = tk.Frame(self.root, width=150, bd=1)
        tb.pack(side=tk.LEFT, fill=tk.Y)
        
        self.btn_pixel = tk.Button(tb, text="Ver Píxel", command=lambda: self._set_modo("ver_pixel", self.btn_pixel))
        self.btn_mod_pixel = tk.Button(tb, text="Modificar Píxel", command=lambda: self._set_modo("mod_pixel", self.btn_mod_pixel))
        self.btn_resta = tk.Button(tb, text="Restar Imágenes", command=self.restar)
        self.btn_selector = tk.Button(tb, text="Seleccionar Región", command=lambda: self._set_modo("selector", self.btn_selector))
        
        # Gestión de estados inicial (Botones deshabilitados hasta tener datos o ROI)
        self.btn_copiar = tk.Button(tb, text="Copiar Región", command=self.copiar, state=tk.DISABLED)
        self.btn_promedio = tk.Button(tb, text="Promedio Región", command=self.promedio, state=tk.DISABLED)
        
        for b in [self.btn_pixel, self.btn_mod_pixel, self.btn_resta, self.btn_selector, self.btn_copiar, self.btn_promedio]:
            b.pack(fill=tk.X, padx=5, pady=2)

        self.botones_herramientas = [self.btn_pixel, self.btn_mod_pixel, self.btn_selector]
        self.botones_roi = [self.btn_copiar, self.btn_promedio]
        self.botones_operaciones = [self.btn_resta]
        self.todos_los_botones = self.botones_herramientas + self.botones_roi + self.botones_operaciones

        # --- Barra de Estado ---
        self.lbl_status = tk.Label(self.root, text="Listo", anchor=tk.W)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- Menú ---
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        arch = tk.Menu(menu, tearoff=0)
        arch.add_command(label="Abrir", command=self.cargar)
        arch.add_command(label="Guardar", command=self.guardar)
        arch.add_command(label="Cerrar Imagen", command=self.cerrar_imagen)
        arch.add_separator()
        arch.add_command(label="Salir", command=self.root.quit)
        menu.add_cascade(label="Archivo", menu=arch)

        # --- Visor (Matplotlib integrado en Tkinter) ---
        f_visor = tk.Frame(self.root)
        f_visor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        
        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=f_visor)
        self.canvas_mpl.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.selector = RectangleSelector(self.ax, self._al_seleccionar, useblit=True, button=[1], interactive=True)
        self.fig.canvas.mpl_connect('button_press_event', self._al_click)

        if self.matriz_actual is not None: 
            self._dibujar()
        else:
            self.cerrar_imagen()

    def _set_modo(self, modo, btn):
        """Gestiona el modo activo de la interfaz visual y la apariencia de botones."""
        self.modo_activo = modo
        self.selector.set_visible(modo == "selector")
        self.selector.set_active(modo == "selector")
        
        for b in self.botones_herramientas: 
            b.config(relief=tk.RAISED)
        
        if btn: 
            btn.config(relief=tk.SUNKEN)

    def _resetear(self):
        """Reinicia la selección y el modo activo reseteando el visor (Ej. Botón Escape)."""
        self.area_seleccionada = False
        self.selector.extents = (0, 0, 0, 0)
        
        # Deshabilita los botones de ROI si no hay selección válida
        for b in self.botones_roi: 
            b.config(state=tk.DISABLED)
            
        self._set_modo(None, None)

    def _al_seleccionar(self, eclick, erelease):
        """Callback al finalizar selección de ROI. Habilita herramientas dependientes si la ROI es válida."""
        x1, x2, y1, y2 = self.selector.extents
        if abs(x2 - x1) < 1 or abs(y2 - y1) < 1: 
            return self._resetear()
            
        self.area_seleccionada = True
        
        # Gestión de estados: Habilita los botones de ROI
        for b in self.botones_roi: 
            b.config(state=tk.NORMAL)

    def _al_click(self, e):
        """Maneja interacciones puntuales (Ver/Modificar Píxel)."""
        if self.matriz_actual is None or e.inaxes != self.ax: 
            return
            
        x, y = int(e.xdata), int(e.ydata)
        
        try:
            if self.modo_activo == "ver_pixel":
                self.lbl_status.config(text=f"Px ({x},{y}): {obtener_pixel(self.matriz_actual, x, y)}")
            
            elif self.modo_activo == "mod_pixel":
                nv = simpledialog.askstring("Modificar", f"Valor RGB/Gris para ({x},{y}):")
                if nv:
                    val = np.fromstring(nv, sep=',', dtype=np.uint8) if self.matriz_actual.ndim == 3 else int(nv)
                    self.matriz_actual = modificar_pixel(self.matriz_actual, x, y, val)
                    self._dibujar()
                    
        except Exception as err: 
            messagebox.showerror("Error", str(err))

    def _dibujar(self):
        """Actualiza el canvas con la matriz cargada."""
        self.ax.clear()
        h, w = self.matriz_actual.shape[:2]
        self.ax.set_facecolor('#f0f0f0')
        self.ax.imshow(self.matriz_actual, cmap='gray' if self.matriz_actual.ndim == 2 else None, vmin=0, vmax=255)
        self.ax.set_xlim(-20, w + 20)
        self.ax.set_ylim(h + 20, -20)
        self.ax.axis('off')
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self._resetear()
        self.canvas_mpl.draw()

    def _pedir_raw(self, ruta):
        """
        Flujo de datos RAW y validación de integridad.
        Solicita dimensiones si la extensión es .RAW para construir correctamente la matriz.
        """
        if not ruta.upper().endswith(".RAW"): 
            return None
            
        w = simpledialog.askinteger("RAW", "Ancho:", minvalue=1)
        h = simpledialog.askinteger("RAW", "Alto:", minvalue=1) if w else None
        
        return (w, h) if h else False
    
    def _obtener_roi_validada(self):
        """
        Lógica de ROI y clipping de coordenadas para NumPy.
        Garantiza que las coordenadas se mantengan estrictamente en los límites de la matriz.
        """
        h, w = self.matriz_actual.shape[:2]
        x1, x2, y1, y2 = self.selector.extents      
        
        xm = max(0, min(w, round(x1)))
        xM = max(0, min(w, round(x2)))
        ym = max(0, min(h, round(y1)))
        yM = max(0, min(h, round(y2)))
        
        return xm, ym, xM, yM

    def cargar(self):
        """Carga en memoria una imagen y actualiza UI."""
        ruta = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta: 
            return
            
        try:
            dim = self._pedir_raw(ruta)
            if dim is False: 
                return  # Usuario canceló el diálogo RAW
                
            self.matriz_actual = cargar_imagen(ruta, *dim) if dim else cargar_imagen(ruta)
            self.nombre_archivo = os.path.basename(ruta)
            self.root.title(f"Visualizador - {self.nombre_archivo}")
            self._dibujar()
            
            # Gestión de estados: Habilita herramientas con imagen activa
            for b in self.botones_herramientas + self.botones_operaciones:
                b.config(state=tk.NORMAL)
                
            self.lbl_status.config(text=f"Imagen cargada: {self.nombre_archivo}")
            
        except Exception as e: 
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
            self.cerrar_imagen()

    def cerrar_imagen(self):
        """Limpia el visor y bloquea controles que requieren matriz cargada."""
        self.matriz_actual = None
        self.nombre_archivo = None
        self.root.title("Visualizador")
        self.ax.clear()
        self.ax.axis('off')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas_mpl.draw()
        self.lbl_status.config(text="Imagen cerrada")
        
        for b in self.todos_los_botones:
            b.config(state=tk.DISABLED)
            
        self._resetear()

    def guardar(self):
        """Vuelca la matriz en disco respetando el formato requerido."""
        if self.matriz_actual is None: 
            return
            
        try:
            h, w = self.matriz_actual.shape[:2]
            n = f"{os.path.splitext(self.nombre_archivo)[0] if self.nombre_archivo else 'img'}_{w}x{h}"
            ruta = filedialog.asksaveasfilename(initialfile=n, filetypes=self.filtros)
            
            if ruta: 
                guardar_imagen(self.matriz_actual, ruta)
                
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    def restar(self):
        """Operación de resta usando un nuevo flujo recursivo de Tkinter."""
        if self.matriz_actual is None: 
            return
            
        ruta2 = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta2: 
            return
            
        try:
            dim = self._pedir_raw(ruta2)
            if dim is False: 
                return
                
            m2 = cargar_imagen(ruta2, *dim) if dim else cargar_imagen(ruta2)
            res = restar_imagenes(self.matriz_actual, m2)
            
            # Recursividad con Toplevel para visualización paralela
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_resta")
            
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    def copiar(self):
        """Extrae la ROI actual a un visualizador paralelo."""
        if self.matriz_actual is None: 
            return
            
        try:
            coords = self._obtener_roi_validada()
            res = copiar_region(self.matriz_actual, *coords)
            
            # Recursividad con Toplevel
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_copia")
            
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    def promedio(self):
        """Opera analíticamente sobre la ROI."""
        if self.matriz_actual is None: 
            return
            
        try:
            coords = self._obtener_roi_validada()
            cant, prom = obtener_estadisticas_region(self.matriz_actual, *coords)
            self.lbl_status.config(text=f"Región: {cant}px | Promedio: {prom}")
            
        except Exception as e: 
            messagebox.showerror("Error", str(e))


def iniciar_aplicacion():
    """Punto de inicialización único de la aplicación GUI."""
    root = tk.Tk()
    AppProcesamiento(root)
    root.mainloop()