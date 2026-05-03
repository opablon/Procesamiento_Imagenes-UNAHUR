import functools
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Callable, Optional, Tuple

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def pedir_entero(
    titulo: str, mensaje: str, minvalue: Optional[int] = None, maxvalue: Optional[int] = None
) -> Optional[int]:
    dialog = ctk.CTkInputDialog(text=mensaje, title=titulo)
    val = dialog.get_input()
    if not val:
        return None
    try:
        i = int(val)
        if minvalue is not None and i < minvalue:
            return None
        if maxvalue is not None and i > maxvalue:
            return None
        return i
    except ValueError:
        return None


def pedir_float(
    titulo: str, mensaje: str, minvalue: Optional[float] = None, maxvalue: Optional[float] = None
) -> Optional[float]:
    dialog = ctk.CTkInputDialog(text=mensaje, title=titulo)
    val = dialog.get_input()
    if not val:
        return None
    try:
        f = float(val)
        if minvalue is not None and f < minvalue:
            return None
        if maxvalue is not None and f > maxvalue:
            return None
        return f
    except ValueError:
        return None


def pedir_string(titulo: str, mensaje: str) -> Optional[str]:
    dialog = ctk.CTkInputDialog(text=mensaje, title=titulo)
    return dialog.get_input()


import core.funciones as funciones
from gui.menus import GestorMenus
from gui.visualizaciones import VisorMatplotlib, preparar_histograma


def feedback_visual(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        AppProcesamiento.set_estado_global("Procesando...", "watch")
        # Forzamos actualización de la UI para que se vea el cursor antes del procesamiento pesado
        try:
            for inst in AppProcesamiento.instancias:
                if inst.root.winfo_exists():
                    inst.root.update_idletasks()
        except Exception:
            pass

        try:
            return func(self, *args, **kwargs)
        finally:
            AppProcesamiento.set_estado_global("Listo", "")

    return wrapper


class AppProcesamiento:
    instancias = []

    def __init__(
        self, root: tk.Tk | ctk.CTk | ctk.CTkToplevel, matriz: Optional[np.ndarray] = None, titulo: Optional[str] = None
    ) -> None:
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
            lambda e: e.widget.event_generate("<Return>") if isinstance(e.widget, (tk.Entry, tk.Button)) else None,
        )
        self.root.bind("<Escape>", lambda e: self._resetear())

        self.filtros = [
            ("Imágenes", "*.jpg *.JPG *.png *.PNG *.bmp *.BMP *.tif *.TIF *.pgm *.PGM *.raw *.RAW"),
            ("Todos", "*"),
        ]

        # --- Barra de Estado ---
        self.f_status = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.f_status.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = ctk.CTkLabel(self.f_status, text="Listo", anchor=tk.W)
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.color_sample = ctk.CTkFrame(self.f_status, width=20, height=20, fg_color="transparent")
        self.color_sample.pack_propagate(False)
        self.color_sample.pack(side=tk.RIGHT, padx=5, pady=2)

        # --- Menú (Header) ---
        self.f_header = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        self.f_header.pack(side=tk.TOP, fill=tk.X)
        self.gestor_menus = GestorMenus(self.f_header, self)

        # --- Visor (Matplotlib integrado en Tkinter) ---
        f_visor = ctk.CTkFrame(self.root)
        f_visor.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.visor = VisorMatplotlib(f_visor, {"al_seleccionar": self._al_seleccionar, "al_click": self._al_click})

        if self.matriz_actual is not None:
            self.gestor_menus.cambiar_estado(tk.NORMAL)
            self._dibujar()
        else:
            self.cerrar_imagen()

    def _set_modo(self, modo: Optional[str]) -> None:
        """Gestiona el modo activo de la interfaz visual."""
        self.modo_activo = modo
        self.visor.set_modo_selector(modo == "selector")

        if hasattr(self, "color_sample"):
            self.color_sample.configure(fg_color="transparent")

        if modo:
            AppProcesamiento.set_estado_global("Herramienta activa. ESC para salir o finalizar.", "crosshair")
        else:
            AppProcesamiento.set_estado_global("Listo", "")

    def _resetear(self) -> None:
        """Reinicia la selección y el modo activo reseteando el visor (Ej. Botón Escape)."""
        self.area_seleccionada = False
        self.visor.resetear_selector()
        self.gestor_menus.cambiar_estado_roi(tk.DISABLED)
        self._set_modo(None)

    def _al_seleccionar(self, eclick: Any, erelease: Any) -> None:
        """Callback al finalizar selección de ROI. Habilita herramientas dependientes si la ROI es válida."""
        x1, x2, y1, y2 = self.visor.obtener_extents_selector()
        if abs(x2 - x1) < 1 or abs(y2 - y1) < 1:
            return self._resetear()

        self.area_seleccionada = True
        self.gestor_menus.cambiar_estado_roi(tk.NORMAL)

    def _al_click(self, e: Any) -> None:
        """Maneja interacciones puntuales (Ver/Modificar Píxel)."""
        if self.matriz_actual is None or e.inaxes != self.visor.ax:
            return

        x, y = int(e.xdata), int(e.ydata)

        try:
            if self.modo_activo == "ver_pixel":
                val = funciones.obtener_pixel(self.matriz_actual, x, y)
                self.lbl_status.configure(text=f"Coords: ({x},{y}) | Valor: {val}")

                if self.matriz_actual.ndim == 3:
                    hex_color = f"#{int(val[0]):02x}{int(val[1]):02x}{int(val[2]):02x}"
                else:
                    hex_color = f"#{int(val):02x}{int(val):02x}{int(val):02x}"

                self.color_sample.configure(fg_color=hex_color)

            elif self.modo_activo == "mod_pixel":
                msg = "Valor RGB (ej: 255,0,0):" if self.matriz_actual.ndim == 3 else "Valor Gris (0-255):"
                nv = pedir_string("Modificar", f"Px ({x},{y})\n{msg}")
                if nv:
                    val = np.fromstring(nv, sep=",", dtype=np.uint8) if self.matriz_actual.ndim == 3 else int(nv)
                    self.matriz_actual = funciones.modificar_pixel(self.matriz_actual, x, y, val)
                    self._dibujar()

        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _dibujar(self) -> None:
        """Actualiza el canvas con la matriz cargada."""
        if self.matriz_actual is None:
            return
        self.visor.dibujar(self.matriz_actual)
        self._resetear()

    def _pedir_raw(self, ruta: str) -> Any:
        if not ruta.upper().endswith(".RAW"):
            return None
        w = pedir_entero("RAW", "Ancho:", minvalue=1)
        if w is None:
            return False
        h = pedir_entero("RAW", "Alto:", minvalue=1)
        if h is None:
            return False
        return (w, h)

    def _obtener_roi_validada(self) -> Tuple[int, int, int, int]:
        if self.matriz_actual is None:
            return 0, 0, 0, 0
        h, w = self.matriz_actual.shape[:2]
        x1, x2, y1, y2 = self.visor.obtener_extents_selector()
        xm = max(0, min(w, round(x1)))
        xM = max(0, min(w, round(x2)))
        ym = max(0, min(h, round(y1)))
        yM = max(0, min(h, round(y2)))
        return xm, ym, xM, yM

    def _mostrar_ventana_grafico(self, fig: Any, titulo: str) -> None:
        """Abre un Toplevel simple y muestra una figura de Matplotlib."""
        top = ctk.CTkToplevel(self.root)
        top.title(titulo)
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def _limpiar_nombre(self, sufijo: str) -> str:
        """Genera un nombre descriptivo manteniendo la extensión original al final."""
        if not self.nombre_archivo:
            return f"procesada_{sufijo}"
        base, ext = os.path.splitext(self.nombre_archivo)
        return f"{base}_{sufijo}{ext}"

    def on_closing(self) -> None:
        """Protocolo de cierre de seguridad."""
        if self in AppProcesamiento.instancias:
            AppProcesamiento.instancias.remove(self)

        try:
            AppProcesamiento.set_estado_global("Listo", "")
        except Exception:
            pass

        try:
            if isinstance(self.root, ctk.CTk):
                self.root.quit()
            else:
                self.root.destroy()
        except Exception:
            pass

    @classmethod
    def set_estado_global(cls, texto: str, cursor: str) -> None:
        AppProcesamiento.instancias = [i for i in AppProcesamiento.instancias if i.root.winfo_exists()]
        for inst in AppProcesamiento.instancias:
            try:
                if inst.root.winfo_exists():
                    inst.root.configure(cursor=cursor)
                    inst.lbl_status.configure(text=texto)
            except Exception:
                continue

    # --- Operaciones Globales y Archivos ---

    def cargar(self) -> None:
        ruta = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta:
            return
        try:
            dim = self._pedir_raw(ruta)
            if dim is False:
                return
            self.matriz_actual = (
                funciones.cargar_imagen(ruta, *dim) if isinstance(dim, tuple) else funciones.cargar_imagen(ruta)
            )
            self.nombre_archivo = os.path.basename(ruta)
            self.root.title(f"Visualizador - {self.nombre_archivo}")
            self._dibujar()
            self.gestor_menus.cambiar_estado(tk.NORMAL)
            AppProcesamiento.set_estado_global("Listo", "")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
            self.cerrar_imagen()

    def cerrar_imagen(self) -> None:
        self.matriz_actual = None
        self.nombre_archivo = None
        self.root.title("Visualizador")
        self.visor.limpiar()
        self.lbl_status.configure(text="Imagen cerrada")
        self.gestor_menus.cambiar_estado(tk.DISABLED)
        self._resetear()

    def guardar(self) -> None:
        if self.matriz_actual is None:
            return
        try:
            alto, ancho = self.matriz_actual.shape[:2]
            if self.nombre_archivo:
                base, ext = os.path.splitext(self.nombre_archivo)
                sugerencia = f"{base}_{ancho}x{alto}{ext}"
            else:
                sugerencia = f"imagen_procesada_{ancho}x{alto}"

            ruta = filedialog.asksaveasfilename(initialfile=sugerencia, filetypes=self.filtros, parent=self.root)
            if ruta:
                funciones.guardar_imagen(self.matriz_actual, ruta)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Motor Genérico de Operaciones ---

    @feedback_visual
    def _ejecutar_operacion_core(self, funcion_core: Callable, sufijo: str, *args: Any) -> None:
        """Ejecuta una función core de forma asíncrona sobre la matriz actual y abre una nueva instancia."""
        if self.matriz_actual is None:
            return
        try:
            res = funcion_core(self.matriz_actual, *args)
            AppProcesamiento(ctk.CTkToplevel(self.root), res, self._limpiar_nombre(sufijo))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Comandos TP0 ---

    def restar(self) -> None:
        if self.matriz_actual is None:
            return
        ruta2 = filedialog.askopenfilename(filetypes=self.filtros)
        if not ruta2:
            return
        try:
            dim = self._pedir_raw(ruta2)
            if dim is False:
                return
            m2 = funciones.cargar_imagen(ruta2, *dim) if isinstance(dim, tuple) else funciones.cargar_imagen(ruta2)
            self._ejecutar_operacion_core(funciones.restar_imagenes, "resta", m2)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copiar(self) -> None:
        if self.matriz_actual is None:
            return
        try:
            coords = self._obtener_roi_validada()
            self._ejecutar_operacion_core(funciones.copiar_region, "copia", *coords)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def promedio(self) -> None:
        if self.matriz_actual is None:
            return

        self.root.configure(cursor="watch")
        self.lbl_status.configure(text="Calculando promedio...")
        self.root.update_idletasks()

        try:
            coords = self._obtener_roi_validada()
            cant, prom = funciones.obtener_estadisticas_region(self.matriz_actual, *coords)
            self.lbl_status.configure(text=f"Región: {cant}px | Promedio: {prom}")

            if self.matriz_actual.ndim == 3:
                hex_color = f"#{int(prom[0]):02x}{int(prom[1]):02x}{int(prom[2]):02x}"
            else:
                hex_color = f"#{int(prom):02x}{int(prom):02x}{int(prom):02x}"

            self.color_sample.configure(fg_color=hex_color)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.lbl_status.configure(text="Listo")
        finally:
            self.root.configure(cursor="")

    # --- Comandos TP1 ---

    def transformacion_potencia(self) -> None:
        gamma = pedir_float("Gamma", "Ingrese valor de Gamma (0 < gamma < 2):", minvalue=0.01, maxvalue=1.99)
        if gamma is not None:
            self._ejecutar_operacion_core(funciones.aplicar_transformacion_potencia, f"potencia_{gamma}", gamma)

    def negativo(self) -> None:
        self._ejecutar_operacion_core(funciones.obtener_negativo, "negativo")

    def ecualizacion(self) -> None:
        self._ejecutar_operacion_core(funciones.ecualizar_histograma, "ecualizado")

    def umbralizacion(self) -> None:
        umbral = pedir_entero("Umbral", "Valor de umbral (0-255):", minvalue=0, maxvalue=255)
        if umbral is not None:
            self._ejecutar_operacion_core(funciones.obtener_umbralizacion, "umbral", umbral)

    def ruido_gaussiano(self) -> None:
        densidad = pedir_float("Densidad", "Densidad de ruido (0-100):", minvalue=0, maxvalue=100)
        if densidad is None:
            return
        sigma = pedir_float("Sigma", "Desvío estándar (sigma):", minvalue=0)
        if sigma is not None:
            self._ejecutar_operacion_core(funciones.aplicar_ruido_aditivo_gaussiano, "r_gauss", densidad, sigma)

    def ruido_exponencial(self) -> None:
        porcentaje = pedir_float("Porcentaje", "Porcentaje de ruido (0-100):", minvalue=0, maxvalue=100)
        if porcentaje is None:
            return
        lambd = pedir_float("Lambda", "Parámetro lambda (>0):", minvalue=0.0001)
        if lambd is not None:
            self._ejecutar_operacion_core(
                funciones.aplicar_ruido_multiplicativo_exponencial, "r_exp", porcentaje, lambd
            )

    def ruido_sal_pimienta(self) -> None:
        densidad = pedir_float("Densidad", "Densidad de ruido (0-100):", minvalue=0, maxvalue=100)
        if densidad is not None:
            self._ejecutar_operacion_core(funciones.aplicar_ruido_sal_y_pimienta, "r_sp", densidad)

    def filtro_media(self) -> None:
        tamano = pedir_entero("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_media, "f_media", tamano)

    def filtro_mediana(self) -> None:
        tamano = pedir_entero("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_mediana, "f_mediana", tamano)

    def filtro_mediana_ponderada(self) -> None:
        tamano = pedir_entero("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_mediana_ponderada, "f_med_pond", tamano)

    def filtro_gaussiano(self) -> None:
        sigma = pedir_float("Sigma", "Desvío estándar (sigma > 0):", minvalue=0.01)
        if sigma is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_gaussiano, "f_gauss", sigma)

    def filtro_bordes(self) -> None:
        tamano = pedir_entero("Tamaño", "Tamaño de la máscara (impar):", minvalue=3)
        if tamano is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_realce_de_bordes, "f_bordes", tamano)

    @feedback_visual
    def mostrar_histograma(self) -> None:
        if self.matriz_actual is None:
            return
        try:
            nombre = self.nombre_archivo if self.nombre_archivo else "Sin título"
            titulo_full = f"Histograma - {nombre}"
            histograma = funciones.obtener_histograma_gris(self.matriz_actual)
            fig = preparar_histograma(histograma, titulo=titulo_full)
            self._mostrar_ventana_grafico(fig, titulo_full)
        except Exception as e:
            messagebox.showerror("Error", str(e))


def iniciar_aplicacion() -> None:
    """Punto de inicialización único de la aplicación GUI."""
    root = ctk.CTk()
    AppProcesamiento(root)
    try:
        root.mainloop()
    except Exception:
        pass
    finally:
        try:
            plt.close("all")
            root.destroy()
        except Exception:
            pass
