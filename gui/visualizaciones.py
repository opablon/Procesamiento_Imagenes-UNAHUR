import matplotlib.pyplot as plt

def preparar_histograma(histograma, titulo="Histograma de Niveles de Gris"):
    """
    Crea una figura con el histograma para ser incrustada en la GUI.
    Recibe el array del histograma (calculado en funciones.py).
    """
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    
    ax.bar(range(256), histograma, color='gray', width=1.0)
    ax.set_title(titulo)
    ax.set_xlabel("Nivel de gris")
    ax.set_ylabel("Frecuencia relativa")
    ax.grid(alpha=0.3)
    
    fig.tight_layout()
    return fig # DEVOLVEMOS LA FIGURA