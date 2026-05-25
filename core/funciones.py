import os
from typing import Any, Optional, Tuple

import matplotlib.image as mpimg
import numpy as np

# --- VALIDACIONES Y UTILIDADES ---
dimensiones_validas_imagen = [2, 3]


def _es_imagen_valida(matriz: Optional[np.ndarray]) -> bool:
    """Valida si la matriz no es None y tiene un formato soportado (2D o 3D)."""
    if matriz is None:
        return False
    return matriz.ndim in dimensiones_validas_imagen


def _obtener_extension(ruta: str) -> str:
    """Obtiene la extensión del archivo en formato .EXT (mayúsculas)."""
    return os.path.splitext(ruta)[1].upper()


def _escalar_a_8bit(matriz: np.ndarray) -> np.ndarray:
    """
    Transformación lineal para remapear cualquier rango al intervalo [0, 255]
    y evitar pérdida de información.
    """
    min_val = np.min(matriz)
    max_val = np.max(matriz)

    # Caso imagen uniforme para evitar división por cero
    if max_val - min_val == 0:
        return np.zeros(matriz.shape, dtype=np.uint8)

    # s = (r - min) * (255 / (max - min))
    matriz_escalada = (matriz - min_val) * (255.0 / (max_val - min_val))

    return matriz_escalada.astype(np.uint8)


# --- INICIO TP 0 ---
# --- CARGA Y GUARDADO ---


def _cargar_raw_8bit(ruta: str, ancho: int, alto: int) -> np.ndarray:
    """Procesa archivos RAW. Detecta Gris o RGB por peso de archivo."""
    datos = np.fromfile(ruta, dtype=np.uint8)
    tamanio_esperado = ancho * alto

    # Validación de tamaño físico vs resolución solicitada
    if len(datos) < tamanio_esperado:
        raise ValueError(
            f"El archivo no contiene suficientes datos para la resolución indicada ({ancho}x{alto})."
            " Verifique las dimensiones o si el archivo está corrupto."
        )

    if len(datos) >= tamanio_esperado * 3:
        # Caso RGB
        return datos[: tamanio_esperado * 3].reshape((alto, ancho, 3))
    else:
        # Caso Gris
        return datos[:tamanio_esperado].reshape((alto, ancho))


def _cargar_formato_con_cabecera(ruta: str) -> np.ndarray:
    """Carga formatos estándar (JPG, PNG, etc.) y normaliza a uint8 (0-255)."""
    matriz = mpimg.imread(ruta)
    # Si la imagen viene en punto flotante, la escalamos
    if matriz.dtype == np.float32 or matriz.dtype == np.float64:
        matriz = (matriz * 255).astype(np.uint8)
    return matriz


def cargar_imagen(ruta: str, ancho: Optional[int] = None, alto: Optional[int] = None) -> np.ndarray:
    """Punto de entrada único para cargar cualquier imagen soportada."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    ext = _obtener_extension(ruta)
    if ext == ".RAW":
        if ancho is None or alto is None:
            raise ValueError("Ancho y alto requeridos para RAW")
        return _cargar_raw_8bit(ruta, ancho, alto)
    return _cargar_formato_con_cabecera(ruta)


def guardar_imagen(matriz: np.ndarray, ruta: str) -> None:
    """
    Guarda la matriz en disco detectando el formato por la extensión.
    Para RAW guarda el binario directo; para otros usa matplotlib.
    """
    if not _es_imagen_valida(matriz):
        raise ValueError("Matriz inválida para guardado.")

    ext = _obtener_extension(ruta)

    if ext == ".RAW":
        # Clipping de seguridad antes de convertir a uint8
        m_save = np.clip(matriz, 0, 255).astype(np.uint8)
        m_save.tofile(ruta)
    else:
        # matplotlib maneja el guardado de formatos estándar
        if matriz.ndim == 2:
            mpimg.imsave(ruta, matriz, cmap="gray")
        else:
            mpimg.imsave(ruta, matriz)


# --- MANIPULACIÓN DE PÍXELES Y REGIONES ---


def obtener_pixel(matriz: np.ndarray, x: int, y: int) -> Any:
    """Retorna intensidad (int) o color (array [R,G,B])."""
    if not _es_imagen_valida(matriz):
        raise ValueError("Imagen no soportada.")
    alto, ancho = matriz.shape[:2]
    if not (0 <= x < ancho and 0 <= y < alto):
        raise IndexError(f"Coordenadas fuera de rango: {x},{y}")
    return matriz[y, x]


def modificar_pixel(matriz: np.ndarray, x: int, y: int, nuevo_valor: Any) -> np.ndarray:
    """Retorna una copia de la matriz con el valor del píxel modificado."""
    if not _es_imagen_valida(matriz):
        raise ValueError("Imagen no soportada.")
    alto, ancho = matriz.shape[:2]
    if not (0 <= x < ancho and 0 <= y < alto):
        raise IndexError("Coordenadas fuera de rango.")

    nueva = matriz.copy()
    nueva[y, x] = nuevo_valor
    return nueva


def copiar_region(matriz: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    """Extrae una sub-matriz validando límites."""
    if not _es_imagen_valida(matriz):
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


def restar_imagenes(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Realiza la resta img1 - img2. Soporta Gris-Gris, RGB-RGB y Mixtos."""
    if not (_es_imagen_valida(img1) and _es_imagen_valida(img2)):
        raise ValueError("Formatos de imagen no soportados.")
    if img1.shape[:2] != img2.shape[:2]:
        raise ValueError("Las resoluciones deben ser idénticas para la resta.")

    # Convertimos a float para el cálculo y evitar overflow/underflow
    m1 = img1.astype(np.float32)
    m2 = img2.astype(np.float32)

    if m1.ndim == m2.ndim:
        resultado = m1 - m2
    elif m1.ndim == 2:  # Gris - RGB
        r_r = m1 - m2[:, :, 0]
        r_g = m1 - m2[:, :, 1]
        r_b = m1 - m2[:, :, 2]
        resultado = (r_r + r_g + r_b) / 3
    else:  # RGB - Gris
        r_r = m1[:, :, 0] - m2
        r_g = m1[:, :, 1] - m2
        r_b = m1[:, :, 2] - m2
        resultado = (r_r + r_g + r_b) / 3

    min_val = np.min(resultado)
    max_val = np.max(resultado)

    # EVITAR DIVISIÓN POR CERO
    if max_val - min_val == 0:
        return np.zeros(resultado.shape, dtype=np.uint8)

    # ESCALADO
    resultado = (resultado - min_val) * (255.0 / (max_val - min_val))

    return resultado.astype(np.uint8)


# --- ESTADÍSTICAS DE REGIÓN ---


def obtener_estadisticas_region(matriz: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, Any]:
    """
    Calcula estadísticas descriptivas de una Región de Interés (ROI).
    Retorna la cantidad total de píxeles y el valor promedio (intensidad o color)
    de la sub-matriz delimitada por los puntos (x1, y1) y (x2, y2).
    """
    # Se utiliza la función auxiliar para extraer la sub-matriz validando límites
    region = copiar_region(matriz, x1, y1, x2, y2)

    alto, ancho = region.shape[:2]
    total_pixeles = alto * ancho

    if total_pixeles == 0:
        return 0, 0

    if region.ndim == 2:
        # Promedio simple para niveles de gris
        suma_acumulada = 0.0

        for y in range(alto):
            for x in range(ancho):
                suma_acumulada += float(region[y, x])

        # El promedio es la suma de intensidades sobre el total de píxeles
        promedio = np.uint8(suma_acumulada / total_pixeles)

    else:
        # Promedio por componente para RGB
        promedio_rgb = np.zeros(3, dtype=np.uint8)

        for canal in range(3):
            suma_canal = 0.0
            for y in range(alto):
                for x in range(ancho):
                    suma_canal += float(region[y, x, canal])

            # Cálculo del promedio independiente para cada banda R, G y B
            promedio_rgb[canal] = np.uint8(suma_canal / total_pixeles)

        promedio = promedio_rgb

    return total_pixeles, promedio


# --- INICIO TP 1 ---
# --- AUMENTO DE CONTRASTE (POTENCIA / GAMMA) ---


def aplicar_transformacion_potencia(matriz_original: np.ndarray, gamma: float) -> np.ndarray:
    """
    Realiza el realce de contraste mediante la función de potencia.
    s = c * r^gamma, donde 'r' es la intensidad original y 's' la transformada.
    Gamma < 1: Aclara la imagen (realce de sombras).
    Gamma > 1: Oscurece la imagen (realce de altas luces).
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    if not (0 < gamma < 2):
        raise ValueError("El valor de gamma debe estar en el rango (0, 2).")

    if gamma == 1:
        return matriz_original.copy()  # Evitamos cálculos innecesarios para la identidad

    # 'c' es la constante de normalización para asegurar que el rango dinámico sea [0, 255]
    # c = 255 / (255^gamma) => 255^(1-gamma)
    constante_c = 255 ** (1 - gamma)

    # Conversión a float32 para evitar errores de precisión durante la potencia
    matriz_float = matriz_original.astype(np.float32)
    matriz_transformada = constante_c * (matriz_float**gamma)

    # Retornamos el escalado
    return np.clip(matriz_transformada, 0, 255).astype(np.uint8)


# --- NEGATIVO ---


def obtener_negativo(matriz_original: np.ndarray) -> np.ndarray:
    """
    Obtiene el negativo de la imagen.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    return 255 - matriz_original.astype(np.uint8)


# --- HISTOGRAMA ---


def obtener_histograma_gris(matriz_original: np.ndarray) -> np.ndarray:
    """
    Calcula el histograma normalizado (frecuencias relativas).
    Retorna un arreglo de 256 elementos donde cada componente h_i se define como:
    h_i = n_i / (N * M)
    donde n_i es la cantidad de píxeles con nivel de gris 'i', y (N*M) es el total de píxeles.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Inicialización del arreglo de frecuencias para 256 niveles
    histograma = np.zeros(256, dtype=int)
    alto, ancho = matriz_original.shape[:2]

    # Recorrido manual para el conteo de frecuencias absolutas
    for y in range(alto):
        for x in range(ancho):
            if matriz_original.ndim == 3:
                # Conversión manual a niveles de gris (promedio de bandas R, G y B)
                suma = 0.0
                for canal in range(3):
                    # Uso de float para evitar el overflow del tipo uint8 en la suma
                    suma += float(matriz_original[y, x, canal])
                valor = int(suma / 3)
            else:
                valor = int(matriz_original[y, x])

            # Incremento de n_i: cantidad de ocurrencias del nivel de gris detectado
            histograma[valor] += 1

    total_pixeles = alto * ancho

    # Retorno del histograma normalizado h_i = n_i / total_pixeles
    return histograma / total_pixeles


# --- UMBRALIZACIÓN ---


def obtener_umbralizacion(matriz_original: np.ndarray, umbral: int) -> np.ndarray:
    """
    Aplica una transformación puntual de umbralización binaria a la imagen.
    La imagen de salida es binaria (blanco y negro) basándose en la función a trozos:
    T(r) = 255 si r >= u
    T(r) = 0   si r < u
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Validación de dominio para el umbral
    if not (0 <= umbral <= 255):
        raise ValueError("El umbral debe estar entre 0 y 255.")

    alto, ancho = matriz_original.shape[:2]

    # Preparar matriz de salida (siempre 2D para imagen binaria)
    resultado = np.zeros((alto, ancho), dtype=np.uint8)

    # Recorrido manual
    for y in range(alto):
        for x in range(ancho):
            # Obtener valor de gris (x,y)
            if matriz_original.ndim == 3:
                # Promedio de los 3 canales (R+G+B)/3
                suma_canales = 0.0
                for canal in range(3):
                    # Convertimos explícitamente a float para evitar el overflow del uint8
                    suma_canales += float(matriz_original[y, x, canal])
                valor_gris = suma_canales / 3
            else:
                valor_gris = matriz_original[y, x]

            # Aplicar lógica de umbral
            if valor_gris >= umbral:
                resultado[y, x] = 255
            else:
                resultado[y, x] = 0

    return resultado


# --- ECUALIZACIÓN DEL HISTOGRAMA ---


def ecualizar_histograma(matriz_original: np.ndarray) -> np.ndarray:
    """
    Aplica la ecualización global basada en la frecuencia relativa de los niveles de gris.
    Implementa la fórmula de discretización teórica utilizando s_min para maximizar el rango dinámico:
    s_k = T(r_k) = (L-1) * sum_{j=0}^{k} p_r(r_j)
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    histograma = obtener_histograma_gris(matriz_original)
    alto, ancho = matriz_original.shape[:2]

    # Cálculo de la probabilidad acumulada (FDA / s_k)
    probabilidad_acumulada = np.zeros(256, dtype=float)
    acumulado = 0.0
    for i in range(256):
        acumulado += histograma[i]
        probabilidad_acumulada[i] = acumulado

    # Identificación de s_min (primer valor estrictamente mayor a cero)
    probabilidad_minima = 0.0
    for prob in probabilidad_acumulada:
        if prob > 0:
            probabilidad_minima = prob
            break

    # Evitar división por cero si la imagen es de un único color
    if probabilidad_minima >= 1.0:
        return matriz_original.copy()

    resultado = np.zeros_like(matriz_original)

    # Mapeo de píxeles
    for y in range(alto):
        for x in range(ancho):
            if matriz_original.ndim == 3:
                for canal in range(3):
                    # Nivel de gris actual de entrada (r_k)
                    gris_entrada = matriz_original[y, x, canal]

                    # Aplicación de la fórmula con s_k y s_min
                    valor_transformado = 255 * (
                        (probabilidad_acumulada[gris_entrada] - probabilidad_minima) / (1.0 - probabilidad_minima)
                    )

                    # Parte entera para obtener s_pico (valor discretizado)
                    gris_salida = int(valor_transformado)
                    resultado[y, x, canal] = max(0, min(255, gris_salida))
            else:
                # Nivel de gris actual de entrada (r_k)
                gris_entrada = matriz_original[y, x]

                # Aplicación de la fórmula con s_k y s_min
                valor_transformado = 255 * (
                    (probabilidad_acumulada[gris_entrada] - probabilidad_minima) / (1.0 - probabilidad_minima)
                )

                # Parte entera para obtener s_pico (valor discretizado)
                gris_salida = int(valor_transformado)
                resultado[y, x] = max(0, min(255, gris_salida))

    return resultado


# --- GENERADORES ALEATORIOS ---
# --- GENERADOR GAUSSIANO ---


def generar_gaussiano(sigma: float, forma: Tuple[int, int], media: float = 0) -> np.ndarray:
    """
    Genera ruido con distribución Normal (Gaussiana).
    """
    if sigma < 0:
        raise ValueError(f"El desvío estándar (sigma={sigma}) no puede ser negativo.")

    ruido_gaussiano = np.random.normal(loc=media, scale=sigma, size=forma)
    return ruido_gaussiano


# --- GENERADOR EXPONENCIAL ---


def generar_exponencial(lambd: float, forma: Tuple[int, int]) -> np.ndarray:
    """
    Genera ruido con distribución Exponencial.
    """
    if lambd <= 0:
        raise ValueError("El parámetro lambda debe ser mayor a 0.")

    ruido_exponencial = np.random.exponential(scale=1.0 / lambd, size=forma)
    return ruido_exponencial


# --- RUIDO ADITIVO GAUSSIANO ---


def aplicar_ruido_aditivo_gaussiano(matriz_original: np.ndarray, densidad: float, sigma: float) -> np.ndarray:
    """
    Contamina una fracción de la imagen sumando ruido con distribución Normal N(μ, σ).
    Sigue el modelo aditivo: Ic(i,j) = I(i,j) + η(i,j) para (i,j) ∈ D,
    donde η es el ruido gaussiano y D es el conjunto de píxeles contaminados.
    """
    if sigma < 0:
        raise ValueError(f"El desvío (sigma={sigma}) debe ser mayor o igual a 0.")
    if not (0 <= densidad <= 100):
        raise ValueError("La densidad d debe estar entre 0 y 100.")

    # Conversión a float64 para permitir valores fuera del rango [0, 255] durante la suma
    matriz_float = matriz_original.astype(np.float64)

    # Probabilidad p de que un píxel pertenezca al conjunto D (porcentaje de contaminación)
    probabilidad = densidad / 100.0

    # Generación del conjunto D (máscara booleana) mediante muestreo aleatorio
    mascara = np.random.choice([True, False], size=matriz_original.shape[:2], p=[probabilidad, 1 - probabilidad])

    # Generar ruido gaussiano solo para la forma de la imagen
    # con valores aleatorios con media 0 y desvío estándar sigma
    ruido_generado = generar_gaussiano(sigma, matriz_original.shape[:2])

    # Aplicar la suma solo a los píxeles seleccionados
    if matriz_original.ndim == 3:  # Imagen color
        for canal in range(3):
            matriz_float[:, :, canal][mascara] += ruido_generado[mascara]
    else:  # Imagen gris
        matriz_float[mascara] += ruido_generado[mascara]

    # Clipping para mantener el rango uint8
    return np.clip(matriz_float, 0, 255).astype(np.uint8)


# --- RUIDO MULTIPLICATIVO EXPONENCIAL ---


def aplicar_ruido_multiplicativo_exponencial(
    matriz_original: np.ndarray, porcentaje: float, lambd: float
) -> np.ndarray:
    """
    Contamina una fracción de la imagen mediante ruido exponencial multiplicativo.
    Sigue el modelo: Ic(i,j) = I(i,j) * η(i,j) para (i,j) ∈ D,
    donde η es una variable aleatoria con distribución exponencial de parámetro λ.
    """
    if lambd <= 0:
        raise ValueError("El parámetro lambda debe ser mayor a 0.")
    if not (0 <= porcentaje <= 100):
        raise ValueError("El porcentaje debe estar entre 0 y 100.")

    # Conversión a float64 para evitar errores de precisión y desbordamiento en la multiplicación
    res = matriz_original.astype(np.float64)

    # Definición de la probabilidad p de pertenencia al conjunto de píxeles D
    probabilidad = porcentaje / 100.0

    # Generación de la máscara aleatoria para identificar el conjunto D
    mascara = np.random.choice([True, False], size=matriz_original.shape[:2], p=[probabilidad, 1 - probabilidad])

    # Generación de la componente de ruido η siguiendo una distribución exponencial
    ruido = generar_exponencial(lambd, matriz_original.shape[:2])

    # Aplicación del modelo multiplicativo solo a los píxeles seleccionados
    if matriz_original.ndim == 3:  # Caso imagen color (RGB)
        for i in range(3):
            # Ic = I * η
            res[:, :, i][mascara] *= ruido[mascara]
    else:  # Caso niveles de gris
        res[mascara] *= ruido[mascara]

    # Truncamiento (Clipping) para asegurar que el resultado final pertenezca al rango [0, 255]
    return np.clip(res, 0, 255).astype(np.uint8)


# --- RUIDO SAL Y PIMIENTA ---


def aplicar_ruido_sal_y_pimienta(matriz_original: np.ndarray, densidad: float) -> np.ndarray:
    """
    Sustituye píxeles por 0 (pimienta) o 255 (sal) según una densidad p.
    """
    if not (0 <= densidad <= 100):
        raise ValueError("La densidad debe estar entre 0 y 100.")

    matriz_ruidosa = matriz_original.copy()

    # p es la probabilidad para cada extremo (sal o pimienta)
    # Si la densidad total es 10%, p = 0.05 (5% sal, 5% pimienta)
    probabilidad = (densidad / 100.0) / 2.0

    # Generamos una matriz aleatoria uniforme [0, 1]
    # Usamos shape[:2] para que funcione igual en gris y color
    variables_aleatorias = np.random.rand(*matriz_original.shape[:2])

    # Aplicamos las sustituciones
    matriz_ruidosa[variables_aleatorias <= probabilidad] = 0  # Pimienta
    matriz_ruidosa[variables_aleatorias > (1 - probabilidad)] = 255  # Sal

    return matriz_ruidosa


# --- FILTROS DESLIZANTES ---


def _aplicar_convolucion_manual(matriz: np.ndarray, mascara: np.ndarray) -> np.ndarray:
    """
    Aplica una máscara de pesos de forma manual a una imagen 2D o RGB[cite: 1].
    Devuelve el resultado en float32 para procesar gradientes o suavizados sin saturación[cite: 1].
    """
    tamano = mascara.shape[0]
    offset = tamano // 2
    alto, ancho = matriz.shape[:2]

    matriz_float = matriz.astype(np.float32)
    resultado = np.copy(matriz_float)

    for y in range(offset, alto - offset):
        for x in range(offset, ancho - offset):

            if matriz.ndim == 3:  # Caso RGB
                for c in range(3):
                    acumulado = 0.0
                    for mascara_y in range(-offset, offset + 1):
                        for mascara_x in range(-offset, offset + 1):
                            val_pixel = matriz_float[y + mascara_y, x + mascara_x, c]
                            peso = mascara[mascara_y + offset, mascara_x + offset]
                            acumulado += val_pixel * peso
                    resultado[y, x, c] = acumulado
            else:  # Caso Gris
                acumulado = 0.0
                for mascara_y in range(-offset, offset + 1):
                    for mascara_x in range(-offset, offset + 1):
                        val_pixel = matriz_float[y + mascara_y, x + mascara_x]
                        peso = mascara[mascara_y + offset, mascara_x + offset]
                        acumulado += val_pixel * peso
                resultado[y, x] = acumulado
    return resultado


# --- FILTRO DE LA MEDIA ---


def aplicar_filtro_media(matriz_original: np.ndarray, tamano_mascara: int) -> np.ndarray:
    """
    Filtro de la Media.
    Consiste en pasar una máscara con pesos (núcleo) donde todos los elementos valen 1/N.
    Reemplaza el centro por el promedio de la vecindad.
    """
    if tamano_mascara % 2 == 0:
        raise ValueError("El tamaño de la máscara debe ser impar.")

    # Creamos la máscara donde cada peso es 1 / N^2
    mascara = np.full((tamano_mascara, tamano_mascara), 1.0 / (tamano_mascara**2), dtype=float)

    # Delegamos la computación
    resultado = _aplicar_convolucion_manual(matriz_original, mascara)

    return np.clip(resultado, 0, 255).astype(np.uint8)


# --- FILTRO DE LA MEDIANA ---


def aplicar_filtro_mediana(matriz_original: np.ndarray, tamano_mascara: int) -> np.ndarray:
    """
    Consiste en ordenar los valores de la vecindad y tomar el del medio
    Efectivo para eliminar ruido Sal y Pimienta.
    """
    if tamano_mascara % 2 == 0:
        raise ValueError("El tamaño de la máscara debe ser impar.")

    alto, ancho = matriz_original.shape[:2]
    offset = tamano_mascara // 2
    matriz_filtrada = matriz_original.copy()

    # El índice central en un array ordenado de tamaño N*N
    indice_central = (tamano_mascara * tamano_mascara) // 2

    for y in range(offset, alto - offset):
        for x in range(offset, ancho - offset):
            if matriz_original.ndim == 2:
                # Caso Niveles de Gris: Extraer, aplanar, ordenar y tomar centro
                vecindad = matriz_original[y - offset : y + offset + 1, x - offset : x + offset + 1]
                lista_valores = sorted(vecindad.flatten().tolist())
                matriz_filtrada[y, x] = lista_valores[indice_central]
            else:
                # Caso RGB: Procesar cada canal por separado
                for canal in range(3):
                    vecindad_canal = matriz_original[y - offset : y + offset + 1, x - offset : x + offset + 1, canal]
                    lista_valores = sorted(vecindad_canal.flatten().tolist())
                    matriz_filtrada[y, x, canal] = lista_valores[indice_central]

    return matriz_filtrada


# --- GENERA LA MASCARA PARA EL FILTRO DE LA MEDIANA PONDERADA ---


def _generar_pesos_mediana_ponderada(tamano_mascara: int) -> np.ndarray:
    """
    Genera una matriz de pesos enteros basada en una aproximación discreta
    de la campana de Gauss utilizando coeficientes binomiales.
    """
    n = tamano_mascara - 1
    kernel_1d = np.zeros(tamano_mascara, dtype=int)

    # Generar el vector 1D iterativamente
    valor = 1
    for i in range(tamano_mascara):
        kernel_1d[i] = valor
        # Fórmula iterativa para el siguiente coeficiente binomial
        valor = valor * (n - i) // (i + 1)

    # Generar la matriz 2D manualmente
    pesos = np.zeros((tamano_mascara, tamano_mascara), dtype=int)
    for y in range(tamano_mascara):
        for x in range(tamano_mascara):
            pesos[y, x] = kernel_1d[y] * kernel_1d[x]

    return pesos


# --- FILTRO DE LA MEDIANA PONDERADA ---


def aplicar_filtro_mediana_ponderada(matriz_original: np.ndarray, tamano_mascara: int) -> np.ndarray:
    """
    Aplica el filtro de la mediana ponderada (operador no lineal de orden).
    A diferencia de la mediana simple, cada píxel de la vecindad se repite
    según un peso definido en una máscara, dándole mayor importancia al centro.
    """
    if tamano_mascara % 2 == 0:
        raise ValueError("El tamaño de la máscara debe ser impar.")

    alto, ancho = matriz_original.shape[:2]
    offset = tamano_mascara // 2
    matriz_filtrada = matriz_original.copy()

    # Generación dinámica de la máscara de pesos (Aproximación Gaussiana/Binomial)
    mascara_pesos = _generar_pesos_mediana_ponderada(tamano_mascara)

    # Recorrido de la imagen evitando los bordes
    for y in range(offset, alto - offset):
        for x in range(offset, ancho - offset):
            # Extracción de la vecindad actual centrada en (y, x)
            vecindad = matriz_original[y - offset : y + offset + 1, x - offset : x + offset + 1]

            if matriz_original.ndim == 2:
                # Caso niveles de gris
                valores_ponderados = []
                for i in range(tamano_mascara):
                    for j in range(tamano_mascara):
                        # Expansión manual: se repite el valor del píxel según indica su peso
                        peso = mascara_pesos[i, j]
                        valor_pixel = vecindad[i, j]
                        valores_ponderados.extend([valor_pixel] * peso)

                # Ordenamiento manual y selección del valor central (mediana ponderada)
                valores_ponderados.sort()
                indice_central = len(valores_ponderados) // 2
                matriz_filtrada[y, x] = valores_ponderados[indice_central]

            else:
                # Caso RGB: Procesar cada canal por separado
                for canal in range(3):
                    valores_ponderados = []
                    for i in range(tamano_mascara):
                        for j in range(tamano_mascara):
                            peso = mascara_pesos[i, j]
                            valor_pixel = vecindad[i, j, canal]
                            valores_ponderados.extend([valor_pixel] * peso)

                    # Ordenamiento y selección de mediana por canal
                    valores_ponderados.sort()
                    indice_central = len(valores_ponderados) // 2
                    matriz_filtrada[y, x, canal] = valores_ponderados[indice_central]

    return matriz_filtrada


# --- GENERA LA MASCARA PARA FILTRO GAUSSIANO ---


def _generar_mascara_gaussiana(sigma: float, tamano_mascara: int) -> np.ndarray:
    """
    Genera el núcleo (kernel) de pesos siguiendo la Función Gaussiana
    de dos variables: G(x,y) = (1 / 2πσ²) * exp(-(x² + y²) / σ²)
    donde μ=(0,0) es el centro de la máscara.
    """
    # Definición del entorno o vecindad respecto al pixel central (0,0)
    radio = tamano_mascara // 2
    mascara = np.zeros((tamano_mascara, tamano_mascara), dtype=float)

    # Coeficiente: 1 / (2 * π * σ²)
    coeficiente = 1 / (2 * np.pi * (sigma**2))
    suma_total = 0.0

    # Iteración para el cálculo de distancias y pesos
    for y in range(-radio, radio + 1):
        for x in range(-radio, radio + 1):
            # Distancia cuadrada: (x - μ1)² + (y - μ2)² con μ = (0,0)
            distancia_cuadrada = x**2 + y**2

            # Exponente: -(distancia_cuadrada) / σ²
            exponente = -distancia_cuadrada / (sigma**2)

            # Función completa G(x,y)
            valor = coeficiente * np.exp(exponente)

            mascara[y + radio, x + radio] = valor
            suma_total += valor

    # Normalización manual para que la suma de pesos sea 1
    for y in range(tamano_mascara):
        for x in range(tamano_mascara):
            mascara[y, x] /= suma_total

    return mascara


# --- FILTRO GAUSSIANO ---


def aplicar_filtro_gaussiano(matriz_original: np.ndarray, sigma: float) -> np.ndarray:
    """
    Reemplaza el valor original del pixel con la suma de los valores
    originales multiplicados por los pesos de la máscara.
    """
    if sigma <= 0:
        raise ValueError("El desvío estándar sigma debe ser mayor a 0.")

    # El tamaño de la máscara debe ser acorde al valor de σ
    # Se utiliza k = 2 * σ + 1
    tamano_mascara = int(2 * sigma + 1)

    if tamano_mascara % 2 == 0:
        raise ValueError(f"El desvío (sigma={sigma}) debe generar una máscara de tamaño impar. Ingrese otro valor.")

    # Obtención de la máscara de pesos
    mascara = _generar_mascara_gaussiana(sigma, tamano_mascara)

    # Convolución centralizada
    resultado = _aplicar_convolucion_manual(matriz_original, mascara)

    return np.clip(resultado, 0, 255).astype(np.uint8)


# --- GENERA LA MASCARA REALCE DE BORDES ---


def _generar_mascara_realce_de_bordes(tamano_mascara: int) -> np.ndarray:
    """
    Genera la máscara de realce de tamaño variable
    Posee coeficientes negativos en la periferia y el centro positivo
    de manera que todos los elementos sumen 0.
    """
    mascara = np.zeros((tamano_mascara, tamano_mascara), dtype=float)
    centro = tamano_mascara // 2

    # Se asignan coeficientes negativos (-1) en la periferia
    # y se calcula el valor central para que la suma sea 0.
    valor_periferia = -1.0
    suma_periferia = 0.0

    for y in range(tamano_mascara):
        for x in range(tamano_mascara):
            if y == centro and x == centro:
                continue
            mascara[y, x] = valor_periferia
            suma_periferia += valor_periferia

    # El centro debe compensar la suma de la periferia: Centro = - (Suma Periferia)
    mascara[centro, centro] = -suma_periferia

    return mascara


# --- FILTRO REALCE DE BORDES ---


def aplicar_filtro_realce_de_bordes(matriz_original: np.ndarray, tamano_mascara: int) -> np.ndarray:
    """
    Realce de Bordes con máscara de tamaño variable.
    Destaca detalles intensificando las transiciones de intensidad.
    """
    if tamano_mascara % 2 == 0:
        raise ValueError("El tamaño de la máscara debe ser impar.")

    # Generación de la máscara acorde al tamaño solicitado
    mascara = _generar_mascara_realce_de_bordes(tamano_mascara)

    # Aplicamos la máscara
    resultado = _aplicar_convolucion_manual(matriz_original, mascara)

    # Retorno con escalado para preservar la integridad de las transiciones detectadas
    return _escalar_a_8bit(resultado)


# --- INICIO TP 2 ---
# --- DETECTORES DE BORDES ---
# --- PREWITT ---


def aplicar_operador_prewitt(matriz_original: np.ndarray) -> np.ndarray:
    """
    Detecta bordes mediante el operador de Prewitt estándar de 3x3.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Máscaras de Prewitt
    mascara_x = np.array([[-1.0, 0.0, 1.0],
                   [-1.0, 0.0, 1.0],
                   [-1.0, 0.0, 1.0]], dtype=float)

    mascara_y = np.array([[-1.0, -1.0, -1.0],
                   [ 0.0,  0.0,  0.0],
                   [ 1.0,  1.0,  1.0]], dtype=float)

    # Si es escala de grises (2D)
    if matriz_original.ndim == 2:
        g_x = _aplicar_convolucion_manual(matriz_original.astype(np.float64), mascara_x)
        g_y = _aplicar_convolucion_manual(matriz_original.astype(np.float64), mascara_y)
        magnitud = np.sqrt(g_x**2 + g_y**2)
        return _escalar_a_8bit(magnitud)

    # Si es color (3D): procesar canal por canal
    else:
        alto, ancho, canales = matriz_original.shape
        borde_color = np.zeros((alto, ancho, canales), dtype=np.float64)

        for c in range(canales):
            canal = matriz_original[:, :, c].astype(np.float64)
            g_x = _aplicar_convolucion_manual(canal, mascara_x)
            g_y = _aplicar_convolucion_manual(canal, mascara_y)
            borde_color[:, :, c] = np.sqrt(g_x**2 + g_y**2)

        return _escalar_a_8bit(borde_color)


# --- SOBEL ---


def aplicar_operador_sobel(matriz_original: np.ndarray) -> np.ndarray:
    """
    Detecta bordes mediante el operador de Sobel estándar de 3x3.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Máscaras de Sobel
    mascara_x = np.array([[-1.0, 0.0, 1.0],
                   [-2.0, 0.0, 2.0],
                   [-1.0, 0.0, 1.0]], dtype=float)

    mascara_y = np.array([[-1.0, -2.0, -1.0],
                   [ 0.0,  0.0,  0.0],
                   [ 1.0,  2.0,  1.0]], dtype=float)

    # Si es escala de grises (2D)
    if matriz_original.ndim == 2:
        g_x = _aplicar_convolucion_manual(matriz_original.astype(np.float64), mascara_x)
        g_y = _aplicar_convolucion_manual(matriz_original.astype(np.float64), mascara_y)
        magnitud = np.sqrt(g_x**2 + g_y**2)
        return _escalar_a_8bit(magnitud)

    # Si es color (3D): procesar canal por canal
    else:
        alto, ancho, canales = matriz_original.shape
        borde_color = np.zeros((alto, ancho, canales), dtype=np.float64)

        for c in range(canales):
            canal = matriz_original[:, :, c].astype(np.float64)
            g_x = _aplicar_convolucion_manual(canal, mascara_x)
            g_y = _aplicar_convolucion_manual(canal, mascara_y)
            borde_color[:, :, c] = np.sqrt(g_x**2 + g_y**2)

        return _escalar_a_8bit(borde_color)


# --- LAPLACIANO ---


def _obtener_mascara_laplaciana(matriz_original: np.ndarray) -> np.ndarray:
    """
    Aplica el operador de Laplace mediante una máscara de 3x3 de 4-vecinos.
    Retorna la matriz con valores flotantes (con signo) para evaluar cruces por cero.
    """
    # Máscara de Laplace: 4*I(x,y) - I(vecinos)
    laplaciana_3x3 = np.array([[ 0.0, -1.0,  0.0],
                               [-1.0,  4.0, -1.0],
                               [ 0.0, -1.0,  0.0]], dtype=float)

    return _aplicar_convolucion_manual(matriz_original, laplaciana_3x3)


# --- DETECTAR CRUCES POR CERO ---


def _detectar_cruces_por_cero(matriz_flotante: np.ndarray, umbral: float) -> np.ndarray:
    """
    Detecta cruces por cero horizontales y verticales.
    Marca un borde (255) si el cambio de signo supera el umbral dado.
    """
    alto, ancho = matriz_flotante.shape[:2]
    resultado = np.zeros((alto, ancho), dtype=np.uint8)
    canales = 3 if matriz_flotante.ndim == 3 else 1

    for c in range(canales):
        matriz_laplaciana = matriz_flotante[:, :, c] if canales == 3 else matriz_flotante

        for y in range(alto - 1):
            for x in range(ancho - 1):
                pixel_actual = matriz_laplaciana[y, x]

                # --- EVALUACIÓN HORIZONTAL ---
                pixel_derecho = matriz_laplaciana[y, x + 1]

                # Caso 1: Cambio de signo directo (+,-) o (-,+)
                if (pixel_actual * pixel_derecho) < 0:

                    # Se calcula la pendiente (|a+b|) y se compara con el umbral
                    if abs(pixel_actual - pixel_derecho) >= umbral:
                        resultado[y, x] = 255

                # Caso 2: Cero intermedio (+,0,-) o (-,0,+)
                elif pixel_derecho == 0 and x + 2 < ancho:
                    pixel_derecho_2 = matriz_laplaciana[y, x + 2] # Evaluamos el pixel que sigue al cero
                    if (pixel_actual * pixel_derecho_2) < 0:
                        if abs(pixel_actual - pixel_derecho_2) >= umbral:
                            resultado[y, x] = 255

                # --- EVALUACIÓN VERTICAL ---
                pixel_abajo = matriz_laplaciana[y + 1, x]

                # Caso 1: Cambio de signo directo
                if (pixel_actual * pixel_abajo) < 0:
                    if abs(pixel_actual - pixel_abajo) >= umbral:
                        resultado[y, x] = 255

                # Caso 2: Cero intermedio
                elif pixel_abajo == 0 and y + 2 < alto:
                    pixel_abajo_2 = matriz_laplaciana[y + 2, x]
                    if (pixel_actual * pixel_abajo_2) < 0:
                        if abs(pixel_actual - pixel_abajo_2) >= umbral:
                            resultado[y, x] = 255

    return resultado


# --- MÉTODO DEL LAPLACIANO ---

def aplicar_mascara_laplaciana(matriz_original: np.ndarray) -> np.ndarray:
    """
    Implementa el Método del Laplaciano clásico (sin filtro de umbral).
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Aplicar máscara de Laplace para obtener la segunda derivada
    crudo = _obtener_mascara_laplaciana(matriz_original)

    # Detectar cualquier cruce por cero (umbral = 0)
    return _detectar_cruces_por_cero(crudo, umbral=0.0)


# --- LAPLACIANO CON PENDIENTE ---


def aplicar_laplaciano_con_pendiente(matriz_original: np.ndarray, umbral: float) -> np.ndarray:
    """
    Implementa el Método del Laplaciano evaluando la magnitud de la pendiente.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Aplicar máscara de Laplace
    crudo = _obtener_mascara_laplaciana(matriz_original)

    # Filtrar bordes reales: solo cruces cuya pendiente supere 'umbral'
    return _detectar_cruces_por_cero(crudo, umbral=umbral)


# --- MASCARA LOG ---


def _generar_mascara_log(sigma: float, tamano_mascara: int) -> np.ndarray:
    """
    Genera la máscara del Laplaciano del Gaussiano (LoG) centrada en (0,0).
    """
    radio = tamano_mascara // 2
    mascara = np.zeros((tamano_mascara, tamano_mascara), dtype=float)

    # Optimizaciones de la constante
    sigma_al_cuadrado = sigma ** 2
    sigma_al_cubo = sigma ** 3
    coeficiente = 1.0 / (2.0 * np.pi * sigma_al_cubo)

    # Variable para acumular la suma de todos los coeficientes calculados.
    # Necesaria para medir el error introducido al truncar la función continua.
    suma_total = 0.0

    for y in range(-radio, radio + 1):
        for x in range(-radio, radio + 1):
            dist_cuadrada = float(x**2 + y**2)

            # Parte exponencial de la función de Gauss
            exponente = -dist_cuadrada / (2.0 * sigma_al_cuadrado)

            # Término derivado del Laplaciano
            termino_log = (dist_cuadrada / sigma_al_cuadrado) - 2.0

            # Valor puntual de la máscara
            valor = coeficiente * np.exp(exponente) * termino_log
            mascara[y + radio, x + radio] = valor

            # Acumulamos el valor calculado
            suma_total += valor

    # En el dominio continuo, la integral de esta derivada es exactamente 0.
    # En esta matriz finita, los valores descartados fuera del radio dejan un residuo.
    # Restar este residuo (suma_total) al píxel central garantiza que la sumatoria
    # de la matriz sea 0 absoluto, evitando que detecte bordes falsos en áreas de color uniforme.
    mascara[radio, radio] -= suma_total

    return mascara


# --- LAPLACIANO GAUSSIANO (MARR-HILDRETH) ---

def aplicar_marr_hildreth(matriz_original: np.ndarray, sigma: float, umbral: float) -> np.ndarray:
    """
    Implementa el Detector LoG (Marr-Hildreth) para mitigar el ruido.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Validaciones de parámetros
    if sigma <= 0:
        raise ValueError(f"El valor de sigma ({sigma}) debe ser mayor a 0 para definir la campana de Gauss.")

    if umbral < 0:
        raise ValueError(f"El umbral de pendiente ({umbral}) no puede ser negativo.")

    # El tamaño de la máscara depende del desvío (4*sigma + 1)
    tamano_mascara = int(4 * sigma + 1)

    # La máscara debe ser impar para tener un centro (x=0, y=0)
    if tamano_mascara % 2 == 0:
        raise ValueError(f"El desvío (sigma={sigma}) debe generar una máscara de tamaño impar.")

    # Generación de máscara basada en sigma
    mascara_log = _generar_mascara_log(sigma, tamano_mascara)

    # La convolución de LoG devuelve floats con signo
    imagen_log_cruda = _aplicar_convolucion_manual(matriz_original, mascara_log)

    # Detección final
    return _detectar_cruces_por_cero(imagen_log_cruda, umbral)


# --- DIFUSIÓN ISOTRÓPICA ---


def aplicar_difusion_isotropica(
    matriz_original: np.ndarray,
    iteraciones: int,
    constante_lambda: float = 0.25
) -> np.ndarray:
    """
    Resuelve la ecuación del calor de conducción isotrópica mediante diferencias finitas.

    Esta implementación utiliza la misma estructura
    iterativa que la difusión anisotrópica (Perona-Malik), pero asume un medio
    isotrópico donde la conducción es idéntica en todas las direcciones (coeficientes c = 1).
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # El parámetro de integración lambda (constante_lambda) debe ser <= 0.25
    # para garantizar la estabilidad numérica en una grilla 2D de 4 vecinos.
    if not (0 < constante_lambda <= 0.25):
        raise ValueError("Por estabilidad matemática, constante_lambda debe estar en (0, 0.25].")

    img = matriz_original.astype(np.float32)
    alto, ancho = img.shape[:2]

    for _ in range(iteraciones):
        nueva_img = np.copy(img)
        canales = 3 if img.ndim == 3 else 1

        for c in range(canales):
            capa = img[:, :, c] if canales == 3 else img
            nueva_capa = np.copy(capa)

            # Recorrido de píxeles internos (omite bordes físicos)
            for y in range(1, alto - 1):
                for x in range(1, ancho - 1):
                    # Diferencias espaciales hacia los 4 vecinos directos (N, S, E, O)
                    dn = capa[y + 1, x] - capa[y, x]
                    ds = capa[y - 1, x] - capa[y, x]
                    de = capa[y, x - 1] - capa[y, x]
                    do = capa[y, x + 1] - capa[y, x]

                    # En un medio isotrópico, los coeficientes de conducción son 1.
                    # Por lo tanto, el flujo total es simplemente la suma de las diferencias.
                    variacion_total = dn + ds + de + do

                    # Actualización de la intensidad: I(t+1) = I(t) + lambda * Variacion
                    nueva_capa[y, x] += constante_lambda * variacion_total

            if canales == 3:
                nueva_img[:, :, c] = nueva_capa
            else:
                nueva_img = nueva_capa
        img = nueva_img

    return np.clip(img, 0, 255).astype(np.uint8)


# --- DIFUSIÓN ANISOTRÓPICA ---


def aplicar_difusion_anisotropica(
    matriz_original: np.ndarray,
    iteraciones: int,
    sigma: float,
    constante_lambda: float = 0.25,
    metodo: str = 'leclerc'
) -> np.ndarray:
    """
    Aplica la ecuación de difusión anisotrópica de Perona-Malik.

    Suaviza regiones de intensidad uniforme (reduciendo ruido) mientras detiene
    la difusión en los bordes gracias al cálculo de coeficientes de conducción variables g(D).

    El parámetro sigma actúa como un umbral de contraste: diferencias mayores a sigma
    detienen la difusión (borde), menores a sigma se suavizan (ruido).
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Restricción matemática de la constante de iteración (lambda)
    if not (0 < constante_lambda <= 0.25):
        raise ValueError("Por estabilidad matemática, constante_lambda debe estar en (0, 0.25].")

    img = matriz_original.astype(np.float32)
    alto, ancho = img.shape[:2]

    for _ in range(iteraciones):
        nueva_img = np.copy(img)
        canales = 3 if img.ndim == 3 else 1

        for c in range(canales):
            capa = img[:, :, c] if canales == 3 else img
            nueva_capa = np.copy(capa)

            for y in range(1, alto - 1):
                for x in range(1, ancho - 1):
                    # Cálculo de gradientes locales (Diferencias Finitas D)
                    dif_norte = capa[y + 1, x] - capa[y, x]
                    dif_sur = capa[y - 1, x] - capa[y, x]
                    dif_este = capa[y, x - 1] - capa[y, x]
                    dif_oeste = capa[y, x + 1] - capa[y, x]

                    # Cálculo de coeficientes de conducción (c)
                    if metodo.lower() == 'leclerc':
                        # Función Exponencial: Privilegia bordes de alto contraste
                        coef_norte = np.exp(-(dif_norte / sigma)**2)
                        coef_sur = np.exp(-(dif_sur / sigma)**2)
                        coef_este = np.exp(-(dif_este / sigma)**2)
                        coef_oeste = np.exp(-(dif_oeste / sigma)**2)
                    else:  # Lorentz
                        # Función Racional (Lorentz): Privilegia regiones amplias
                        coef_norte = 1.0 / (1.0 + (dif_norte / sigma)**2)
                        coef_sur = 1.0 / (1.0 + (dif_sur / sigma)**2)
                        coef_este = 1.0 / (1.0 + (dif_este / sigma)**2)
                        coef_oeste = 1.0 / (1.0 + (dif_oeste / sigma)**2)

                    # Sumatoria de flujos direccionales limitados por sus coeficientes
                    variacion_total = (
                        (dif_norte * coef_norte)
                        + (dif_sur * coef_sur)
                        + (dif_este * coef_este)
                        + (dif_oeste * coef_oeste)
                    )

                    # Actualización del píxel en la iteración t+1
                    nueva_capa[y, x] += constante_lambda * variacion_total

            if canales == 3:
                nueva_img[:, :, c] = nueva_capa
            else:
                nueva_img = nueva_capa
        img = nueva_img

    return np.clip(img, 0, 255).astype(np.uint8)


def aplicar_filtro_bilateral(
    matriz_original: np.ndarray,
    sigma_s: float,
    sigma_r: float
) -> np.ndarray:
    """
    Aplica el filtro bilateral para suavizado con preservación de bordes.

    El tamaño de la máscara se calcula en función de sigma_s
    Se utiliza k = 2 * σ_s + 1
    sigma_s: constante de suavizado en términos espaciales.
    sigma_r: constante de suavizado en términos de intensidad de color.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # El tamaño de la máscara debe ser acorde al valor de σ_s
    # Se utiliza k = 2 * σ_s + 1
    tamano_mascara = int(2 * sigma_s + 1)

    if tamano_mascara % 2 == 0:
        raise ValueError(
            f"El desvío del suavizado espacial (sigma_s={sigma_s}) debe "
            "generar una máscara de tamaño impar. Ingrese otro valor."
        )

    offset = tamano_mascara // 2
    alto, ancho = matriz_original.shape[:2]

    # Conversión a float32 para evitar overflow en potencias y restas de uint8
    matriz_float = matriz_original.astype(np.float32)
    resultado = np.zeros_like(matriz_float)

    # Pre-cálculo del kernel espacial (no depende de la intensidad)
    kernel_espacial = np.zeros((tamano_mascara, tamano_mascara), dtype=np.float32)
    for my in range(-offset, offset + 1):
        for mx in range(-offset, offset + 1):
            distancia_sq = float(mx**2 + my**2)
            kernel_espacial[my + offset, mx + offset] = np.exp(-distancia_sq / (2 * sigma_s**2))

    canales = 3 if matriz_original.ndim == 3 else 1

    # Recorrido pixel a pixel de la imagen
    for y in range(offset, alto - offset):
        for x in range(offset, ancho - offset):

            if canales == 3:
                # --- CASO COLOR (VECTORIAL) ---
                valor_central = matriz_float[y, x]  # Vector [R, G, B] del pixel central
                acumulado = np.zeros(3, dtype=np.float32)
                w_x = 0.0

                # Recorrido de la ventana local
                for my in range(-offset, offset + 1):
                    for mx in range(-offset, offset + 1):
                        valor_vecino = matriz_float[y + my, x + mx]  # Vector [R, G, B] vecino

                        # Norma euclídea al cuadrado en el espacio de color RGB
                        distancia_color_sq = (
                            (valor_central[0] - valor_vecino[0])**2 +
                            (valor_central[1] - valor_vecino[1])**2 +
                            (valor_central[2] - valor_vecino[2])**2
                        )

                        # Similitud en rango/cromática
                        g_r = np.exp(-distancia_color_sq / (2 * sigma_r**2))

                        # Peso conjunto (espacial * rango)
                        peso = kernel_espacial[my + offset, mx + offset] * g_r

                        # Acumulación de color y peso de normalización
                        acumulado += valor_vecino * peso
                        w_x += peso

                # Aplicar normalización
                resultado[y, x] = acumulado / w_x if w_x > 0 else valor_central

            else:
                # --- CASO GRIS (ESCALAR) ---
                valor_central = matriz_float[y, x]  # Escalar
                acumulado = 0.0
                w_x = 0.0

                # Recorrido de la ventana local
                for my in range(-offset, offset + 1):
                    for mx in range(-offset, offset + 1):
                        valor_vecino = matriz_float[y + my, x + mx]

                        # Diferencia de intensidad escalar al cuadrado
                        g_r = np.exp(-((valor_central - valor_vecino)**2) / (2 * sigma_r**2))

                        # Peso conjunto
                        peso = kernel_espacial[my + offset, mx + offset] * g_r

                        acumulado += valor_vecino * peso
                        w_x += peso

                resultado[y, x] = acumulado / w_x if w_x > 0 else valor_central

    return np.clip(resultado, 0, 255).astype(np.uint8)


# --- UMBRALIZACIÓN ÓPTIMA ITERATIVA ---


def _obtener_umbral_iterativo(matriz_original: np.ndarray, delta_t: float = 0.5) -> float:
    """
    Calcula el umbral óptimo de forma iterativa basándose en la media de
    intensidades del objeto y el fondo.
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Si es RGB, trabajamos con la intensidad promedio (escala de grises)
    if matriz_original.ndim == 3:
        img = np.mean(matriz_original.astype(float), axis=2)
    else:
        img = matriz_original.astype(float)

    alto, ancho = img.shape

    # Umbral inicial (Media global de la imagen)
    t_actual = np.mean(img)
    convergencia = False

    while not convergencia:
        suma_g1 = 0.0
        cont_g1 = 0
        suma_g2 = 0.0
        cont_g2 = 0

        # Clasificación y cálculo manual de sumas para medias
        for y in range(alto):
            for x in range(ancho):
                valor = img[y, x]
                if valor > t_actual:  # Grupo G1
                    suma_g1 += valor
                    cont_g1 += 1
                else:  # Grupo G2
                    suma_g2 += valor
                    cont_g2 += 1

        # Calcular medias m1 y m2
        m1 = suma_g1 / cont_g1 if cont_g1 > 0 else 0
        m2 = suma_g2 / cont_g2 if cont_g2 > 0 else 0

        # Nuevo umbral
        t_nuevo = 0.5 * (m1 + m2)

        # Verificar delta_t
        if abs(t_nuevo - t_actual) < delta_t:
            convergencia = True

        t_actual = t_nuevo

    return t_actual


def aplicar_umbralizacion_automatica(matriz_original: np.ndarray, delta_t: float = 0.5) -> np.ndarray:
    """
    Punto de entrada que estima el umbral y aplica la binarización.
    """
    umbral_optimo = _obtener_umbral_iterativo(matriz_original, delta_t)
    return obtener_umbralizacion(matriz_original, int(umbral_optimo))


# --- UMBRALIZACIÓN DE OTSU ---


def _obtener_umbral_otsu(matriz_original: np.ndarray) -> int:
    """
    Calcula el umbral óptimo utilizando el método de Otsu, maximizando
    la varianza entre clases (objetivo y fondo).
    """
    if not _es_imagen_valida(matriz_original):
        raise ValueError("Imagen no soportada.")

    # Computar histograma normalizado pi
    p = obtener_histograma_gris(matriz_original)
    L = 256

    # Computar sumas acumuladas P1(t)
    P1 = np.zeros(L, dtype=float)
    acumulado_p = 0.0
    for t in range(L):
        acumulado_p += p[t]
        P1[t] = acumulado_p

    # Computar promedios ponderados acumulados m(t)
    m = np.zeros(L, dtype=float)
    acumulado_m = 0.0
    for t in range(L):
        acumulado_m += t * p[t]
        m[t] = acumulado_m

    # Promedio ponderado global mG (es el último valor de m)
    mG = m[L - 1]

    # Computar varianza entre clases sigma_B^2(t)
    sigma_B_sq = np.zeros(L, dtype=float)

    for t in range(L):
        denominador = P1[t] * (1.0 - P1[t])

        # Evitar división por cero si una clase está vacía
        if denominador > 0:
            numerador = (mG * P1[t] - m[t]) ** 2
            sigma_B_sq[t] = numerador / denominador
        else:
            sigma_B_sq[t] = 0

    # Maximizar la varianza para hallar t*
    umbral_optimo = 0
    varianza_maxima = -1.0

    for t in range(L):
        if sigma_B_sq[t] > varianza_maxima:
            varianza_maxima = sigma_B_sq[t]
            umbral_optimo = t

    return umbral_optimo


def aplicar_umbralizacion_otsu(matriz_original: np.ndarray) -> np.ndarray:
    """
    Segmenta la imagen utilizando el umbral calculado por el método de Otsu.
    """
    t_estrella = _obtener_umbral_otsu(matriz_original)
    return obtener_umbralizacion(matriz_original, t_estrella)


# --- SEGMENTACIÓN DE IMÁGENES RGB MEDIANTE UMBRALIZACIÓN POR BANDAS ---


def segmentar_color_por_bandas(matriz_original: np.ndarray) -> np.ndarray:
    """
    Segmenta una imagen RGB en 8 regiones de color aplicando el umbral
    óptimo de Otsu de forma independiente a cada banda (R, G, B).
    """
    if not _es_imagen_valida(matriz_original) or matriz_original.ndim != 3:
        raise ValueError("Se requiere una imagen en color (RGB) para este método.")

    alto, ancho = matriz_original.shape[:2]
    resultado = np.zeros((alto, ancho, 3), dtype=np.uint8)

    # Procesamiento independiente por canal
    for canal in range(3):
        banda = matriz_original[:, :, canal]

        # Hallar umbral óptimo para la banda actual mediante Otsu
        t_opt = _obtener_umbral_otsu(banda)

        # Binarización manual de la banda
        for y in range(alto):
            for x in range(ancho):
                if banda[y, x] >= t_opt:
                    resultado[y, x, canal] = 255
                else:
                    resultado[y, x, canal] = 0

    return resultado
