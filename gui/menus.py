import tkinter as tk
from typing import TYPE_CHECKING

import customtkinter as ctk

if TYPE_CHECKING:
    from gui.ventana_principal import AppProcesamiento


class GestorMenus:
    def __init__(self, header_frame: ctk.CTkFrame, app: "AppProcesamiento") -> None:
        """
        Construye la barra de navegación superior (Header) usando CustomTkinter.
        """
        self.app = app
        self.header_frame = header_frame

        # Menú Archivo
        self.var_archivo = ctk.StringVar(value="Archivo")
        self.menu_archivo = ctk.CTkOptionMenu(
            self.header_frame,
            values=["Abrir Imagen...", "Guardar Imagen Como...", "Cerrar Imagen", "Salir"],
            command=self._handler_archivo,
            variable=self.var_archivo,
            width=120,
        )
        self.menu_archivo.pack(side=tk.LEFT, padx=5, pady=5)

        # Menú TP0
        self.base_tp0 = ["Ver Píxel", "Modificar Píxel", "Seleccionar Región", "Restar Imágenes"]
        self.roi_tp0 = ["Copiar Región", "Promedio Región"]

        self.var_tp0 = ctk.StringVar(value="TP0")
        self.menu_tp0 = ctk.CTkOptionMenu(
            self.header_frame,
            values=self.base_tp0,
            command=self._handler_tp0,
            variable=self.var_tp0,
            width=140,
            state=tk.DISABLED,
        )
        self.menu_tp0.pack(side=tk.LEFT, padx=5, pady=5)

        # Menú TP1
        self.var_tp1 = ctk.StringVar(value="TP1")
        self.menu_tp1 = ctk.CTkOptionMenu(
            self.header_frame,
            values=[
                "Ver Histograma",
                "Transformación Potencia",
                "Obtener Negativo",
                "Ecualizar Histograma",
                "Umbralización",
                "Filtro: Media",
                "Filtro: Mediana",
                "Filtro: Mediana Ponderada",
                "Filtro: Gaussiano",
                "Filtro: Realce de Bordes",
                "Ruido: Gaussiano",
                "Ruido: Exponencial",
                "Ruido: Sal y Pimienta",
            ],
            command=self._handler_tp1,
            variable=self.var_tp1,
            width=220,
            state=tk.DISABLED,
        )
        self.menu_tp1.pack(side=tk.LEFT, padx=5, pady=5)

    def _reset_labels(self) -> None:
        """Reinicia el texto mostrado en los OptionMenu."""
        self.var_archivo.set("Archivo")
        self.var_tp0.set("TP0")
        self.var_tp1.set("TP1")

    def _handler_archivo(self, eleccion: str) -> None:
        self._reset_labels()
        if eleccion == "Abrir Imagen...":
            self.app.cargar()
        elif eleccion == "Guardar Imagen Como...":
            self.app.guardar()
        elif eleccion == "Cerrar Imagen":
            self.app.cerrar_imagen()
        elif eleccion == "Salir":
            self.app.on_closing()

    def _handler_tp0(self, eleccion: str) -> None:
        self._reset_labels()
        if eleccion == "Ver Píxel":
            self.app._set_modo("ver_pixel")
        elif eleccion == "Modificar Píxel":
            self.app._set_modo("mod_pixel")
        elif eleccion == "Seleccionar Región":
            self.app._set_modo("selector")
        elif eleccion == "Copiar Región":
            self.app.copiar()
        elif eleccion == "Promedio Región":
            self.app.promedio()
        elif eleccion == "Restar Imágenes":
            self.app.restar()

    def _handler_tp1(self, eleccion: str) -> None:
        self._reset_labels()
        if eleccion == "Ver Histograma":
            self.app.mostrar_histograma()
        elif eleccion == "Transformación Potencia":
            self.app.transformacion_potencia()
        elif eleccion == "Obtener Negativo":
            self.app.negativo()
        elif eleccion == "Ecualizar Histograma":
            self.app.ecualizacion()
        elif eleccion == "Umbralización":
            self.app.umbralizacion()
        elif eleccion == "Filtro: Media":
            self.app.filtro_media()
        elif eleccion == "Filtro: Mediana":
            self.app.filtro_mediana()
        elif eleccion == "Filtro: Mediana Ponderada":
            self.app.filtro_mediana_ponderada()
        elif eleccion == "Filtro: Gaussiano":
            self.app.filtro_gaussiano()
        elif eleccion == "Filtro: Realce de Bordes":
            self.app.filtro_bordes()
        elif eleccion == "Ruido: Gaussiano":
            self.app.ruido_gaussiano()
        elif eleccion == "Ruido: Exponencial":
            self.app.ruido_exponencial()
        elif eleccion == "Ruido: Sal y Pimienta":
            self.app.ruido_sal_pimienta()

    def cambiar_estado(self, estado: str) -> None:
        """Habilita o deshabilita las opciones principales según el estado."""
        self.menu_tp0.configure(state=estado)
        self.menu_tp1.configure(state=estado)

    def cambiar_estado_roi(self, estado: str) -> None:
        """Habilita opciones dependientes de ROI agregándolas dinámicamente."""
        if estado == tk.NORMAL:
            self.menu_tp0.configure(values=self.base_tp0 + self.roi_tp0)
        else:
            self.menu_tp0.configure(values=self.base_tp0)
