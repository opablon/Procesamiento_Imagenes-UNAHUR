import tkinter as tk
from typing import Callable, Dict, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector


def preparar_histograma(
    histograma: Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    titulo: str = "Histograma"
) -> Figure:
    """
    Crea una figura con el histograma para ser incrustada en la GUI.
    Se adapta dinámicamente al tamaño del array de entrada para soportar histogramas universales.
    Soporta histogramas individuales por canales (RGB) pasados como una tupla.
    """
    # Fondo oscuro para que haga juego con CustomTkinter dark mode
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

    if isinstance(histograma, tuple):
        # Histograma RGB: graficamos cada canal con su respectivo color y transparencia
        hist_r, hist_g, hist_b = histograma
        num_niveles = len(hist_r)
        ax.bar(range(num_niveles), hist_r, color="red", width=1.0, edgecolor="red", alpha=0.4, label="Rojo")
        ax.bar(range(num_niveles), hist_g, color="green", width=1.0, edgecolor="green", alpha=0.4, label="Verde")
        ax.bar(range(num_niveles), hist_b, color="blue", width=1.0, edgecolor="blue", alpha=0.4, label="Azul")
        ax.legend(facecolor="#2b2b2b", edgecolor="white", labelcolor="white")
    else:
        # Histograma de escala de grises / genérico
        num_niveles = len(histograma)
        ax.bar(range(num_niveles), histograma, color="#1f6aa5", width=1.0, edgecolor="#1f6aa5", alpha=0.9)  # CTk blue

    ax.set_xlabel("Nivel / Valor")
    ax.set_ylabel("Frecuencia relativa")

    # Ajustamos los límites de la caja para evitar espacios vacíos en los extremos del gráfico
    ax.set_xlim(-1, num_niveles)

    # Configuración explícita del eje X para que muestre 255 en lugar de quedarse en 250
    if num_niveles == 256:
        ax.set_xticks([0, 50, 100, 150, 200, 255])
    else:
        ticks = list(range(0, num_niveles, max(1, num_niveles // 5)))
        if (num_niveles - 1) not in ticks:
            ticks.append(num_niveles - 1)
        ax.set_xticks(ticks)

    ax.grid(alpha=0.2, color="white", linestyle='--')

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
