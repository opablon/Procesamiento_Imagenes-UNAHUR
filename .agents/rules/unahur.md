---
trigger: always_on
---

### Reglas de Desarrollo Académico - TP Procesamiento de Imágenes

**1. Estilo de Código y Legibilidad:**
- Priorizar siempre el paradigma **imperativo** y lineal.
- El código debe ser legible para un entorno académico, evitando abstracciones complejas, decoradores avanzados o "one-liners" crípticos.
- Usar nombres de variables y funciones descriptivos en español.

**2. Arquitectura y Escalabilidad:**
- **Modularidad:** El proyecto debe ser modular. Las funciones comunes y reutilizables (ej: `es_imagen_valida()`) deben centralizarse para ser usadas en todo el proyecto a medida que crezca.
- **Responsabilidad Única (SRP):** Separar estrictamente la lógica de cálculo (NumPy en `core/`) de la interfaz de usuario (Tkinter/Matplotlib en `gui/`).
- **Diseño de Interfaz:** Usar **Tkinter estándar** con parámetros por defecto para garantizar una estructura limpia y fácil de escalar al agregar nuevos botones para futuros Trabajos Prácticos.

**3. Documentación y Validación:**
- **Docstrings:** Cada función debe incluir un docstring descriptivo (triple comilla) detallando propósito, parámetros y retorno.
- **Comentarios:** Incluir comentarios breves en pasos críticos de manipulación de matrices de NumPy.
- **Robustez:** Implementar validaciones consistentes antes de procesar imágenes para asegurar que el software sea robusto frente a errores de carga o formatos incompatibles.

**4. Dependencias Técnicas:**
- Uso exclusivo de **NumPy** y **Matplotlib** (FigureCanvasTkAgg) para el procesamiento y visualización.
- Prohibido el uso de Pillow (PIL), OpenCV u otras librerías externas de procesamiento de imágenes.