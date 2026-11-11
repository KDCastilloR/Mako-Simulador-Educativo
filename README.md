# MAKO – Simulador Educativo de Cirugía Robótica

## Descripción general

Proyecto de Ingeniería Biomédica enfocado en el **diseño, desarrollo e integración de un simulador educativo de cirugía robótica basado en el sistema MAKO**, orientado al estudio de los sistemas biomecatrónicos y su aplicación en procedimientos quirúrgicos ortopédicos.
<img width="3200" height="1898" alt="image" src="https://github.com/user-attachments/assets/700fc612-7ff3-4355-a8f5-78a8b0e9c67c" />


El proyecto combina diferentes áreas de la ingeniería, incluyendo robótica, biomecánica, modelado tridimensional, programación, automatización, sistemas de control, procesamiento de imágenes médicas e inteligencia artificial.

Mediante la integración de herramientas tecnológicas, se desarrolló un entorno virtual que permite representar el funcionamiento de un brazo robótico quirúrgico, simular sus movimientos, controlar sus articulaciones y visualizar su interacción con un modelo anatómico.

Además, se implementaron sistemas complementarios de control remoto, adquisición de imágenes, almacenamiento médico y generación automatizada de información, permitiendo desarrollar una plataforma educativa multidisciplinaria.

## Componentes principales del proyecto

### 1. Diseño y modelado tridimensional
Desarrollo y organización de los componentes mecánicos del robot MAKO, incluyendo su estructura, articulaciones y herramienta quirúrgica. Se utilizaron herramientas de modelado 3D para preparar los elementos que conforman el sistema robótico.

### 2. Simulación robótica y biomecatrónica
Implementación del robot en CoppeliaSim, configurando sus articulaciones, grados de libertad, jerarquías mecánicas y movimientos. Se desarrollaron secuencias automatizadas para representar la interacción de la herramienta quirúrgica con el modelo anatómico.

### 3. Entorno quirúrgico virtual
Construcción de un escenario tridimensional que representa un quirófano, incorporando equipo médico, personal clínico, paciente y estructuras anatómicas. Este entorno permite contextualizar el funcionamiento del robot durante un procedimiento quirúrgico simulado.

### 4. Sistemas de control y automatización
Desarrollo de interfaces gráficas para gestionar los movimientos del robot y ejecutar diferentes funciones del simulador. Se integraron controles desde la computadora y dispositivos móviles, utilizando programación en Python y Lua para la comunicación y automatización de procesos.

### 5. Sistemas de visualización
Implementación de cámaras virtuales ubicadas en diferentes puntos del entorno quirúrgico, permitiendo observar el procedimiento desde múltiples perspectivas. Se incorporaron funciones de captura y almacenamiento de imágenes generadas durante la simulación.

### 6. Procesamiento de imágenes médicas
Desarrollo de herramientas para convertir imágenes capturadas en formato PNG a archivos DICOM, facilitando su integración con sistemas de gestión de imágenes médicas.

### 7. Integración con sistemas PACS
Implementación de Orthanc como servidor PACS para recibir, organizar y almacenar las imágenes DICOM generadas por el simulador, representando un flujo de trabajo relacionado con los sistemas de información e imágenes utilizados en instituciones de salud.

### 8. Inteligencia artificial
Integración experimental de modelos de inteligencia artificial basados en YOLO para analizar imágenes obtenidas durante la simulación, identificar elementos visuales y generar resultados automatizados.

### 9. Gestión de expedientes e informes
Desarrollo de módulos para generar expedientes médicos ficticios, organizar información de pacientes simulados y producir informes PDF con imágenes, resultados de procesamiento y análisis experimental.

### 10. Integración y validación del sistema
Unificación de los diferentes módulos tecnológicos para comprobar el funcionamiento general del simulador. Se realizaron pruebas de movimiento, control remoto, visualización, captura de imágenes, conversión DICOM, comunicación PACS y generación automatizada de documentación.

## Tecnologías utilizadas

- **Simulación y modelado:** CoppeliaSim y Blender.
- **Programación:** Python y Lua.
- **Control y comunicación:** interfaces gráficas, Flask y tecnologías web.
- **Procesamiento de imágenes:** PNG, DICOM y herramientas de Python.
- **Almacenamiento médico:** Orthanc PACS.
- **Inteligencia artificial:** YOLO y procesamiento automatizado de imágenes.
- **Documentación:** JSON, ReportLab y generación de archivos PDF.
- **Control de versiones:** GitHub y Git LFS.

## Objetivo del proyecto

Desarrollar una plataforma de simulación educativa que permita comprender y demostrar la integración de sistemas robóticos quirúrgicos con tecnologías de control, visualización, procesamiento de imágenes médicas e inteligencia artificial, mediante un entorno virtual interactivo.

## Resultado final

Se desarrolló un **prototipo funcional de simulación quirúrgica** que integra diferentes tecnologías utilizadas en ingeniería biomédica.

El sistema permite representar el funcionamiento mecánico de un robot quirúrgico, ejecutar movimientos automatizados, controlar sus articulaciones desde diferentes dispositivos, visualizar procedimientos mediante cámaras virtuales, capturar imágenes, convertirlas a formato DICOM, almacenarlas en un servidor PACS y generar documentación médica ficticia e informes experimentales mediante inteligencia artificial.

Este proyecto constituye una herramienta educativa para el estudio de la robótica quirúrgica y la integración de sistemas biomédicos, además de proporcionar una base para futuras investigaciones y mejoras relacionadas con simulación, automatización y tecnologías aplicadas a la salud.

**Nota:** El simulador fue desarrollado con fines académicos, educativos y de investigación. No está destinado a realizar procedimientos quirúrgicos reales ni a proporcionar diagnósticos clínicos.
