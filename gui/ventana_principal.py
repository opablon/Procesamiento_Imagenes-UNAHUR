import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
import numpy as np
import os
from core.funciones import (cargar_imagen, guardar_imagen, obtener_estadisticas_region, restar_imagenes, copiar_region, obtener_pixel, modificar_pixel)

class AppProcesamiento:
    def __init__(self, root, matriz=None, titulo=None):
        self.root = root
        self.nombre_archivo = titulo
        self.root.title(f"Visualizador - {titulo}" if titulo else "Visualizador")
        self.matriz_actual = matriz
        self.modo_activo = None
        self.area_seleccionada = False
        
        self.root.geometry("800x600")
        self.root.bind_all("<KP_Enter>", lambda e: e.widget.event_generate("<Return>") if isinstance(e.widget, (tk.Entry, tk.Button)) else None)
        self.root.bind("<Escape>", lambda e: self._resetear())

        self.filtros = [("Imágenes", "*.jpg *.png *.bmp *.tif *.pgm *.raw"), ("Todos", "*")]

        tb = tk.Frame(self.root, width=150, bd=1)
        tb.pack(side=tk.LEFT, fill=tk.Y)
        
        self.btn_pixel = tk.Button(tb, text="Ver Píxel", command=lambda: self._set_modo("ver_pixel", self.btn_pixel))
        self.btn_mod_pixel = tk.Button(tb, text="Modificar Píxel", command=lambda: self._set_modo("mod_pixel", self.btn_mod_pixel))
        self.btn_resta = tk.Button(tb, text="Restar Imágenes", command=self.restar)
        self.btn_selector = tk.Button(tb, text="Seleccionar Región", command=lambda: self._set_modo("selector", self.btn_selector))
        self.btn_copiar = tk.Button(tb, text="Copiar Región", command=self.copiar, state=tk.DISABLED)
        self.btn_promedio = tk.Button(tb, text="Promedio Región", command=self.promedio, state=tk.DISABLED)
        
        for b in [self.btn_pixel, self.btn_mod_pixel, self.btn_resta, self.btn_selector, self.btn_copiar, self.btn_promedio]:
            b.pack(fill=tk.X, padx=5, pady=2)

        self.lbl_status = tk.Label(self.root, text="Listo", anchor=tk.W)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)
        
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        arch = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Archivo", menu=arch)
        arch.add_command(label="Abrir", command=self.cargar)
        arch.add_command(label="Guardar", command=self.guardar)
        arch.add_command(label="Cerrar", command=lambda: self.cargar(cerrar=True))
        
        f_visor = tk.Frame(self.root)
        f_visor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        
        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=f_visor)
        self.canvas_mpl.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.selector = RectangleSelector(self.ax, self._al_seleccionar, useblit=True, button=[1], interactive=True)
        self.fig.canvas.mpl_connect('button_press_event', self._al_click)

        if self.matriz_actual is not None: self._dibujar()
        self._resetear()

    def _set_modo(self, modo, btn):
        self.modo_activo = modo
        self.selector.set_visible(modo == "selector")
        self.selector.set_active(modo == "selector")
        for b in [self.btn_pixel, self.btn_mod_pixel, self.btn_selector]: b.config(relief=tk.RAISED)
        if btn: btn.config(relief=tk.SUNKEN)

    def _resetear(self):
        self.area_seleccionada = False
        self.selector.extents = (0, 0, 0, 0)
        self.btn_copiar.config(state=tk.DISABLED)
        self.btn_promedio.config(state=tk.DISABLED)
        self._set_modo(None, None)

    def _al_seleccionar(self, eclick, erelease):
        x1, x2, y1, y2 = self.selector.extents
        if abs(x2-x1)<1 or abs(y2-y1)<1: return self._resetear()
        self.area_seleccionada = True
        self.btn_copiar.config(state=tk.NORMAL)
        self.btn_promedio.config(state=tk.NORMAL)

    def _al_click(self, e):
        if self.matriz_actual is None or e.inaxes != self.ax: return
        x, y = int(e.xdata), int(e.ydata)
        try:
            if self.modo_activo == "ver_pixel":
                self.lbl_status.config(text=f"Px ({x},{y}): {obtener_pixel(self.matriz_actual, x, y)}")
            elif self.modo_activo == "mod_pixel":
                nv = simpledialog.askstring("Modificar", f"Valor RGB/Gris para ({x},{y}):")
                if nv:
                    val = np.fromstring(nv, sep=',', dtype=np.uint8) if self.matriz_actual.ndim==3 else int(nv)
                    self.matriz_actual = modificar_pixel(self.matriz_actual, x, y, val)
                    self._dibujar()
        except Exception as err: messagebox.showerror("Error", str(err))

    def _dibujar(self):
        self.ax.clear()
        h, w = self.matriz_actual.shape[:2]
        self.ax.set_facecolor('#f0f0f0')
        self.ax.imshow(self.matriz_actual, cmap='gray' if self.matriz_actual.ndim==2 else None, vmin=0, vmax=255)
        self.ax.set_xlim(-20, w + 20)
        self.ax.set_ylim(h + 20, -20)
        self.ax.axis('off')
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self._resetear()
        self.canvas_mpl.draw()

    def _pedir_raw(self, ruta):
        if not ruta.upper().endswith(".RAW"): return None
        w = simpledialog.askinteger("RAW", "Ancho:", minvalue=1)
        h = simpledialog.askinteger("RAW", "Alto:", minvalue=1) if w else None
        return (w, h) if h else False

    def cargar(self, cerrar=False):
        if cerrar:
            self.matriz_actual, self.nombre_archivo = None, None
            self.root.title("Visualizador")
            self.ax.clear()
            self.canvas_mpl.draw()
            return
        ruta = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta: return
        try:
            dim = self._pedir_raw(ruta)
            if dim is False: return
            self.matriz_actual = cargar_imagen(ruta, *dim) if dim else cargar_imagen(ruta)
            self.nombre_archivo = os.path.basename(ruta)
            self.root.title(f"Visualizador - {self.nombre_archivo}")
            self._dibujar()
        except Exception as e: messagebox.showerror("Error", str(e))

    def guardar(self):
        if self.matriz_actual is None: return
        try:
            h, w = self.matriz_actual.shape[:2]
            n = f"{os.path.splitext(self.nombre_archivo)[0] if self.nombre_archivo else 'img'}_{w}x{h}"
            ruta = filedialog.asksaveasfilename(initialfile=n, filetypes=self.filtros)
            if ruta: guardar_imagen(self.matriz_actual, ruta)
        except Exception as e: messagebox.showerror("Error", str(e))

    def restar(self):
        if self.matriz_actual is None: return
        ruta2 = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta2: return
        try:
            dim = self._pedir_raw(ruta2)
            if dim is False: return
            m2 = cargar_imagen(ruta2, *dim) if dim else cargar_imagen(ruta2)
            res = restar_imagenes(self.matriz_actual, m2)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_resta")
        except Exception as e: messagebox.showerror("Error", str(e))

    def copiar(self):
        if self.matriz_actual is None: return
        try:
            h, w = self.matriz_actual.shape[:2]
            x1, x2, y1, y2 = self.selector.extents
            xm, xM = max(0, min(w, round(x1))), max(0, min(w, round(x2)))
            ym, yM = max(0, min(h, round(y1))), max(0, min(h, round(y2)))
            res = copiar_region(self.matriz_actual, xm, ym, xM, yM)
            AppProcesamiento(tk.Toplevel(self.root), res, f"{self.nombre_archivo}_copia")
        except Exception as e: messagebox.showerror("Error", str(e))

    def promedio(self):
        if self.matriz_actual is None: return
        try:
            h, w = self.matriz_actual.shape[:2]
            x1, x2, y1, y2 = self.selector.extents
            xm, xM = max(0, min(w, round(x1))), max(0, min(w, round(x2)))
            ym, yM = max(0, min(h, round(y1))), max(0, min(h, round(y2)))
            cant, prom = obtener_estadisticas_region(self.matriz_actual, xm, ym, xM, yM)
            self.lbl_status.config(text=f"Región: {cant}px | Promedio: {prom}")
        except Exception as e: messagebox.showerror("Error", str(e))

def iniciar_aplicacion():
    root = tk.Tk()
    AppProcesamiento(root)
    root.mainloop()