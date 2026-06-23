import functools
import multiprocessing
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


def _obtener_raiz_actual() -> tk.Tk | ctk.CTk | None:
    """Devuelve la raíz activa de Tk si ya existe."""
    try:
        raiz = getattr(tk, "_default_root", None)
        if raiz is not None and raiz.winfo_exists():
            return raiz
    except Exception:
        pass
    return None


def _poner_ventana_al_frente(ventana: tk.Toplevel, parent: Any = None) -> None:
    """Eleva una ventana secundaria sin dejarla fijada como always-on-top."""

    def elevar() -> None:
        try:
            if parent is not None:
                ventana.lift(parent)
            else:
                ventana.lift()
        except Exception:
            pass

        try:
            ventana.focus_force()
        except Exception:
            pass

    try:
        ventana.update_idletasks()
    except Exception:
        pass

    try:
        elevar()
    except Exception:
        pass

    try:
        ventana.attributes("-topmost", False)
    except Exception:
        pass

    try:
        ventana.after_idle(elevar)
        ventana.after(75, elevar)
        ventana.after(250, elevar)
    except Exception:
        pass



def pedir_entero(
    titulo: str, mensaje: str, minvalue: Optional[int] = None, maxvalue: Optional[int] = None
) -> Optional[int]:
    parent = _obtener_raiz_actual()
    dialog = ctk.CTkToplevel(parent) if parent is not None else ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("350x180")
    _poner_ventana_al_frente(dialog, parent)
    dialog.wait_visibility()
    dialog.grab_set()

    resultado: list[Optional[int]] = [None]

    lbl = ctk.CTkLabel(dialog, text=mensaje)
    lbl.pack(pady=10)

    entry = ctk.CTkEntry(dialog)
    entry.pack(pady=10)
    entry.focus()
    entry.select_range(0, tk.END)

    def on_ok(event=None):
        val = entry.get().strip()
        if not val:
            dialog.destroy()
            return
        try:
            entero = int(val)
            if minvalue is not None and entero < minvalue:
                messagebox.showerror("Error", f"El valor debe ser >= {minvalue}", parent=dialog)
                return
            if maxvalue is not None and entero > maxvalue:
                messagebox.showerror("Error", f"El valor debe ser <= {maxvalue}", parent=dialog)
                return
            resultado[0] = entero
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número entero válido.", parent=dialog)

    def on_cancel():
        dialog.destroy()

    entry.bind("<Return>", on_ok)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    botones = ctk.CTkFrame(dialog, fg_color="transparent")
    botones.pack(pady=10)

    btn_ok = ctk.CTkButton(botones, text="Aceptar", command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=5)

    btn_cancel = ctk.CTkButton(botones, text="Cancelar", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    dialog.wait_window()
    return resultado[0]


def pedir_float(
    titulo: str, mensaje: str, minvalue: Optional[float] = None, maxvalue: Optional[float] = None
) -> Optional[float]:
    parent = _obtener_raiz_actual()
    dialog = ctk.CTkToplevel(parent) if parent is not None else ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("350x180")
    _poner_ventana_al_frente(dialog, parent)
    dialog.wait_visibility()
    dialog.grab_set()

    resultado: list[Optional[float]] = [None]

    lbl = ctk.CTkLabel(dialog, text=mensaje)
    lbl.pack(pady=10)

    entry = ctk.CTkEntry(dialog)
    entry.pack(pady=10)
    entry.focus()
    entry.select_range(0, tk.END)

    def on_ok(event=None):
        val = entry.get().strip()
        if not val:
            dialog.destroy()
            return
        try:
            numero = float(val)
            if minvalue is not None and numero < minvalue:
                messagebox.showerror("Error", f"El valor debe ser >= {minvalue}", parent=dialog)
                return
            if maxvalue is not None and numero > maxvalue:
                messagebox.showerror("Error", f"El valor debe ser <= {maxvalue}", parent=dialog)
                return
            resultado[0] = numero
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número decimal válido.", parent=dialog)

    def on_cancel():
        dialog.destroy()

    entry.bind("<Return>", on_ok)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    botones = ctk.CTkFrame(dialog, fg_color="transparent")
    botones.pack(pady=10)

    btn_ok = ctk.CTkButton(botones, text="Aceptar", command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=5)

    btn_cancel = ctk.CTkButton(botones, text="Cancelar", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    dialog.wait_window()
    return resultado[0]


def pedir_float_sug(
    titulo: str, mensaje: str, valor_sugerido: float, minvalue: Optional[float] = None, maxvalue: Optional[float] = None
) -> Optional[float]:
    """Muestra un diálogo de entrada pre-relleno con el valor sugerido."""
    parent = _obtener_raiz_actual()
    dialog = ctk.CTkToplevel(parent) if parent is not None else ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("350x180")
    _poner_ventana_al_frente(dialog, parent)
    dialog.wait_visibility()
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
    parent = _obtener_raiz_actual()
    dialog = ctk.CTkToplevel(parent) if parent is not None else ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("350x180")
    _poner_ventana_al_frente(dialog, parent)
    dialog.wait_visibility()
    dialog.grab_set()

    resultado: list[Optional[str]] = [None]

    lbl = ctk.CTkLabel(dialog, text=mensaje)
    lbl.pack(pady=10)

    entry = ctk.CTkEntry(dialog)
    entry.pack(pady=10)
    entry.focus()
    entry.select_range(0, tk.END)

    def on_ok(event=None):
        val = entry.get().strip()
        if not val:
            dialog.destroy()
            return
        resultado[0] = val
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    entry.bind("<Return>", on_ok)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    botones = ctk.CTkFrame(dialog, fg_color="transparent")
    botones.pack(pady=10)

    btn_ok = ctk.CTkButton(botones, text="Aceptar", command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=5)

    btn_cancel = ctk.CTkButton(botones, text="Cancelar", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    dialog.wait_window()
    return resultado[0]


def pedir_opcion(titulo: str, mensaje: str, opciones: list[str]) -> Optional[str]:
    parent = _obtener_raiz_actual()
    dialog = ctk.CTkToplevel(parent) if parent is not None else ctk.CTkToplevel()
    dialog.title(titulo)
    dialog.geometry("300x150")
    _poner_ventana_al_frente(dialog, parent)
    dialog.wait_visibility()
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


import re


def _obtener_secuencia_archivos(ruta_inicial: str) -> list[str]:
    """
    Dada una ruta de archivo inicial, busca en su directorio archivos que sigan
    la secuencia numérica ascendente a partir de dicho archivo.
    Ejemplo: frame_001.png -> [frame_001.png, frame_002.png, frame_003.png, ...]
    """
    directorio = os.path.dirname(ruta_inicial)
    nombre_archivo = os.path.basename(ruta_inicial)

    # Expresión regular para encontrar el último grupo de dígitos antes de la extensión
    match = re.search(r"(.*?)(\d+)(\.[^.]+)$", nombre_archivo)
    if not match:
        return [ruta_inicial]

    prefix, num_str, suffix = match.groups()
    num_inicio = int(num_str)
    num_len = len(num_str)

    archivos_secuencia = []
    idx = num_inicio
    while True:
        siguiente_nombre = f"{prefix}{str(idx).zfill(num_len)}{suffix}"
        siguiente_ruta = os.path.join(directorio, siguiente_nombre)
        if os.path.exists(siguiente_ruta):
            archivos_secuencia.append(siguiente_ruta)
            idx += 1
        else:
            break

    return archivos_secuencia


class DialogoConfiguracionContornos(ctk.CTkToplevel):
    def __init__(self, parent: tk.Tk | ctk.CTk | ctk.CTkToplevel) -> None:
        super().__init__(parent)
        self.title("Configuración - Contornos Activos")
        self.geometry("450x380")
        _poner_ventana_al_frente(self, parent)
        self.wait_visibility()
        self.grab_set()

        self.resultado: Optional[Tuple[str, Tuple[int, int, int], Tuple[int, int, int], int]] = None

        # Título
        lbl_title = ctk.CTkLabel(self, text="Configuración de Contornos Activos", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # Modo (Única vs Secuencia)
        f_modo = ctk.CTkFrame(self)
        f_modo.pack(fill=tk.X, padx=20, pady=5)
        lbl_modo = ctk.CTkLabel(f_modo, text="Modo de procesamiento:")
        lbl_modo.pack(side=tk.LEFT, padx=10, pady=5)
        self.var_modo = ctk.StringVar(value="Imagen única")
        opt_modo = ctk.CTkOptionMenu(f_modo, values=["Imagen única", "Secuencia de imágenes"], variable=self.var_modo)
        opt_modo.pack(side=tk.RIGHT, padx=10, pady=5)

        # Colores (Lin y Lout)
        f_colores = ctk.CTkFrame(self)
        f_colores.pack(fill=tk.X, padx=20, pady=5)

        lbl_lin = ctk.CTkLabel(f_colores, text="Color Lin (RGB):")
        lbl_lin.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.entry_lin_r = ctk.CTkEntry(f_colores, width=50)
        self.entry_lin_r.insert(0, "255")
        self.entry_lin_r.grid(row=0, column=1, padx=2, pady=5)

        self.entry_lin_g = ctk.CTkEntry(f_colores, width=50)
        self.entry_lin_g.insert(0, "0")
        self.entry_lin_g.grid(row=0, column=2, padx=2, pady=5)

        self.entry_lin_b = ctk.CTkEntry(f_colores, width=50)
        self.entry_lin_b.insert(0, "0")
        self.entry_lin_b.grid(row=0, column=3, padx=2, pady=5)

        lbl_lout = ctk.CTkLabel(f_colores, text="Color Lout (RGB):")
        lbl_lout.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.entry_lout_r = ctk.CTkEntry(f_colores, width=50)
        self.entry_lout_r.insert(0, "0")
        self.entry_lout_r.grid(row=1, column=1, padx=2, pady=5)

        self.entry_lout_g = ctk.CTkEntry(f_colores, width=50)
        self.entry_lout_g.insert(0, "0")
        self.entry_lout_g.grid(row=1, column=2, padx=2, pady=5)

        self.entry_lout_b = ctk.CTkEntry(f_colores, width=50)
        self.entry_lout_b.insert(0, "255")
        self.entry_lout_b.grid(row=1, column=3, padx=2, pady=5)

        # Iteraciones máximas
        f_iters = ctk.CTkFrame(self)
        f_iters.pack(fill=tk.X, padx=20, pady=5)
        lbl_iters = ctk.CTkLabel(f_iters, text="Iteraciones máximas por frame:")
        lbl_iters.pack(side=tk.LEFT, padx=10, pady=5)
        self.entry_iters = ctk.CTkEntry(f_iters, width=80)
        self.entry_iters.insert(0, "100")
        self.entry_iters.pack(side=tk.RIGHT, padx=10, pady=5)

        # Leyenda
        lbl_leyenda = ctk.CTkLabel(
            self,
            text="Nota: Para secuencia de imágenes (video), asegúrese de tener archivos\n"
            "con nombres ordenados numéricamente de forma ascendente (ej. frame_001.png,\n"
            "frame_002.png) y tener abierto el primer archivo de la serie.",
            font=("Arial", 10, "italic"),
            justify=tk.LEFT,
            text_color="gray",
        )
        lbl_leyenda.pack(pady=10, padx=20)

        # Botones
        f_btns = ctk.CTkFrame(self, fg_color="transparent")
        f_btns.pack(pady=10)

        btn_ok = ctk.CTkButton(f_btns, text="Aceptar", width=100, command=self._on_ok)
        btn_ok.pack(side=tk.LEFT, padx=10)

        btn_cancel = ctk.CTkButton(f_btns, text="Cancelar", width=100, command=self.destroy)
        btn_cancel.pack(side=tk.LEFT, padx=10)

        self.wait_window()

    def _validar_color(self, r: str, g: str, b: str, nombre: str) -> Optional[Tuple[int, int, int]]:
        try:
            vr = int(r)
            vg = int(g)
            vb = int(b)
            if not (0 <= vr <= 255 and 0 <= vg <= 255 and 0 <= vb <= 255):
                raise ValueError()
            return vr, vg, vb
        except ValueError:
            messagebox.showerror(
                "Error", f"Valores de color {nombre} inválidos. Deben ser enteros entre 0 y 255.", parent=self
            )
            return None

    def _on_ok(self) -> None:
        c_in = self._validar_color(self.entry_lin_r.get(), self.entry_lin_g.get(), self.entry_lin_b.get(), "Lin")
        if c_in is None:
            return
        c_out = self._validar_color(self.entry_lout_r.get(), self.entry_lout_g.get(), self.entry_lout_b.get(), "Lout")
        if c_out is None:
            return

        try:
            iters = int(self.entry_iters.get())
            if iters <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                "Error", "La cantidad de iteraciones debe ser un entero positivo mayor a 0.", parent=self
            )
            return

        modo = "unica" if self.var_modo.get() == "Imagen única" else "secuencia"
        self.resultado = (modo, c_in, c_out, iters)
        self.destroy()


class VentanaSecuenciaContornos(ctk.CTkToplevel):
    def __init__(
        self,
        parent: tk.Tk | ctk.CTk | ctk.CTkToplevel,
        rutas_archivos: list[str],
        roi_inicial: Tuple[int, int, int, int],
        color_in: Tuple[int, int, int],
        color_out: Tuple[int, int, int],
        max_iters: int,
    ) -> None:
        super().__init__(parent)
        self.rutas_archivos = rutas_archivos
        self.roi_inicial = roi_inicial
        self.color_in = list(color_in)
        self.color_out = list(color_out)
        self.max_iters = max_iters

        self.title("Procesamiento de Secuencia - Contornos Activos")
        self.geometry("900x700")
        self.minsize(900, 600)

        # Registrar instancia
        AppProcesamiento.instancias.append(self)
        self.root = self

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Escape>", self._on_escape)

        # --- Barra de Estado ---
        self.f_status = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.f_status.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_status = ctk.CTkLabel(self.f_status, text="Inicializando...", anchor=tk.W)
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # --- Panel de Controles ---
        f_controls = ctk.CTkFrame(self)
        f_controls.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Fila 1: Ejecución
        f_controls_exec = ctk.CTkFrame(f_controls, fg_color="transparent")
        f_controls_exec.pack(fill=tk.X, padx=2, pady=2)

        self.btn_paso = ctk.CTkButton(f_controls_exec, text="Paso Iteración", command=self.paso_iteracion)
        self.btn_paso.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        self.btn_fin = ctk.CTkButton(f_controls_exec, text="Fin Frame", command=self.fin_frame)
        self.btn_fin.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        self.btn_play = ctk.CTkButton(f_controls_exec, text="Reproducir Completo", command=self.reproducir_completo)
        self.btn_play.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        # Fila 2: Navegación
        f_controls_nav = ctk.CTkFrame(f_controls, fg_color="transparent")
        f_controls_nav.pack(fill=tk.X, padx=2, pady=2)

        self.btn_reiniciar = ctk.CTkButton(f_controls_nav, text="Reiniciar Secuencia", command=self.reiniciar_secuencia)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        self.btn_anterior = ctk.CTkButton(f_controls_nav, text="Frame Anterior", command=self.frame_anterior)
        self.btn_anterior.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        self.btn_prox = ctk.CTkButton(f_controls_nav, text="Próximo Frame", command=self.proximo_frame)
        self.btn_prox.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)

        # --- Visor ---
        f_visor = ctk.CTkFrame(self)
        f_visor.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.visor = VisorMatplotlib(
            f_visor, {"al_seleccionar": self._al_seleccionar_nueva_roi, "al_click": lambda *a: None}
        )

        # Estado de segmentación
        self.idx_actual = 0
        self.reproduciendo = False
        self.phi: Optional[np.ndarray] = None

        # Inicializar el primer frame
        self._cargar_frame_actual()

    def _cargar_frame_actual(self, usar_phi_previo: bool = False) -> None:
        try:
            self.matriz_frame_original = funciones.cargar_imagen(self.rutas_archivos[self.idx_actual])
            if self.idx_actual == 0 and not usar_phi_previo:
                self.phi, self.L_in, self.L_out = funciones._inicializar_estado_segmentacion(
                    self.matriz_frame_original, self.roi_inicial
                )
            else:
                assert self.phi is not None
                self.phi, self.L_in, self.L_out = funciones._inicializar_desde_phi(self.phi)

            self.convergido = False
            self.num_iter_frame = 0
            self._actualizar_vista()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar/inicializar el frame: {str(e)}", parent=self)

    def _actualizar_vista(self) -> None:
        img = self.matriz_frame_original
        if img.ndim == 2:
            resultado = np.stack((img,) * 3, axis=-1)
        else:
            resultado = img.copy()

        # Dibujar L_in en el color elegido
        for px, py in self.L_in:
            if 0 <= px < resultado.shape[1] and 0 <= py < resultado.shape[0]:
                resultado[py, px] = self.color_in

        # Dibujar L_out en el color elegido
        for px, py in self.L_out:
            if 0 <= px < resultado.shape[1] and 0 <= py < resultado.shape[0]:
                resultado[py, px] = self.color_out

        self.visor.dibujar(resultado)

        nombre_f = os.path.basename(self.rutas_archivos[self.idx_actual])
        info = (
            f"Frame {self.idx_actual + 1}/{len(self.rutas_archivos)} ({nombre_f}) | "
            f"Iteración: {self.num_iter_frame} | "
            f"Convergido: {'Sí' if self.convergido else 'No'}"
        )
        self.lbl_status.configure(text=info)

    def _al_seleccionar_nueva_roi(self, eclick: Any, erelease: Any) -> None:
        # Obtener coordenadas de selección
        h, w = self.matriz_frame_original.shape[:2]
        x1, x2, y1, y2 = self.visor.obtener_extents_selector()
        xm = max(0, min(w, round(x1)))
        xM = max(0, min(w, round(x2)))
        ym = max(0, min(h, round(y1)))
        yM = max(0, min(h, round(y2)))

        # Validar selección mínima
        if abs(xM - xm) < 2 or abs(yM - ym) < 2:
            return

        # Inicializar segmentación con esta nueva ROI
        self.roi_inicial = (xm, ym, xM, yM)
        self.phi, self.L_in, self.L_out = funciones._inicializar_estado_segmentacion(
            self.matriz_frame_original, self.roi_inicial
        )

        # Desactivar selector y resetear su dibujo en Matplotlib
        self.visor.set_modo_selector(False)
        self.visor.resetear_selector()

        # Actualizar vista
        self._actualizar_vista()

    def paso_iteracion(self) -> None:
        if self.phi is None:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione un rectángulo inicial en la imagen para comenzar.",
                parent=self,
            )
            return

        if self.convergido:
            messagebox.showinfo("Contornos Activos", "El frame actual ya ha convergido o finalizado.", parent=self)
            return

        try:
            self.phi, self.L_in, self.L_out, terminado = funciones._ejecutar_paso_segmentacion(
                self.matriz_frame_original, self.phi, self.L_in, self.L_out
            )
            self.num_iter_frame += 1
            if terminado or self.num_iter_frame >= self.max_iters:
                self.convergido = True
            self._actualizar_vista()
        except Exception as e:
            messagebox.showerror("Error", f"Error en paso de segmentación: {str(e)}", parent=self)

    def fin_frame(self) -> None:
        if self.phi is None:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione un rectángulo inicial en la imagen para comenzar.",
                parent=self,
            )
            return

        if self.convergido:
            messagebox.showinfo("Contornos Activos", "El frame actual ya ha convergido o finalizado.", parent=self)
            return

        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            while not self.convergido and self.num_iter_frame < self.max_iters:
                self.phi, self.L_in, self.L_out, terminado = funciones._ejecutar_paso_segmentacion(
                    self.matriz_frame_original, self.phi, self.L_in, self.L_out
                )
                self.num_iter_frame += 1
                if terminado:
                    break
            self.convergido = True
            self._actualizar_vista()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar fin de frame: {str(e)}", parent=self)
        finally:
            self.configure(cursor="")

    def proximo_frame(self) -> None:
        if self.phi is None:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione un rectángulo inicial en la imagen para comenzar.",
                parent=self,
            )
            return

        if self.idx_actual + 1 >= len(self.rutas_archivos):
            messagebox.showinfo("Contornos Activos", "Fin de la secuencia de imágenes.", parent=self)
            return

        self.idx_actual += 1
        self._cargar_frame_actual(usar_phi_previo=True)

    def frame_anterior(self) -> None:
        if self.phi is None:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione un rectángulo inicial en la imagen para comenzar.",
                parent=self,
            )
            return

        if self.idx_actual <= 0:
            messagebox.showinfo("Contornos Activos", "Ya se encuentra en el primer frame.", parent=self)
            return

        self.idx_actual -= 1
        self._cargar_frame_actual(usar_phi_previo=True)

    def reiniciar_secuencia(self) -> None:
        self.idx_actual = 0
        try:
            self.matriz_frame_original = funciones.cargar_imagen(self.rutas_archivos[0])
            self.phi = None
            self.L_in = set()
            self.L_out = set()
            self.convergido = False
            self.num_iter_frame = 0

            # Dibujar la imagen limpia
            self.visor.dibujar(self.matriz_frame_original)

            # Activar el modo selector para que el usuario pueda dibujar la nueva curva
            self.visor.set_modo_selector(True)

            self.lbl_status.configure(
                text="Secuencia reiniciada. Seleccione un nuevo rectángulo inicial arrastrando sobre la imagen."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al reiniciar secuencia: {str(e)}", parent=self)

    def reproducir_completo(self) -> None:
        if self.phi is None:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione un rectángulo inicial en la imagen para comenzar.",
                parent=self,
            )
            return

        if self.reproduciendo:
            self.reproduciendo = False
            return

        fps = pedir_entero("Reproducir", "Ingrese FPS mínimos (ej. 5):", minvalue=1, maxvalue=60)
        if fps is None:
            return

        delay_ms = int(1000 / fps)
        self.reproduciendo = True

        self.btn_paso.configure(state=tk.DISABLED)
        self.btn_fin.configure(state=tk.DISABLED)
        self.btn_prox.configure(state=tk.DISABLED)
        self.btn_anterior.configure(state=tk.DISABLED)
        self.btn_reiniciar.configure(state=tk.DISABLED)
        self.btn_play.configure(text="Pausar")

        import time

        try:
            while self.reproduciendo and self.winfo_exists():
                t_inicio = time.time()

                # Procesar frame actual hasta convergencia/límite
                while not self.convergido and self.num_iter_frame < self.max_iters:
                    self.phi, self.L_in, self.L_out, terminado = funciones._ejecutar_paso_segmentacion(
                        self.matriz_frame_original, self.phi, self.L_in, self.L_out
                    )
                    self.num_iter_frame += 1
                    if terminado:
                        break
                self.convergido = True
                self._actualizar_vista()
                self.update()

                if self.idx_actual + 1 < len(self.rutas_archivos):
                    t_fin = time.time()
                    tiempo_comp = (t_fin - t_inicio) * 1000
                    delay = max(1, delay_ms - tiempo_comp)

                    time.sleep(delay / 1000.0)

                    self.idx_actual += 1
                    # Cargar siguiente frame
                    self.matriz_frame_original = funciones.cargar_imagen(self.rutas_archivos[self.idx_actual])
                    assert self.phi is not None
                    self.phi, self.L_in, self.L_out = funciones._inicializar_desde_phi(self.phi)
                    self.convergido = False
                    self.num_iter_frame = 0
                else:
                    messagebox.showinfo("Contornos Activos", "Secuencia completada.", parent=self)
                    break
        except Exception as e:
            messagebox.showerror("Error", f"Error en reproducción completa: {str(e)}", parent=self)
        finally:
            self.reproduciendo = False
            if self.winfo_exists():
                self.btn_paso.configure(state=tk.NORMAL)
                self.btn_fin.configure(state=tk.NORMAL)
                self.btn_prox.configure(state=tk.NORMAL)
                self.btn_anterior.configure(state=tk.NORMAL)
                self.btn_reiniciar.configure(state=tk.NORMAL)
                self.btn_play.configure(text="Reproducir Completo")

    def on_closing(self) -> None:
        self.reproduciendo = False
        if self in AppProcesamiento.instancias:
            AppProcesamiento.instancias.remove(self)
        self.destroy()

    def _on_escape(self, event: Optional[Any] = None) -> None:
        if self.reproduciendo:
            self.reproduciendo = False
            self.lbl_status.configure(text="Operación cancelada")
            messagebox.showinfo("Operación", "Operación cancelada", parent=self)


import core.funciones as funciones
from gui.menus import GestorMenus
from gui.visualizaciones import VisorMatplotlib, preparar_histograma


def _funcion_trabajadora_proceso(queue: Any, funcion_core: Callable, imagen: np.ndarray, *args: Any) -> None:
    """Función de nivel de módulo para que sea picklable por multiprocessing."""
    try:
        res = funcion_core(imagen, *args)
        queue.put(("SUCCESS", res))
    except KeyboardInterrupt:
        queue.put(("CANCELLED", None))
    except Exception as e:
        queue.put(("ERROR", str(e)))


def _obtener_histogramas_rgb(imagen: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calcula los histogramas individuales para los canales R, G y B de forma picklable."""
    hist_r = funciones.obtener_histograma(imagen[:, :, 0])
    hist_g = funciones.obtener_histograma(imagen[:, :, 1])
    hist_b = funciones.obtener_histograma(imagen[:, :, 2])
    return hist_r, hist_g, hist_b


def feedback_visual(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.set_estado("Procesando...", "watch")
        try:
            self.root.update_idletasks()
        except Exception:
            pass

        try:
            return func(self, *args, **kwargs)
        finally:
            self.set_estado("Listo", "")

    return wrapper


class AppProcesamiento:
    instancias: list[Any] = []

    def __init__(
        self, root: tk.Tk | ctk.CTk | ctk.CTkToplevel, matriz: Optional[np.ndarray] = None, titulo: Optional[str] = None
    ) -> None:
        AppProcesamiento.instancias.append(self)
        self.root = root
        self.nombre_archivo = titulo
        self.root.title(f"Visualizador - {titulo}" if titulo else "Visualizador")
        self.matriz_actual = matriz
        self.ruta_completa = None
        self.modo_activo = None
        self.area_seleccionada = False
        self._proceso_activo = None
        self._cola_proceso = None
        self._cursores_originales = {}
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("900x650")
        self.root.minsize(900, 600)
        self.root.bind_all(
            "<KP_Enter>",
            lambda e: e.widget.event_generate("<Return>") if isinstance(e.widget, (tk.Entry, tk.Button)) else None,
        )
        self.root.bind("<Escape>", self._on_escape)

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
            self.set_estado("Herramienta activa. ESC para salir o finalizar.", "crosshair")
        else:
            self.set_estado("Listo", "")

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
            messagebox.showerror("Error", str(err), parent=self.root)

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

    def _mostrar_ventana_grafico(self, fig: Any, titulo: str, histograma: Any) -> None:
        """Abre un Toplevel y muestra una figura de Matplotlib con la opción de escala logarítmica."""
        top = ctk.CTkToplevel(self.root)
        top.title(titulo)
        _poner_ventana_al_frente(top, self.root)

        # Frame de controles en la parte inferior
        frame_controles = ctk.CTkFrame(top)
        frame_controles.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Canvas para el gráfico
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax = fig.gca()

        var_log = ctk.BooleanVar(value=False)

        def actualizar_escala() -> None:
            # Escala Y (Logarítmica vs Lineal)
            if var_log.get():
                ax.set_yscale("log")
                if isinstance(histograma, tuple):
                    valores = []
                    for h in histograma:
                        h_validos = h[h > 0]
                        if len(h_validos) > 0:
                            valores.append(np.min(h_validos))
                    min_val = min(valores) if valores else 1e-5
                else:
                    h_validos = histograma[histograma > 0]
                    min_val = np.min(h_validos) if len(h_validos) > 0 else 1e-5
                ax.set_ylim(bottom=min_val * 0.5)
            else:
                ax.set_yscale("linear")
                ax.set_ylim(bottom=0)

            # Auto-escala el límite superior basándose en el máximo valor real (adherencia teórica)
            if isinstance(histograma, tuple):
                max_real = max(np.max(h) for h in histograma)
            else:
                max_real = np.max(histograma)
            ax.set_ylim(top=max_real * 1.05)

            canvas.draw()

        chk_log = ctk.CTkCheckBox(
            frame_controles, text="Escala Logarítmica", variable=var_log, command=actualizar_escala
        )
        chk_log.pack(side=tk.LEFT, padx=10, pady=5)

        canvas.draw()

    def _limpiar_nombre(self, sufijo: str) -> str:
        """Genera un nombre descriptivo manteniendo la extensión original al final."""
        if not self.nombre_archivo:
            return f"procesada_{sufijo}"
        base, ext = os.path.splitext(self.nombre_archivo)
        return f"{base}_{sufijo}{ext}"

    def on_closing(self) -> None:
        """Protocolo de cierre de seguridad."""
        self.reproduciendo = False
        if hasattr(self, "_proceso_activo") and self._proceso_activo and self._proceso_activo.is_alive():
            self._cancelar_operacion_activa()

        if self in AppProcesamiento.instancias:
            AppProcesamiento.instancias.remove(self)

        try:
            self.set_estado("Listo", "")
        except Exception:
            pass

        try:
            if isinstance(self.root, ctk.CTk):
                self.root.quit()
            else:
                self.root.destroy()
        except Exception:
            pass

    def set_estado(self, texto: str, cursor: str) -> None:
        """Establece el estado y el cursor de forma local a esta instancia."""
        try:
            if self.root.winfo_exists():
                self._set_cursor_recursivo(self.root, cursor)
                self.lbl_status.configure(text=texto)
        except Exception:
            pass

    def _set_cursor_recursivo(self, widget: Any, cursor: str) -> None:
        """Propaga el cursor recursivamente a todos los widgets del árbol,
        evitando redibujos de CustomTkinter para prevenir parpadeos.
        """
        # Ignoramos widgets de CustomTkinter excepto las ventanas de nivel superior (CTk, CTkToplevel)
        is_ctk_widget = type(widget).__module__.startswith("customtkinter")
        is_window = isinstance(widget, (ctk.CTk, ctk.CTkToplevel, tk.Tk, tk.Toplevel))

        if not is_ctk_widget or is_window:
            wid_id = str(widget)
            if cursor != "":
                if wid_id not in self._cursores_originales:
                    try:
                        self._cursores_originales[wid_id] = widget.cget("cursor")
                    except Exception:
                        self._cursores_originales[wid_id] = ""
                try:
                    widget.configure(cursor=cursor)
                except Exception:
                    pass
            else:
                orig = self._cursores_originales.get(wid_id, "")
                try:
                    widget.configure(cursor=orig)
                except Exception:
                    pass
                if wid_id in self._cursores_originales:
                    try:
                        del self._cursores_originales[wid_id]
                    except Exception:
                        pass

        try:
            for child in widget.winfo_children():
                self._set_cursor_recursivo(child, cursor)
        except Exception:
            pass

    @classmethod
    def set_estado_global(cls, texto: str, cursor: str) -> None:
        """Mantenido por compatibilidad global."""
        cls.instancias = [i for i in cls.instancias if i.root.winfo_exists()]
        for inst in cls.instancias:
            try:
                inst.set_estado(texto, cursor)
            except Exception:
                continue

    def _on_escape(self, event: Optional[Any] = None) -> None:
        """Maneja el evento de la tecla Escape."""
        if hasattr(self, "_proceso_activo") and self._proceso_activo and self._proceso_activo.is_alive():
            self._cancelar_operacion_activa()
        else:
            self._resetear()

    def _cancelar_operacion_activa(self) -> None:
        """Cancela el proceso de cálculo activo usando terminación nativa del OS."""
        if hasattr(self, "_proceso_activo") and self._proceso_activo and self._proceso_activo.is_alive():
            try:
                self._proceso_activo.terminate()
                self._proceso_activo.join()
            except Exception:
                pass
            self._limpiar_proceso_activo()
            self.set_estado("Listo", "")
            messagebox.showinfo("Operación", "Operación cancelada", parent=self.root)

    def _limpiar_proceso_activo(self) -> None:
        """Limpia las referencias y recursos del proceso activo."""
        if hasattr(self, "_proceso_activo") and self._proceso_activo:
            try:
                if self._proceso_activo.is_alive():
                    self._proceso_activo.terminate()
                self._proceso_activo.close()
            except Exception:
                pass
            self._proceso_activo = None
        self._cola_proceso = None

    def _ejecutar_tarea_proceso(
        self, funcion_core: Callable, on_success: Callable[[Any], None], on_error: Callable[[str], None], *args: Any
    ) -> None:
        """Ejecuta una función core en un proceso separado y monitorea su finalización."""
        if hasattr(self, "_proceso_activo") and self._proceso_activo and self._proceso_activo.is_alive():
            messagebox.showwarning(
                "Procesamiento",
                "Ya hay una operación en curso en esta ventana. Espere o cancélela con ESC.",
                parent=self.root,
            )
            return

        self.set_estado("Procesando...", "watch")

        try:
            self.root.update_idletasks()
        except Exception:
            pass

        self._cola_proceso = multiprocessing.Queue()

        self._proceso_activo = multiprocessing.Process(
            target=_funcion_trabajadora_proceso,
            args=(self._cola_proceso, funcion_core, self.matriz_actual, *args),
            daemon=True,
        )
        self._proceso_activo.start()

        # Comenzar el monitoreo periódico
        self.root.after(100, lambda: self._monitorear_proceso(on_success, on_error))

    def _monitorear_proceso(self, on_success: Callable[[Any], None], on_error: Callable[[str], None]) -> None:
        """Chequea el estado del proceso en ejecución de forma periódica."""
        if not self.root.winfo_exists():
            self._limpiar_proceso_activo()
            return

        # Si ya no hay un proceso o cola activa, ignoramos llamadas tardías/duplicadas
        if self._proceso_activo is None or self._cola_proceso is None:
            return

        if self._proceso_activo.is_alive():
            if not self._cola_proceso.empty():
                self._procesar_resultado_cola(on_success, on_error)
            else:
                self.root.after(100, lambda: self._monitorear_proceso(on_success, on_error))
        else:
            self._procesar_resultado_cola(on_success, on_error)

    def _procesar_resultado_cola(self, on_success: Callable[[Any], None], on_error: Callable[[str], None]) -> None:
        """Recupera los datos de la cola del proceso y ejecuta los callbacks."""
        try:
            if self._cola_proceso and not self._cola_proceso.empty():
                status, res = self._cola_proceso.get_nowait()
                self._limpiar_proceso_activo()
                self.set_estado("Listo", "")

                if status == "SUCCESS":
                    on_success(res)
                elif status == "CANCELLED":
                    messagebox.showinfo("Operación", "Operación cancelada", parent=self.root)
                elif status == "ERROR":
                    on_error(res)
            else:
                self._limpiar_proceso_activo()
                self.set_estado("Listo", "")
                on_error("El proceso de cálculo finalizó inesperadamente.")
        except Exception as e:
            self._limpiar_proceso_activo()
            self.set_estado("Listo", "")
            on_error(f"Error al recuperar el resultado: {str(e)}")

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
            self.ruta_completa = ruta
            self.nombre_archivo = os.path.basename(ruta)
            self.root.title(f"Visualizador - {self.nombre_archivo}")
            self._dibujar()
            self.gestor_menus.cambiar_estado(tk.NORMAL)
            self.set_estado("Listo", "")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}", parent=self.root)
            self.cerrar_imagen()

    def cerrar_imagen(self) -> None:
        self.matriz_actual = None
        self.ruta_completa = None
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
            messagebox.showerror("Error", str(e), parent=self.root)

    # --- Motor Genérico de Operaciones ---

    def _ejecutar_operacion_core(self, funcion_core: Callable, sufijo: str, *args: Any) -> None:
        """Ejecuta una función core de forma asíncrona en un proceso y abre una nueva instancia."""
        if self.matriz_actual is None:
            return

        def on_success(res: Any) -> None:
            try:
                AppProcesamiento(ctk.CTkToplevel(self.root), res, self._limpiar_nombre(sufijo))
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir la ventana: {str(e)}", parent=self.root)

        def on_error(err_msg: str) -> None:
            messagebox.showerror("Error", err_msg, parent=self.root)

        self._ejecutar_tarea_proceso(funcion_core, on_success, on_error, *args)

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
            messagebox.showerror("Error", str(e), parent=self.root)

    def copiar(self) -> None:
        if self.matriz_actual is None:
            return
        try:
            coords = self._obtener_roi_validada()
            self._ejecutar_operacion_core(funciones.copiar_region, "copia", *coords)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def promedio(self) -> None:
        if self.matriz_actual is None:
            return

        self.set_estado("Calculando promedio...", "watch")
        try:
            self.root.update_idletasks()
        except Exception:
            pass

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
            messagebox.showerror("Error", str(e), parent=self.root)
            self.lbl_status.configure(text="Listo")
        finally:
            self.set_estado("Listo", "")

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

    def mostrar_histograma(self) -> None:
        if self.matriz_actual is None:
            return
        nombre_ventana = self.root.title()

        def on_success(histograma: Any) -> None:
            try:
                fig = preparar_histograma(histograma, titulo=nombre_ventana)
                self._mostrar_ventana_grafico(fig, nombre_ventana, histograma)
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar histograma: {str(e)}", parent=self.root)

        def on_error(err_msg: str) -> None:
            messagebox.showerror("Error", err_msg, parent=self.root)

        # Si la imagen es RGB (3 canales o más), calculamos por separado cada canal
        if self.matriz_actual.ndim == 3 and self.matriz_actual.shape[2] >= 3:
            self._ejecutar_tarea_proceso(_obtener_histogramas_rgb, on_success, on_error)
        else:
            self._ejecutar_tarea_proceso(funciones.obtener_histograma, on_success, on_error)

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
        """Maneja la ejecución del detector de bordes Canny con sugerencia de umbrales genéricos."""
        if self.matriz_actual is None:
            return
        t1_sug = 50.0
        t2_sug = 100.0

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
        if self.matriz_actual is None:
            return

        destino = pedir_opcion("SUSAN - Fondo", "Fondo para dibujar resultados:", ["Fondo negro", "Imagen actual"])
        if destino is None:
            return

        img_fondo = self.matriz_actual if destino == "Imagen actual" else None

        t = pedir_float("SUSAN", "Umbral de brillo (t) (por defecto 15.0):", minvalue=0.0)
        if t is None:
            return
        tol = pedir_float("SUSAN", "Tolerancia (por defecto 0.15):", minvalue=0.0)
        if tol is None:
            return
        modo = pedir_opcion("SUSAN", "Visualización:", ["Bordes", "Esquinas", "Ambos"])
        if modo is not None:
            self._ejecutar_operacion_core(
                _obtener_resultado_susan_combinado, f"susan_{modo.lower()}", modo, t, tol, img_fondo
            )

    def hough(self) -> None:
        if self.matriz_actual is None:
            return

        destino = pedir_opcion(
            "Hough - Fondo",
            "Fondo para dibujar rectas:",
            ["Imagen actual (binaria)", "Cargar imagen original de fondo..."],
        )
        if destino is None:
            return

        img_fondo = None
        if destino == "Cargar imagen original de fondo...":
            ruta_fondo = filedialog.askopenfilename(filetypes=self.filtros, parent=self.root)
            if not ruta_fondo:
                return
            dim = self._pedir_raw(ruta_fondo)
            if dim is False:
                return
            try:
                img_fondo = (
                    funciones.cargar_imagen(ruta_fondo, *dim)
                    if isinstance(dim, tuple)
                    else funciones.cargar_imagen(ruta_fondo)
                )
                if img_fondo.shape[:2] != self.matriz_actual.shape[:2]:
                    messagebox.showerror(
                        "Error",
                        "La resolución de la imagen de fondo debe coincidir con la de la imagen binarizada actual.",
                        parent=self.root,
                    )
                    return
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen de fondo: {str(e)}", parent=self.root)
                return

        res_theta = pedir_float("Hough", "Resolución Theta en grados (ej: 1.0):", minvalue=0.1)
        if res_theta is None:
            return

        umbral = pedir_entero("Hough", "Umbral mínimo de votos en acumulador:", minvalue=1)
        if umbral is None:
            return

        self._ejecutar_operacion_core(_obtener_resultado_hough, "hough", res_theta, umbral, img_fondo)

    def contornos_activos(self) -> None:
        if self.matriz_actual is None:
            return
        if not self.area_seleccionada:
            messagebox.showwarning(
                "Contornos Activos",
                "Por favor, seleccione primero una Región de Interés (ROI) "
                "usando la herramienta 'Seleccionar Región' de TP0.",
                parent=self.root,
            )
            return

        dialogo = DialogoConfiguracionContornos(self.root)
        if dialogo.resultado is None:
            return

        modo, color_in, color_out, max_iters = dialogo.resultado
        coords = self._obtener_roi_validada()

        if modo == "unica":
            self._ejecutar_operacion_core(
                _obtener_resultado_contornos_activos, "contornos_activos", coords, color_in, color_out, max_iters
            )
        else:
            if not self.ruta_completa:
                messagebox.showerror(
                    "Error",
                    "Para procesar una secuencia, la imagen actual debe haber sido cargada desde un archivo en disco.",
                    parent=self.root,
                )
                return
            rutas_secuencia = _obtener_secuencia_archivos(self.ruta_completa)
            if not rutas_secuencia:
                messagebox.showerror("Error", "No se encontraron imágenes en la secuencia.", parent=self.root)
                return

            # Abrir la ventana de secuencia
            VentanaSecuenciaContornos(self.root, rutas_secuencia, coords, color_in, color_out, max_iters)


# --- Wrappers de ejecución para TP3 ---


def _obtener_resultado_susan_combinado(
    imagen: np.ndarray, modo: str, t: float, tolerancia: float, imagen_fondo: Optional[np.ndarray] = None
) -> np.ndarray:
    """Ejecuta el detector SUSAN y dibuja los resultados sobre fondo negro o sobre un fondo específico.

    Parámetros:
        imagen: La imagen actual sobre la cual se aplica el detector SUSAN.
        modo: El modo de visualización ("Bordes", "Esquinas" o "Ambos").
        t: Umbral de brillo para el detector SUSAN.
        tolerancia: Tolerancia para la clasificación en el detector SUSAN.
        imagen_fondo: Opcional. Imagen de fondo sobre la cual se dibujarán los resultados.

    Retorna:
        Matriz de la imagen resultante con los bordes y/o esquinas dibujados.
    """
    mapa_bordes, mapa_esquinas = funciones.aplicar_detector_susan(imagen, t, tolerancia)

    # Si no se especificó un fondo, usamos un lienzo negro de 3 canales
    if imagen_fondo is None:
        resultado = np.zeros((imagen.shape[0], imagen.shape[1], 3), dtype=np.uint8)
    else:
        if imagen_fondo.ndim == 2:
            resultado = np.stack((imagen_fondo,) * 3, axis=-1)
        else:
            resultado = imagen_fondo.copy()

    # Inyectar colores directamente donde las máscaras dieron positivo (255)
    if modo in ["Bordes", "Ambos"]:
        resultado[mapa_bordes == 255] = [0, 255, 0]  # Bordes en Verde
    if modo in ["Esquinas", "Ambos"]:
        resultado[mapa_esquinas == 255] = [255, 0, 0]  # Esquinas en Rojo

    return resultado


def _obtener_resultado_hough(
    imagen: np.ndarray, res_theta: float, umbral_hough: int, imagen_fondo: Optional[np.ndarray] = None
) -> np.ndarray:
    """Halla las rectas mediante Hough directamente sobre la imagen binarizada y las dibuja."""
    # Aplicar núcleo de Hough directamente a la imagen actual (ya binarizada)
    mapa_rectas = funciones.aplicar_transformada_hough_rectas(
        imagen, res_theta=res_theta, res_r=1.0, umbral=umbral_hough
    )

    # Si se especificó un fondo, dibujamos sobre él. Si no, sobre la imagen binarizada
    fondo = imagen_fondo if imagen_fondo is not None else imagen

    # Preparar lienzo a color copiando el fondo
    if fondo.ndim == 2:
        resultado = np.stack((fondo,) * 3, axis=-1)
    else:
        resultado = fondo.copy()

    # Inyectar color rojo para las rectas detectadas
    resultado[mapa_rectas == 255] = [255, 0, 0]

    return resultado


def _obtener_resultado_contornos_activos(
    imagen: np.ndarray,
    inicializacion: Tuple[int, int, int, int],
    color_in: Tuple[int, int, int],
    color_out: Tuple[int, int, int],
    maximo_iteraciones: int,
) -> np.ndarray:
    """Ejecuta los contornos activos y dibuja L_in y L_out en los colores personalizados."""
    phi, L_in, L_out = funciones.aplicar_segmentacion_basado_intercambio_pixels(
        imagen, inicializacion, maximo_iteraciones
    )

    if imagen.ndim == 2:
        resultado = np.stack((imagen,) * 3, axis=-1)
    else:
        resultado = imagen.copy()

    # Dibujar L_in
    for px, py in L_in:
        if 0 <= px < resultado.shape[1] and 0 <= py < resultado.shape[0]:
            resultado[py, px] = color_in

    # Dibujar L_out
    for px, py in L_out:
        if 0 <= px < resultado.shape[1] and 0 <= py < resultado.shape[0]:
            resultado[py, px] = color_out

    return resultado


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
