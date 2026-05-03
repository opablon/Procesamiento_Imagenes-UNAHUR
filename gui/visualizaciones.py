import tkinter as tk
from typing import Callable, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector


def preparar_histograma(histograma: np.ndarray, titulo: str = "Histograma de Niveles de Gris") -> Figure:
    """
    Crea una figura con el histograma para ser incrustada en la GUI.
    Recibe el array del histograma (calculado en funciones.py).
    """
    # Usaremos fondo oscuro para que haga juego con CustomTkinter dark mode
    fig = plt.figure(figsize=(6, 4))
    fig.patch.set_facecolor("#2b2b2b")  # CTk dark bg

    ax = fig.add_subplot(111)
    ax.set_facecolor("#2b2b2b")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")

    ax.bar(range(256), histograma, color="#1f6aa5", width=1.0)  # CTk blue
    ax.set_title(titulo)
    ax.set_xlabel("Nivel de gris")
    ax.set_ylabel("Frecuencia relativa")
    ax.grid(alpha=0.2, color="white")

    fig.tight_layout()
    return fig


class VisorMatplotlib:
    """Encapsula la configuración y lógica de dibujo de Matplotlib."""

    def __init__(self, master_widget: tk.Widget, callbacks: Dict[str, Callable]) -> None:
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor("#2b2b2b")  # CTk dark background
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#2b2b2b")
        self.ax.axis("off")

        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=master_widget)
        self.canvas_mpl.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.selector = RectangleSelector(
            self.ax, callbacks["al_seleccionar"], useblit=True, button=MouseButton.LEFT, interactive=True
        )
        self.selector.set_visible(False)
        self.selector.set_active(False)
        self.fig.canvas.mpl_connect("button_press_event", callbacks["al_click"])

    def dibujar(self, matriz: np.ndarray) -> None:
        self.ax.clear()
        h, w = matriz.shape[:2]
        self.ax.set_facecolor("#2b2b2b")
        self.ax.imshow(matriz, cmap="gray" if matriz.ndim == 2 else None, vmin=0, vmax=255)
        self.ax.set_xlim(-20, w + 20)
        self.ax.set_ylim(h + 20, -20)
        self.ax.axis("off")
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.canvas_mpl.draw()

    def limpiar(self) -> None:
        self.ax.clear()
        self.ax.set_facecolor("#2b2b2b")
        self.ax.axis("off")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas_mpl.draw()

    def set_modo_selector(self, activo: bool) -> None:
        self.selector.set_active(activo)
        if activo:
            # Solo mostrar si ya hay una selección válida previa
            x1, x2, y1, y2 = self.selector.extents
            if abs(x2 - x1) > 0.1 or abs(y2 - y1) > 0.1:
                self.selector.set_visible(True)
            else:
                self.selector.set_visible(False)
        else:
            self.selector.set_visible(False)
        self.canvas_mpl.draw()

    def resetear_selector(self) -> None:
        self.selector.extents = (0, 0, 0, 0)

    def obtener_extents_selector(self) -> Tuple[float, float, float, float]:
        return self.selector.extents
