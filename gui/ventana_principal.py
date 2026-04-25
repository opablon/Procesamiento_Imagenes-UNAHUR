import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import core.funciones as funciones
from gui import visualizaciones
import functools

def feedback_visual(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        AppProcesamiento.set_estado_global("Procesando...", "watch")
        try:
            return func(self, *args, **kwargs)
        finally:
            AppProcesamiento.set_estado_global("Listo", "")
    return wrapper

class AppProcesamiento:
    instancias = []

    def __init__(self, root, matriz=None, titulo=None):
        AppProcesamiento.instancias.append(self)
        self.root = root
        self.nombre_archivo = titulo
        self.root.title(f"Visualizador - {titulo}" if titulo else "Visualizador")
        self.matriz_actual = matriz
        self.modo_activo = None
        self.area_seleccionada = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.bind_all(
            "<KP_Enter>", 
            lambda e: e.widget.event_generate("<Return>") if isinstance(e.widget, (tk.Entry, tk.Button)) else None
        )
        self.root.bind("<Escape>", lambda e: self._resetear())

        self.filtros = [
            ("Imágenes", "*.jpg *.JPG *.png *.PNG *.bmp *.BMP *.tif *.TIF *.pgm *.PGM *.raw *.RAW"), 
            ("Todos", "*")
        ]

        # --- Barra de Estado ---
        self.f_status = tk.Frame(self.root)
        self.f_status.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.lbl_status = tk.Label(self.f_status, text="Listo", anchor=tk.W)
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.color_sample = tk.Frame(self.f_status, width=20, height=20, bg=self.f_status.cget("bg"), relief=tk.FLAT, borderwidth=0)
        self.color_sample.pack_propagate(False)
        self.color_sample.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # --- Menú ---
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        self.menu_archivo = tk.Menu(menu, tearoff=0)
        self.menu_archivo.add_command(label="Abrir Imagen...", command=self.cargar)
        self.menu_archivo.add_command(label="Guardar Imagen Como...", command=self.guardar)
        self.menu_archivo.add_command(label="Cerrar Imagen", command=self.cerrar_imagen)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=self.root.quit)
        menu.add_cascade(label="Archivo", menu=self.menu_archivo)

        # Menú TP0
        self.menu_tp0 = tk.Menu(menu, tearoff=0)
        self.menu_tp0.add_command(label="Ver Píxel", command=lambda: self._set_modo("ver_pixel"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Modificar Píxel", command=lambda: self._set_modo("mod_pixel"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Seleccionar Región", command=lambda: self._set_modo("selector"), state=tk.DISABLED)
        self.menu_tp0.add_command(label="Copiar Región", command=self.copiar, state=tk.DISABLED)
        self.menu_tp0.add_command(label="Promedio Región", command=self.promedio, state=tk.DISABLED)
        self.menu_tp0.add_command(label="Restar Imágenes", command=self.restar, state=tk.DISABLED)
        menu.add_cascade(label="TP0", menu=self.menu_tp0)

        # Menú TP1
        self.menu_tp1 = tk.Menu(menu, tearoff=0)
        self.menu_tp1.add_command(label="Ver Histograma", command=self.mostrar_histograma, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Transformación Potencia", command=self.transformacion_potencia, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Obtener Negativo", command=self.negativo, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Ecualizar Histograma", command=self.ecualizacion, state=tk.DISABLED)
        self.menu_tp1.add_command(label="Umbralización", command=self.umbralizacion, state=tk.DISABLED)
        
        # Submenú Ruidos
        self.menu_ruidos = tk.Menu(self.menu_tp1, tearoff=0)
        self.menu_ruidos.add_command(label="Gaussiano", command=self.ruido_gaussiano, state=tk.DISABLED)
        self.menu_ruidos.add_command(label="Exponencial", command=self.ruido_exponencial, state=tk.DISABLED)
        self.menu_ruidos.add_command(label="Sal y Pimienta", command=self.ruido_sal_pimienta, state=tk.DISABLED)
        self.menu_tp1.add_cascade(label="Ruidos", menu=self.menu_ruidos, state=tk.DISABLED)
        
        # Submenú Filtros
        self.menu_filtros = tk.Menu(self.menu_tp1, tearoff=0)
        self.menu_filtros.add_command(label="Media", command=self.filtro_media, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Mediana", command=self.filtro_mediana, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Mediana Ponderada", command=self.filtro_mediana_ponderada, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Gaussiano", command=self.filtro_gaussiano, state=tk.DISABLED)
        self.menu_filtros.add_command(label="Realce de Bordes", command=self.filtro_bordes, state=tk.DISABLED)
        self.menu_tp1.add_cascade(label="Filtros", menu=self.menu_filtros, state=tk.DISABLED)

        menu.add_cascade(label="TP1", menu=self.menu_tp1)

        # --- Visor (Matplotlib integrado en Tkinter) ---
        f_visor = tk.Frame(self.root)
        f_visor.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        
        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=f_visor)
        self.canvas_mpl.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.selector = RectangleSelector(self.ax, self._al_seleccionar, useblit=True, button=[1], interactive=True)
        self.fig.canvas.mpl_connect('button_press_event', self._al_click)

        if self.matriz_actual is not None: 
            self._cambiar_estado_menus(tk.NORMAL)
            self._dibujar()
        else:
            self.cerrar_imagen()

    def _cambiar_estado_menus(self, estado):
        """Habilita o deshabilita las opciones de procesamiento de los menús."""
        opciones_tp0 = ["Ver Píxel", "Modificar Píxel", "Seleccionar Región", "Restar Imágenes"]
        for op in opciones_tp0:
            self.menu_tp0.entryconfig(op, state=estado)
        
        opciones_tp1 = ["Ver Histograma", "Transformación Potencia", "Obtener Negativo", "Ecualizar Histograma", "Umbralización", "Ruidos", "Filtros"]
        for op in opciones_tp1:
            self.menu_tp1.entryconfig(op, state=estado)
        
        opciones_ruidos = ["Gaussiano", "Exponencial", "Sal y Pimienta"]
        for op in opciones_ruidos:
            self.menu_ruidos.entryconfig(op, state=estado)
            
        opciones_filtros = ["Media", "Mediana", "Mediana Ponderada", "Gaussiano", "Realce de Bordes"]
        for op in opciones_filtros:
            self.menu_filtros.entryconfig(op, state=estado)

    def _set_modo(self, modo):
        """Gestiona el modo activo de la interfaz visual."""
        self.modo_activo = modo
        self.selector.set_visible(modo == "selector")
        self.selector.set_active(modo == "selector")
        
        if hasattr(self, 'color_sample') and modo != "ver_pixel":
            self.color_sample.config(bg=self.f_status.cget("bg"), relief=tk.FLAT, borderwidth=0)
            
        if modo:
            AppProcesamiento.set_estado_global("Herramienta activa. ESC para salir o finalizar.", "crosshair")
        else:
            AppProcesamiento.set_estado_global("Listo", "")

    def _resetear(self):
        """Reinicia la selección y el modo activo reseteando el visor (Ej. Botón Escape)."""
        self.area_seleccionada = False
        self.selector.extents = (0, 0, 0, 0)
        
        # Deshabilita los comandos de ROI si no hay selección válida
        self.menu_tp0.entryconfig("Copiar Región", state=tk.DISABLED)
        self.menu_tp0.entryconfig("Promedio Región", state=tk.DISABLED)
            
        self._set_modo(None)

    def _al_seleccionar(self, eclick, erelease):
        """Callback al finalizar selección de ROI. Habilita herramientas dependientes si la ROI es válida."""
        x1, x2, y1, y2 = self.selector.extents
        if abs(x2 - x1) < 1 or abs(y2 - y1) < 1: 
            return self._resetear()
            
        self.area_seleccionada = True
        
        # Gestión de estados: Habilita los comandos de ROI
        self.menu_tp0.entryconfig("Copiar Región", state=tk.NORMAL)
        self.menu_tp0.entryconfig("Promedio Región", state=tk.NORMAL)

    def _al_click(self, e):
        """Maneja interacciones puntuales (Ver/Modificar Píxel)."""
        if self.matriz_actual is None or e.inaxes != self.ax: 
            return
            
        x, y = int(e.xdata), int(e.ydata)
        
        try:
            if self.modo_activo == "ver_pixel":
                val = funciones.obtener_pixel(self.matriz_actual, x, y)
                self.lbl_status.config(text=f"Coords: ({x},{y}) | Valor: {val}")
                
                if self.matriz_actual.ndim == 3:
                    hex_color = f"#{int(val[0]):02x}{int(val[1]):02x}{int(val[2]):02x}"
                else:
                    hex_color = f"#{int(val):02x}{int(val):02x}{int(val):02x}"
                    
                self.color_sample.config(bg=hex_color, relief=tk.SUNKEN, borderwidth=1)
            
            elif self.modo_activo == "mod_pixel":
                # Creamos un mensaje dinámico según los canales de la imagen
                msg = "Valor RGB (ej: 255,0,0):" if self.matriz_actual.ndim == 3 else "Valor Gris (0-255):"
                
                nv = simpledialog.askstring("Modificar", f"Px ({x},{y})\n{msg}")
                if nv:
                    val = np.fromstring(nv, sep=',', dtype=np.uint8) if self.matriz_actual.ndim == 3 else int(nv)
                    self.matriz_actual = funciones.modificar_pixel(self.matriz_actual, x, y, val)
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

    def _mostrar_ventana_grafico(self, fig, titulo):
        """Abre un Toplevel simple y muestra una figura de Matplotlib."""
        top = tk.Toplevel(self.root)
        top.title(titulo)
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def on_closing(self):
        """Protocolo de cierre de seguridad."""
        if self in self.__class__.instancias:
            self.__class__.instancias.remove(self)
            
        AppProcesamiento.set_estado_global("Listo", "")
            
        if isinstance(self.root, tk.Tk):
            self.root.quit()
            self.root.destroy()
        else:
            self.root.destroy()

    @classmethod
    def set_estado_global(cls, texto, cursor):
        for inst in cls.instancias:
            inst.root.config(cursor=cursor)
            inst.lbl_status.config(text=texto)
            inst.root.update()

    def cargar(self):
        """Carga en memoria una imagen y actualiza UI."""
        ruta = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta: 
            return
            
        try:
            dim = self._pedir_raw(ruta)
            if dim is False: 
                return  # Usuario canceló el diálogo RAW
                
            self.matriz_actual = funciones.cargar_imagen(ruta, *dim) if dim else funciones.cargar_imagen(ruta)
            self.nombre_archivo = os.path.basename(ruta)
            self.root.title(f"Visualizador - {self.nombre_archivo}")
            self._dibujar()
            
            # Gestión de estados: Habilita herramientas con imagen activa
            self._cambiar_estado_menus(tk.NORMAL)
                
            AppProcesamiento.set_estado_global("Listo", "")
            
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
        
        self._cambiar_estado_menus(tk.DISABLED)
            
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
                funciones.guardar_imagen(self.matriz_actual, ruta)
                
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    @feedback_visual
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
                
            m2 = funciones.cargar_imagen(ruta2, *dim) if dim else funciones.cargar_imagen(ruta2)
            res = funciones.restar_imagenes(self.matriz_actual, m2)
            
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
            res = funciones.copiar_region(self.matriz_actual, *coords)
            
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
            cant, prom = funciones.obtener_estadisticas_region(self.matriz_actual, *coords)
            self.lbl_status.config(text=f"Región: {cant}px | Promedio: {prom}")
            
        except Exception as e: 
            messagebox.showerror("Error", str(e))

    def transformacion_potencia(self):
        """Aclara u oscurece la imagen según el valor de Gamma."""
        if self.matriz_actual is None: return
        gamma = simpledialog.askfloat("Gamma", "Ingrese valor de Gamma (0 < gamma < 2):", minvalue=0.01, maxvalue=1.99)
        if gamma is None: return
        try:
            res = funciones.aplicar_transformacion_potencia(self.matriz_actual, gamma)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_potencia_{gamma}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def negativo(self):
        """Genera la imagen negativa."""
        if self.matriz_actual is None: return
        try:
            res = funciones.obtener_negativo(self.matriz_actual)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_negativo")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def ecualizacion(self):
        """Aplica ecualización global de histograma."""
        if self.matriz_actual is None: return
        try:
            res = funciones.ecualizar_histograma(self.matriz_actual)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_ecualizado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_histograma(self):
        """Muestra el histograma de la imagen actual."""
        if self.matriz_actual is None: 
            return
        try:
            histograma = funciones.obtener_histograma_gris(self.matriz_actual)
            fig = visualizaciones.preparar_histograma(histograma)
            self._mostrar_ventana_grafico(fig, "Histograma")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ruido_gaussiano(self):
        """Aplica ruido gaussiano."""
        if self.matriz_actual is None: return
        densidad = simpledialog.askfloat("Densidad", "Densidad de ruido (0-100):", minvalue=0, maxvalue=100)
        if densidad is None: return
        sigma = simpledialog.askfloat("Sigma", "Desvío estándar (sigma):", minvalue=0)
        if sigma is None: return
        try:
            res = funciones.aplicar_ruido_aditivo_gaussiano(self.matriz_actual, densidad, sigma)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_r_gauss")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ruido_exponencial(self):
        """Aplica ruido exponencial."""
        if self.matriz_actual is None: return
        porcentaje = simpledialog.askfloat("Porcentaje", "Porcentaje de ruido (0-100):", minvalue=0, maxvalue=100)
        if porcentaje is None: return
        lambd = simpledialog.askfloat("Lambda", "Parámetro lambda (>0):", minvalue=0.0001)
        if lambd is None: return
        try:
            res = funciones.aplicar_ruido_multiplicativo_exponencial(self.matriz_actual, porcentaje, lambd)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_r_exp")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ruido_sal_pimienta(self):
        """Aplica ruido Sal y Pimienta."""
        if self.matriz_actual is None: return
        densidad = simpledialog.askfloat("Densidad", "Densidad de ruido (0-100):", minvalue=0, maxvalue=100)
        if densidad is None: return
        try:
            res = funciones.aplicar_ruido_sal_y_pimienta(self.matriz_actual, densidad)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_r_sp")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def filtro_media(self):
        """Aplica Filtro de la Media."""
        if self.matriz_actual is None: return
        tamano = simpledialog.askinteger("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is None: return
        try:
            res = funciones.aplicar_filtro_media(self.matriz_actual, tamano)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_f_media")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def filtro_mediana(self):
        """Aplica Filtro de la Mediana."""
        if self.matriz_actual is None: return
        tamano = simpledialog.askinteger("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is None: return
        try:
            res = funciones.aplicar_filtro_mediana(self.matriz_actual, tamano)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_f_mediana")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def filtro_mediana_ponderada(self):
        """Aplica Filtro de la Mediana Ponderada."""
        if self.matriz_actual is None: return
        tamano = simpledialog.askinteger("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is None: return
        try:
            res = funciones.aplicar_filtro_mediana_ponderada(self.matriz_actual, tamano)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_f_med_pond")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def filtro_gaussiano(self):
        """Aplica Filtro Gaussiano."""
        if self.matriz_actual is None: return
        sigma = simpledialog.askfloat("Sigma", "Desvío estándar (sigma > 0):", minvalue=0.01)
        if sigma is None: return
        try:
            res = funciones.aplicar_filtro_gaussiano(self.matriz_actual, sigma)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_f_gauss")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def filtro_bordes(self):
        """Aplica Filtro Realce de Bordes."""
        if self.matriz_actual is None: return
        tamano = simpledialog.askinteger("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is None: return
        try:
            res = funciones.aplicar_filtro_realce_de_bordes(self.matriz_actual, tamano)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_f_bordes")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @feedback_visual
    def umbralizacion(self):
        """Aplica Umbralización."""
        if self.matriz_actual is None: return
        umbral = simpledialog.askinteger("Umbral", "Valor de umbral (0-255):", minvalue=0, maxvalue=255)
        if umbral is None: return
        try:
            res = funciones.obtener_umbralizacion(self.matriz_actual, umbral)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_umbral")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def iniciar_aplicacion():
    """Punto de inicialización único de la aplicación GUI."""
    root = tk.Tk()
    AppProcesamiento(root)
    try:
        root.mainloop()
    finally:
        # Forzamos la limpieza al salir del bucle de eventos
        plt.close('all') 
        sys.exit(0)