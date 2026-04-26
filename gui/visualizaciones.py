import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import tkinter as tk

def preparar_histograma(histograma, titulo="Histograma de Niveles de Gris"):
    """
    Crea una figura con el histograma para ser incrustada en la GUI.
    Recibe el array del histograma (calculado en funciones.py).
    """
    # Convertimos la frecuencia absoluta a relativa para el gráfico
    frecuencia_relativa = histograma / sum(histograma)
    
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    
    ax.bar(range(256), frecuencia_relativa, color='gray', width=1.0)
    ax.set_title(titulo)
    ax.set_xlabel("Nivel de gris")
    ax.set_ylabel("Frecuencia relativa")
    ax.grid(alpha=0.3)
    
    fig.tight_layout()
    return fig

class VisorMatplotlib:
    """Encapsula la configuración y lógica de dibujo de Matplotlib."""
    def __init__(self, master_widget, callbacks):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        
        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=master_widget)
        self.canvas_mpl.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.selector = RectangleSelector(
            self.ax, callbacks.get('al_seleccionar'), 
            useblit=True, button=[1], interactive=True
        )
        self.fig.canvas.mpl_connect('button_press_event', callbacks.get('al_click'))
        
    def dibujar(self, matriz):
        self.ax.clear()
        h, w = matriz.shape[:2]
        self.ax.set_facecolor('#f0f0f0')
        self.ax.imshow(matriz, cmap='gray' if matriz.ndim == 2 else None, vmin=0, vmax=255)
        self.ax.set_xlim(-20, w + 20)
        self.ax.set_ylim(h + 20, -20)
        self.ax.axis('off')
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.canvas_mpl.draw()
        
    def limpiar(self):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas_mpl.draw()
        
    def set_modo_selector(self, activo):
        self.selector.set_visible(activo)
        self.selector.set_active(activo)
        
    def resetear_selector(self):
        self.selector.extents = (0, 0, 0, 0)
        
    def obtener_extents_selector(self):
        return self.selector.extents