import os
import numpy as np
import matplotlib.image as mpimg

# --- VALIDACIONES Y UTILIDADES ---
dimensiones_validas_imagen = [2, 3]

def es_imagen_valida(matriz):
    """Valida si la matriz no es None y tiene un formato soportado (2D o 3D)."""
    if matriz is None:
        return False
    return matriz.ndim in dimensiones_validas_imagen

def _obtener_extension(ruta):
    """Obtiene la extensión del archivo en formato .EXT (mayúsculas)."""
    return os.path.splitext(ruta)[1].upper()

# --- CARGA Y GUARDADO ---

def _cargar_raw_8bit(ruta, ancho, alto):
    """Procesa archivos RAW. Detecta Gris o RGB por peso de archivo."""
    datos = np.fromfile(ruta, dtype=np.uint8)
    tamanio_esperado = ancho * alto

    # Validación de tamaño físico vs resolución solicitada
    if len(datos) < tamanio_esperado:
        raise ValueError(f"El archivo es demasiado pequeño para la resolución indicada ({ancho}x{alto}).")

    if len(datos) >= tamanio_esperado * 3:
        # Caso RGB
        return datos[:tamanio_esperado * 3].reshape((alto, ancho, 3))
    else:
        # Caso Gris
        return datos[:tamanio_esperado].reshape((alto, ancho))

def _cargar_formato_con_cabecera(ruta):
    """Carga formatos estándar (JPG, PNG, etc.) y normaliza a uint8 (0-255)."""
    matriz = mpimg.imread(ruta)
    # Si la imagen viene en punto flotante, la escalamos
    if matriz.dtype == np.float32 or matriz.dtype == np.float64:
        matriz = (matriz * 255).astype(np.uint8)
    return matriz

def cargar_imagen(ruta, ancho=None, alto=None):
    """Punto de entrada único para cargar cualquier imagen soportada."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    ext = _obtener_extension(ruta)
    if ext == '.RAW':
        return _cargar_raw_8bit(ruta, ancho, alto)
    return _cargar_formato_con_cabecera(ruta)

def guardar_imagen(matriz, ruta):
    """
    Guarda la matriz en disco detectando el formato por la extensión.
    Para RAW guarda el binario directo; para otros usa matplotlib.
    """
    if not es_imagen_valida(matriz):
        raise ValueError("Matriz inválida para guardado.")

    ext = _obtener_extension(ruta)

    if ext == '.RAW':
        # Clipping de seguridad antes de convertir a uint8 
        m_save = np.clip(matriz, 0, 255).astype(np.uint8)
        m_save.tofile(ruta)
    else:
        # matplotlib maneja el guardado de formatos estándar
        if matriz.ndim == 2:
            mpimg.imsave(ruta, matriz, cmap='gray')
        else:
            mpimg.imsave(ruta, matriz)

# --- MANIPULACIÓN DE PÍXELES Y REGIONES ---

def obtener_pixel(matriz, x, y):
    """Retorna intensidad (int) o color (array [R,G,B])."""
    if not es_imagen_valida(matriz):
        raise ValueError("Imagen no soportada.")
    alto, ancho = matriz.shape[:2]
    if not (0 <= x < ancho and 0 <= y < alto):
        raise IndexError(f"Coordenadas fuera de rango: {x},{y}")
    return matriz[y, x]

def modificar_pixel(matriz, x, y, nuevo_valor):
    """Retorna una copia de la matriz con el valor del píxel modificado."""
    if not es_imagen_valida(matriz):
        raise ValueError("Imagen no soportada.")
    alto, ancho = matriz.shape[:2]
    if not (0 <= x < ancho and 0 <= y < alto):
        raise IndexError("Coordenadas fuera de rango.")

    nueva = matriz.copy()
    nueva[y, x] = nuevo_valor
    return nueva

def copiar_region(matriz, x1, y1, x2, y2):
    """Extrae una sub-matriz validando límites."""
    if not es_imagen_valida(matriz):
        raise ValueError("Imagen no soportada.")
    alto, ancho = matriz.shape[:2]

    # Validación
    if not (0 <= x1 <= ancho and 0 <= y1 <= alto):
      raise IndexError("Punto 1 fuera de límites.")
    if not (0 <= x2 <= ancho and 0 <= y2 <= alto):
      raise IndexError("Punto 2 fuera de límites.")

    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)

    return matriz[ymin:ymax, xmin:xmax].copy()

# --- OPERACIONES ARITMÉTICAS ---

def restar_imagenes(img1, img2):
    """Realiza la resta img1 - img2. Soporta Gris-Gris, RGB-RGB y Mixtos."""
    if not (es_imagen_valida(img1) and es_imagen_valida(img2)):
        raise ValueError("Formatos de imagen no soportados.")
    if img1.shape[:2] != img2.shape[:2]:
        raise ValueError("Las resoluciones deben ser idénticas para la resta.")

    # Convertimos a float para el cálculo y evitar overflow/underflow
    m1 = img1.astype(np.float32)
    m2 = img2.astype(np.float32)

    if m1.ndim == m2.ndim:
        resultado = m1 - m2
    elif m1.ndim == 2: # Gris - RGB
        r_r = m1 - m2[:, :, 0]
        r_g = m1 - m2[:, :, 1]
        r_b = m1 - m2[:, :, 2]
        resultado = (r_r + r_g + r_b) / 3
    else: # RGB - Gris
        r_r = m1[:, :, 0] - m2
        r_g = m1[:, :, 1] - m2
        r_b = m1[:, :, 2] - m2
        resultado = (r_r + r_g + r_b) / 3

    return np.clip(resultado, 0, 255).astype(np.uint8)

# --- ESTADÍSTICAS DE REGIÓN ---

def obtener_estadisticas_region(matriz, x1, y1, x2, y2):
    """ Calcula cantidad de píxeles y el promedio de gris o color de la región. """
    region = copiar_region(matriz, x1, y1, x2, y2)

    alto, ancho = region.shape[:2]
    total_pixeles = alto * ancho

    if total_pixeles == 0:
        return 0, 0

    if region.ndim == 2:
        # Promedio simple para niveles de gris
        promedio = np.uint8(np.mean(region))
    else:
        # Promedio por componente para RGB
        promedio_rgb = np.mean(region, axis=(0, 1))
        promedio = promedio_rgb.astype(np.uint8)

    return total_pixeles, promedio