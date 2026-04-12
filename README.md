# Visualizador y Procesador de Imágenes - UNAHUR

Este repositorio contiene el desarrollo progresivo de una aplicación de escritorio interactiva para la materia Procesamiento de Imágenes y Visión por Computadora de la Tecnicatura Universitaria en Inteligencia Artificial de la Universidad Nacional de Hurlingham (UNaHur).

El proyecto está diseñado con una arquitectura modular (separando la interfaz gráfica de las funciones matemáticas) y evolucionará a lo largo del cuatrimestre, integrando nuevos algoritmos en cada Trabajo Práctico.

## 🛠️ Stack Tecnológico y Arquitectura
El proyecto se desarrolla bajo un estricto enfoque académico, implementando la lógica de procesamiento de matrices desde cero para comprender los fundamentos matemáticos de las imágenes. **No se utilizan librerías de alto nivel para procesamiento (como OpenCV o PIL/Pillow).**

* **Cálculo y Procesamiento de Matrices:** `NumPy`
* **Interfaz Gráfica (GUI):** `Tkinter` nativo
* **Renderizado y Visor de Imágenes:** `Matplotlib` (`FigureCanvasTkAgg` y `RectangleSelector`)
* **Lenguaje:** Python 3

## 🚀 Índice de Progreso y Funcionalidades

### [x] TP0: Operaciones Básicas e Interfaz
- Carga y visualización de formatos estándar (JPG, PNG, BMP, etc.).
- Carga nativa de archivos binarios `.RAW` (sin cabecera) mediante ingreso manual de dimensiones.
- Guardado de imágenes y recortes, inyectando la resolución en el nombre para formatos RAW.
- Inspección interactiva de valores a nivel píxel (intensidad de gris y canales RGB).
- Modificación manual de valores de píxeles.
- Herramienta de selección de Región de Interés (ROI) interactiva con extracción de recortes.
- Cálculo de estadísticas de región (cantidad de píxeles y promedio de color/intensidad).
- Operaciones aritméticas: Resta de imágenes (Gris-Gris, RGB-RGB y Mixtas) con validación estricta de paridad dimensional.

## ⚙️ Instalación y Uso

1. Clonar el repositorio en tu máquina local:
   ```bash
   git clone https://github.com/opablon/Procesamiento_Imagenes-UNAHUR.git
   ```

2. Crear y activar un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   ```

3. Instalar las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar la aplicación:
   ```bash
   python main.py
   ```