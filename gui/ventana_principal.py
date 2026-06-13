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


def pedir_float_sug(
    titulo: str, mensaje: str, valor_sugerido: float, minvalue: Optional[float] = None, maxvalue: Optional[float] = None
) -> Optional[float]:
    """Muestra un diálogo de entrada pre-relleno con el valor sugerido."""
    dialog = ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("350x180")
    dialog.attributes("-topmost", True)
    dialog.grab_set()

    resultado: list[Optional[float]] = [None]

    lbl = ctk.CTkLabel(dialog, text=mensaje)
    lbl.pack(pady=10)

    entry = ctk.CTkEntry(dialog)
    entry.insert(0, f"{valor_sugerido:.2f}")
    entry.pack(pady=10)

    # Focusear el widget y seleccionar todo el texto para fácil edición
    entry.focus()
    entry.select_range(0, tk.END)

    def on_ok(event=None):
        val = entry.get()
        if not val:
            resultado[0] = valor_sugerido
            dialog.destroy()
            return
        try:
            f = float(val)
            if minvalue is not None and f < minvalue:
                messagebox.showerror("Error", f"El valor debe ser >= {minvalue}", parent=dialog)
                return
            if maxvalue is not None and f > maxvalue:
                messagebox.showerror("Error", f"El valor debe ser <= {maxvalue}", parent=dialog)
                return
            resultado[0] = f
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número decimal válido.", parent=dialog)

    entry.bind("<Return>", on_ok)

    btn = ctk.CTkButton(dialog, text="Aceptar", command=on_ok)
    btn.pack(pady=10)

    dialog.wait_window()
    return resultado[0]


def pedir_string(titulo: str, mensaje: str) -> Optional[str]:
    dialog = ctk.CTkInputDialog(text=mensaje, title=titulo)
    return dialog.get_input()


def pedir_opcion(titulo: str, mensaje: str, opciones: list[str]) -> Optional[str]:
    dialog = ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("300x150")
    dialog.attributes("-topmost", True)
    dialog.grab_set()

    resultado: list[Optional[str]] = [None]

    lbl = ctk.CTkLabel(dialog, text=mensaje)
    lbl.pack(pady=10)

    var = ctk.StringVar(value=opciones[0])
    combo = ctk.CTkOptionMenu(dialog, values=opciones, variable=var)
    combo.pack(pady=10)

    def on_ok():
        resultado[0] = var.get()
        dialog.destroy()

    btn = ctk.CTkButton(dialog, text="Aceptar", command=on_ok)
    btn.pack(pady=10)

    dialog.wait_window()
    return resultado[0]


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
    instancias: list["AppProcesamiento"] = []

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
        self.root.geometry("900x650")
        self.root.minsize(900, 600)
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

        # Obtener coordenadas validadas de la selección y mostrarlas en la barra de estado
        xm, ym, xM, yM = self._obtener_roi_validada()
        self.lbl_status.configure(text=f"Región: xmin={xm}, ymin={ym}, xmax={xM}, ymax={yM}")

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
            histograma = funciones.obtener_histograma(self.matriz_actual)
            fig = preparar_histograma(histograma, titulo=titulo_full)
            self._mostrar_ventana_grafico(fig, titulo_full)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Comandos TP2 ---

    def bordes_prewitt(self) -> None:
        self._ejecutar_operacion_core(funciones.aplicar_operador_prewitt, "prewitt")

    def bordes_sobel(self) -> None:
        self._ejecutar_operacion_core(funciones.aplicar_operador_sobel, "sobel")

    def laplaciano(self) -> None:
        self._ejecutar_operacion_core(funciones.aplicar_mascara_laplaciana, "laplaciano")

    def laplaciano_pendiente(self) -> None:
        umbral = pedir_float("Umbral", "Umbral para detección de cruce por cero:", minvalue=0)
        if umbral is not None:
            self._ejecutar_operacion_core(funciones.aplicar_laplaciano_con_pendiente, "lap_pend", umbral)

    def marr_hildreth(self) -> None:
        sigma = pedir_float("Sigma", "Desvío estándar de la Gaussiana (sigma > 0):", minvalue=0.1)
        if sigma is None:
            return
        umbral = pedir_float("Umbral", "Umbral de pendiente para cruce por cero:", minvalue=0)
        if umbral is not None:
            self._ejecutar_operacion_core(funciones.aplicar_marr_hildreth, "marr_h", sigma, umbral)

    def difusion_isotropica(self) -> None:
        iters = pedir_entero("Iteraciones", "Cantidad de iteraciones (ej: 10):", minvalue=1)
        if iters is not None:
            self._ejecutar_operacion_core(funciones.aplicar_difusion_isotropica, "dif_iso", iters)

    def difusion_anisotropica(self) -> None:
        iters = pedir_entero("Iteraciones", "Cantidad de iteraciones (ej: 10):", minvalue=1)
        if iters is None:
            return
        sigma = pedir_float("Sigma", "Parámetro sigma (ej: 10.0):", minvalue=0.1)
        if sigma is None:
            return
        metodo = pedir_opcion("Método", "Seleccione función de conducción:", ["Leclerc", "Lorentz"])
        if metodo is not None:
            # lambda_paso fijo en 0.25 para estabilidad
            self._ejecutar_operacion_core(
                funciones.aplicar_difusion_anisotropica, f"dif_aniso_{metodo.lower()}", iters, sigma, 0.25, metodo
            )

    def filtro_bilateral(self) -> None:
        sigma_s = pedir_float("Sigma S", "Sigma Espacial (ej: 2.0):", minvalue=0.1)
        if sigma_s is None:
            return
        sigma_r = pedir_float("Sigma R", "Sigma Rango (ej: 10.0):", minvalue=0.1)
        if sigma_r is not None:
            self._ejecutar_operacion_core(funciones.aplicar_filtro_bilateral, "bilateral", sigma_s, sigma_r)

    def umbral_iterativa(self) -> None:
        dt = pedir_float("Delta T", "Criterio de convergencia delta_t (ej: 0.5):", minvalue=0.01)
        if dt is not None:
            self._ejecutar_operacion_core(funciones.aplicar_umbralizacion_automatica, "umb_iter", dt)

    def umbral_otsu(self) -> None:
        self._ejecutar_operacion_core(funciones.aplicar_umbralizacion_otsu, "otsu")

    def segmentacion_bandas(self) -> None:
        self._ejecutar_operacion_core(funciones.segmentar_color_por_bandas, "seg_color")

    # --- Comandos TP3 ---

    def canny(self) -> None:
        """Maneja la ejecución del detector de bordes Canny con sugerencia de umbrales."""
        if self.matriz_actual is None:
            return
        t1_sug, t2_sug = funciones._sugerir_umbrales_canny(self.matriz_actual)

        t2 = pedir_float_sug("Canny", f"Umbral superior (t2) [Sugerido: {t2_sug:.2f}]:", t2_sug, minvalue=0.0)
        if t2 is None:
            return

        t1 = pedir_float_sug(
            "Canny", f"Umbral inferior (t1) [Sugerido: {t1_sug:.2f}]:", t1_sug, minvalue=0.0, maxvalue=t2
        )
        if t1 is None:
            return

        conectitud = pedir_opcion("Canny", "Conectividad:", ["4-conexo", "8-conexo"])
        if conectitud is not None:
            self._ejecutar_operacion_core(funciones.aplicar_detector_canny, "canny", t1, t2, conectitud)

    def susan(self) -> None:
        """Maneja la ejecución del detector de características SUSAN."""
        t = pedir_float("SUSAN", "Umbral de brillo (t) (por defecto 15.0):", minvalue=0.0)
        if t is None:
            return
        tol = pedir_float("SUSAN", "Tolerancia (por defecto 0.1):", minvalue=0.0)
        if tol is None:
            return
        modo = pedir_opcion("SUSAN", "Visualización:", ["Bordes", "Esquinas", "Ambos"])
        if modo is not None:
            self._ejecutar_operacion_core(_obtener_resultado_susan_combinado, f"susan_{modo.lower()}", modo, t, tol)


# --- Wrappers de ejecución para TP3 ---


def _obtener_resultado_susan_combinado(imagen: np.ndarray, modo: str, t: float, tolerancia: float) -> np.ndarray:
    """Ejecuta el detector SUSAN y devuelve la matriz correspondiente según el modo."""
    mapa_bordes, mapa_esquinas = funciones.aplicar_detector_susan(imagen, t, tolerancia)
    if modo == "Bordes":
        return mapa_bordes
    elif modo == "Esquinas":
        return mapa_esquinas
    elif modo == "Ambos":
        # Combinar: Esquinas en Rojo (canal 0), Bordes en Verde (canal 1)
        alto, ancho = mapa_bordes.shape[:2]
        resultado = np.zeros((alto, ancho, 3), dtype=np.uint8)
        resultado[:, :, 0] = mapa_esquinas
        resultado[:, :, 1] = mapa_bordes
        return resultado
    else:
        raise ValueError(f"Modo de visualización de SUSAN no soportado: {modo}")


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
