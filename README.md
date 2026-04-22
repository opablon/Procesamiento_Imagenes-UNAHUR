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

**En Linux (Ubuntu):**
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

> Nota para usuarios de Linux: Si al ejecutar la aplicación recibes un error relacionado con tkinter, asegúrate de tener el paquete instalado en tu sistema con:
```bash
sudo apt update && sudo apt install python3-tk
```

### 4. Ejecutar la aplicación
Inicia el visualizador corriendo el punto de entrada principal:
python main.py

---

## ⚙️ Índice de Progreso y Funcionalidades

### [x] TP0: Operaciones Básicas e Interfaz
* **Gestión de archivos:** Carga de formatos estándar y archivos binarios .RAW mediante ingreso manual de dimensiones.
* **Inspección de datos:** Visualización de valores a nivel píxel (Gris/RGB) y modificación manual de valores mediante diálogos interactivos.
* **ROI (Región de Interés):** Herramienta de selección interactiva, extracción de recortes y cálculo de estadísticas regionales (cantidad de píxeles y promedio de intensidad).
* **Aritmética:** Resta de imágenes (Gris, RGB y Mixtas) con implementación de Linear Scaling para la correcta visualización de diferencias negativas.

### [ ] TP1: (Próximamente...)

