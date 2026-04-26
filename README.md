# Visualizador y Procesador de Imágenes - UNAHUR

Este repositorio contiene el desarrollo progresivo de una aplicación de escritorio interactiva para la materia **Procesamiento de Imágenes y Visión por Computadora** de la Tecnicatura Universitaria en Inteligencia Artificial de la Universidad Nacional de Hurlingham (UNaHur).

El proyecto está diseñado con una arquitectura modular, separando estrictamente la lógica de negocio (funciones matemáticas) de la interfaz gráfica, y evoluciona integrando nuevos algoritmos en cada entrega académica.

## 🛠️ Stack Tecnológico y Arquitectura
El proyecto se desarrolla bajo un enfoque académico, implementando la lógica de procesamiento de matrices desde cero para comprender los fundamentos matemáticos. **No se utilizan librerías de alto nivel para procesamiento (como OpenCV o PIL/Pillow)**.

* **Cálculo y Procesamiento de Matrices:** NumPy
* **Interfaz Gráfica (GUI):** Tkinter nativo
* **Renderizado y Visor:** Matplotlib (FigureCanvasTkAgg y RectangleSelector)
* **Lenguaje:** Python 3

---

## 🚀 Instalación y Configuración

Sigue estos pasos para clonar el repositorio y configurar tu entorno local en Linux (Ubuntu) o Windows.

### 1. Clonar el repositorio
Abre una terminal (o PowerShell en Windows) y ejecuta:
```bash
git clone https://github.com/opablon/Procesamiento_Imagenes-UNAHUR.git
cd Procesamiento_Imagenes-UNAHUR
```

### 2. Crear y activar el Entorno Virtual
Es recomendable usar un entorno virtual para mantener las dependencias aisladas del sistema.

**En Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar dependencias
Con el entorno activo, instala las librerías necesarias:
```bash
pip install -r requirements.txt
```

> **Notas sobre la interfaz gráfica (GUI):**
> - **En Windows:** Tkinter suele estar incluido con la instalación de Python, pero si al ejecutar python main.py recibes un error de ModuleNotFoundError: No module named '_tkinter', significa que Python fue instalado sin soporte para interfaces gráficas. Para solucionarlo, se debe ejecutar el instalador de Python nuevamente, seleccionar Modify y asegurarse de que la opción tcl/tk and IDLE esté marcada.
> - **En Linux:** Si recibes un error de "tkinter not found", debes instalar el soporte de Tk para Python usando el gestor de paquetes de tu distribución. Ej. en Ubuntu/Debian:
> ```bash
>   sudo apt update && sudo apt install python3-tk
> ```

### 4. Ejecutar la aplicación
Inicia el visualizador corriendo el punto de entrada principal:
```bash
python main.py
```

---

## ⚙️ Índice de Progreso y Funcionalidades

### [x] TP0: Operaciones Básicas e Interfaz
* **Gestión de archivos:** Carga de formatos estándar y archivos binarios .RAW mediante ingreso manual de dimensiones.
* **Inspección de datos:** Visualización de valores a nivel píxel (Gris/RGB) y modificación manual de valores mediante diálogos interactivos.
* **ROI (Región de Interés):** Herramienta de selección interactiva, extracción de recortes y cálculo de estadísticas regionales (cantidad de píxeles y promedio de intensidad).
* **Aritmética:** Resta de imágenes (Gris, RGB y Mixtas) con implementación de Linear Scaling para la correcta visualización de diferencias negativas.

### [x] TP1: Operadores Puntuales y Filtros Espaciales
* **Operadores Puntuales:** Transformación de potencia (Gamma), Negativo de imagen y Umbralización binaria.
* **Análisis Estadístico:** Cálculo matemático de histogramas (frecuencias absolutas) y Ecualización global de histograma mediante función de distribución acumulada (FDA).
* **Generación de Ruidos:** Implementación de ruido Gaussiano (aditivo), Exponencial (multiplicativo) y Sal y Pimienta, controlados por parámetros de densidad y probabilidad.
* **Filtros Espaciales (Convolución Manual):** Implementación de ventana deslizante para filtros de la Media, Mediana, Mediana Ponderada, Gaussiano y Realce de Bordes. La convolución se realiza de forma manual para cumplir con los objetivos pedagógicos de la asignatura.
* **Actualización de Interfaz:** La GUI fue escalada para soportar arquitectura multiventana simultánea, permitiendo la comparación directa entre la imagen original, la imagen con ruido y la imagen filtrada, junto con sus respectivos histogramas dinámicos.

