
# ============================================================
# MAKO PACS
# INFORME CON IMAGENES E INTELIGENCIA ARTIFICIAL
# YOLO + ORTHANC + REPORTLAB
# ============================================================

import sys
import re
import html
import traceback
import shutil

from pathlib import Path
from datetime import datetime

import requests
import numpy as np

from PIL import Image as PILImage
from ultralytics import YOLO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# 1. CONFIGURACION
# ============================================================

BASE = Path(r"C:\MAKO_PACS")

CAPTURAS = BASE / "capturas_png"

DATOS = BASE / "datos"

# Carpeta individual del informe IA
SALIDA = DATOS / "informes_IA"

# Carpeta general de resultados
RESULTADOS = DATOS / "RESULTADOS_MAKO"

# Imagenes temporales y procesadas
TEMP = SALIDA / "procesadas"

# Orthanc
ORTHANC = "http://localhost:8042"

# Modelo YOLO entrenado
MODELO_ENTRENADO = (
    BASE / "IA" / "runs" / "detect" /
    "segundo_entrenamiento" / "weights" / "best.pt"
)

# Modelo alternativo
MODELO_ALTERNATIVO = (
    BASE / "IA" / "runs" / "detect" / "runs" /
    "mako" / "primer_entrenamiento" /
    "weights" / "best.pt"
)

# Confianza minima
CONFIANZA = 0.25

# Consultar Orthanc
INCLUIR_ORTHANC = True

TIMEOUT = 20


# ============================================================
# 2. IDENTIFICAR SESION
# ============================================================

print("\n==========================================")
print("       MAKO PACS - INFORME IA")
print("==========================================")

if len(sys.argv) < 2:
    print("ERROR: Falta el identificador de sesion.")
    print("Ejemplo: 20261108_122805")
    sys.exit(1)

SESION = sys.argv[1].strip()

if not re.fullmatch(r"\d{8}_\d{6}", SESION):
    print("ERROR: Identificador de sesion no valido.")
    print("Formato requerido: AAAAMMDD_HHMMSS")
    sys.exit(1)

print("SESION:", SESION)


# ============================================================
# 3. CREAR CARPETAS
# ============================================================

try:
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

except Exception as e:
    print("ERROR CREANDO CARPETAS:", e)
    sys.exit(1)


# ============================================================
# 4. LOCALIZAR MODELO YOLO
# ============================================================

print("\nBUSCANDO MODELO YOLO...")

if MODELO_ENTRENADO.exists():
    RUTA_MODELO = MODELO_ENTRENADO

elif MODELO_ALTERNATIVO.exists():
    RUTA_MODELO = MODELO_ALTERNATIVO

else:
    print("ERROR: No se encontro best.pt.")
    print("Rutas revisadas:")
    print(MODELO_ENTRENADO)
    print(MODELO_ALTERNATIVO)
    sys.exit(1)

print("MODELO ENCONTRADO:", RUTA_MODELO)


# ============================================================
# 5. CARGAR INTELIGENCIA ARTIFICIAL
# ============================================================

try:
    print("\nCARGANDO INTELIGENCIA ARTIFICIAL...")

    modelo = YOLO(str(RUTA_MODELO))

    print("MODELO YOLO CARGADO CORRECTAMENTE")
    print("CLASES:", modelo.names)

except Exception as e:
    print("ERROR AL CARGAR YOLO:", e)
    traceback.print_exc()
    sys.exit(1)


# ============================================================
# 6. LOCALIZAR CAPTURAS DE CAMARAS
# ============================================================

print("\nBUSCANDO CAPTURAS DE CAMARAS...")

CAMARAS = {
    "DOCTOR": CAPTURAS / f"doctor_{SESION}.png",
    "MAKO": CAPTURAS / f"mako_{SESION}.png",
    "LAMPARA": CAPTURAS / f"lampara_{SESION}.png"
}

imagenes = []

for nombre, ruta in CAMARAS.items():

    if ruta.exists():

        try:
            with PILImage.open(ruta) as img:
                img.verify()

            imagenes.append((nombre, ruta))
            print("CAPTURA ENCONTRADA:", ruta.name)

        except Exception as e:
            print("IMAGEN INVALIDA:", nombre, e)

    else:
        print("AVISO: No existe:", ruta.name)


if not imagenes:
    print("\nERROR: No hay capturas para esta sesion.")
    print("Carpeta:", CAPTURAS)
    sys.exit(1)


# ============================================================
# 7. CONSULTAR ORTHANC
# ============================================================

imagenes_orthanc = []

if INCLUIR_ORTHANC:

    print("\nCONSULTANDO SERVIDOR ORTHANC...")

    try:
        respuesta = requests.get(
            f"{ORTHANC}/studies",
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()

        estudios = respuesta.json()

        print("ORTHANC CONECTADO CORRECTAMENTE")
        print("ESTUDIOS ENCONTRADOS:", len(estudios))

        if estudios:

            # Consultar el estudio mas reciente
            estudio_id = estudios[-1]

            print("ESTUDIO CONSULTADO:", estudio_id)

            respuesta = requests.get(
                f"{ORTHANC}/studies/{estudio_id}/instances",
                timeout=TIMEOUT
            )

            respuesta.raise_for_status()

            instancias = respuesta.json()

            print("INSTANCIAS:", len(instancias))

            for i, instancia in enumerate(instancias):

                instancia_id = instancia["ID"]

                try:
                    preview = requests.get(
                        f"{ORTHANC}/instances/"
                        f"{instancia_id}/preview",
                        timeout=TIMEOUT
                    )

                    preview.raise_for_status()

                    ruta = TEMP / (
                        f"orthanc_{SESION}_{i + 1}.png"
                    )

                    ruta.write_bytes(preview.content)

                    with PILImage.open(ruta) as img:
                        img.verify()

                    imagenes_orthanc.append(
                        (f"ORTHANC - Imagen {i + 1}", ruta)
                    )

                    print("DICOM RECUPERADO:", ruta.name)

                except Exception as e:
                    print("AVISO INSTANCIA:", e)

        else:
            print("ORTHANC NO TIENE ESTUDIOS.")

    except requests.exceptions.ConnectionError:
        print("AVISO: No se pudo conectar con Orthanc.")

    except Exception as e:
        print("AVISO ORTHANC:", e)

    print(
        "NOTA: El estudio recuperado es el ultimo disponible; "
        "no se ha verificado que pertenezca a esta sesion."
    )


# ============================================================
# 8. UNIFICAR IMAGENES
# ============================================================

todas_las_imagenes = imagenes + imagenes_orthanc

print("\nTOTAL DE IMAGENES:", len(todas_las_imagenes))


# ============================================================
# 9. ANALISIS DE IMAGENES CON YOLO
# ============================================================

print("\n==========================================")
print("INICIANDO ANALISIS CON YOLO")
print("==========================================")

resultados = []
total_detecciones = 0

for indice, (nombre, ruta) in enumerate(todas_las_imagenes):

    print("\nANALIZANDO:", nombre)

    try:
        predicciones = modelo.predict(
            source=str(ruta),
            conf=CONFIANZA,
            verbose=False
        )

        resultado = predicciones[0]

        cantidad = len(resultado.boxes)

        total_detecciones += cantidad

        print("DETECCIONES:", cantidad)

        # Dibujar recuadros de deteccion
        imagen_bgr = resultado.plot()
        imagen_rgb = imagen_bgr[:, :, ::-1]

        ruta_procesada = TEMP / (
            f"procesada_{SESION}_{indice + 1}.jpg"
        )

        PILImage.fromarray(
            np.ascontiguousarray(imagen_rgb)
        ).save(ruta_procesada, quality=95)

        detalle = []

        for caja in resultado.boxes:

            clase_id = int(caja.cls[0])
            confianza = float(caja.conf[0])

            if isinstance(modelo.names, dict):
                nombre_clase = modelo.names.get(
                    clase_id,
                    str(clase_id)
                )
            else:
                nombre_clase = modelo.names[clase_id]

            detalle.append({
                "clase": str(nombre_clase),
                "confianza": confianza
            })

        resultados.append({
            "nombre": nombre,
            "archivo": ruta.name,
            "original": ruta,
            "procesada": ruta_procesada,
            "detecciones": cantidad,
            "detalle": detalle
        })

    except Exception as e:
        print("ERROR PROCESANDO IMAGEN:", nombre, e)
        traceback.print_exc()


if not resultados:
    print("ERROR: No se pudo analizar ninguna imagen.")
    sys.exit(1)


# ============================================================
# 10. PREPARAR ESTILOS DEL INFORME
# ============================================================

print("\nPREPARANDO INFORME PDF...")

estilos = getSampleStyleSheet()

titulo = ParagraphStyle(
    "TituloMAKO",
    parent=estilos["Title"],
    fontSize=20,
    leading=25,
    textColor=colors.HexColor("#24547A"),
    alignment=TA_CENTER,
    spaceAfter=15
)

subtitulo = ParagraphStyle(
    "SubtituloMAKO",
    parent=estilos["Heading2"],
    fontSize=13,
    leading=17,
    textColor=colors.HexColor("#24547A"),
    spaceBefore=12,
    spaceAfter=8
)

texto = ParagraphStyle(
    "TextoMAKO",
    parent=estilos["BodyText"],
    fontSize=9,
    leading=13,
    spaceAfter=7
)

contenido = []


# ============================================================
# 11. PORTADA
# ============================================================

contenido.append(
    Paragraph("MAKO SURGICAL IMAGING", titulo)
)

contenido.append(
    Paragraph(
        "INFORME DE ANALISIS CON INTELIGENCIA ARTIFICIAL",
        subtitulo
    )
)

contenido.append(Spacer(1, 15))

datos = [
    ["IDENTIFICACION", "RESULTADO"],
    ["Identificador de sesion", SESION],
    [
        "Fecha",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ],
    ["Modelo utilizado", RUTA_MODELO.name],
    ["Imagenes analizadas", str(len(resultados))],
    ["Detecciones totales", str(total_detecciones)],
    ["Servidor PACS", "Orthanc"],
    ["Estado", "Analisis finalizado"]
]

tabla = Table(
    datos,
    colWidths=[7 * cm, 9 * cm]
)

tabla.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0),
     colors.HexColor("#24547A")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("PADDING", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
]))

contenido.append(tabla)
contenido.append(Spacer(1, 15))


# ============================================================
# 12. RESUMEN DE RESULTADOS
# ============================================================

contenido.append(
    Paragraph("1. RESUMEN DEL ANALISIS", subtitulo)
)

contenido.append(
    Paragraph(
        "El sistema MAKO PACS procesa imagenes obtenidas "
        "del entorno de simulacion quirurgica. El modelo "
        "YOLO realiza detecciones visuales de las clases "
        "aprendidas durante su entrenamiento.",
        texto
    )
)

filas = [
    ["CAMARA / ORIGEN", "DETECCIONES", "CLASES"]
]

for item in resultados:

    clases = sorted(set(
        d["clase"] for d in item["detalle"]
    ))

    clases_texto = ", ".join(clases)

    if not clases_texto:
        clases_texto = "Sin detecciones"

    filas.append([
        item["nombre"],
        str(item["detecciones"]),
        clases_texto
    ])

tabla_resultados = Table(
    filas,
    colWidths=[5 * cm, 3 * cm, 8 * cm],
    repeatRows=1
)

tabla_resultados.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0),
     colors.HexColor("#24547A")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("PADDING", (0, 0), (-1, -1), 7),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
]))

contenido.append(tabla_resultados)


# ============================================================
# 13. FUNCION PARA AGREGAR IMAGENES
# ============================================================

def agregar_imagen(ruta, ancho_max=15.5, alto_max=8):

    with PILImage.open(ruta) as img:
        ancho, alto = img.size

    factor = min(
        (ancho_max * cm) / ancho,
        (alto_max * cm) / alto
    )

    return Image(
        str(ruta),
        width=ancho * factor,
        height=alto * factor
    )


# ============================================================
# 14. IMAGENES ORIGINALES Y RESULTADOS YOLO
# ============================================================

for item in resultados:

    contenido.append(PageBreak())

    contenido.append(
        Paragraph(
            "2. ANALISIS: " + html.escape(item["nombre"]),
            subtitulo
        )
    )

    contenido.append(
        Paragraph(
            "Archivo: " + html.escape(item["archivo"]),
            texto
        )
    )

    contenido.append(
        Paragraph(
            f"Detecciones identificadas: {item['detecciones']}",
            texto
        )
    )

    contenido.append(
        Paragraph("IMAGEN ORIGINAL", estilos["Heading3"])
    )

    contenido.append(
        agregar_imagen(item["original"])
    )

    contenido.append(Spacer(1, 10))

    contenido.append(
        Paragraph(
            "IMAGEN PROCESADA CON YOLO",
            estilos["Heading3"]
        )
    )

    contenido.append(
        agregar_imagen(item["procesada"])
    )

    contenido.append(Spacer(1, 12))

    contenido.append(
        Paragraph(
            "DETALLE DE DETECCIONES",
            estilos["Heading3"]
        )
    )

    if item["detalle"]:

        for d in item["detalle"]:

            contenido.append(
                Paragraph(
                    "Clase: " + html.escape(d["clase"]) +
                    " | Confianza: " +
                    f"{d['confianza'] * 100:.2f}%",
                    texto
                )
            )

    else:

        contenido.append(
            Paragraph(
                "No se identificaron objetos con el umbral "
                "de confianza configurado.",
                texto
            )
        )


# ============================================================
# 15. CONCLUSION
# ============================================================

contenido.append(PageBreak())

contenido.append(
    Paragraph("3. CONCLUSION", subtitulo)
)

contenido.append(
    Paragraph(
        f"Se procesaron {len(resultados)} imagenes y se "
        f"registraron {total_detecciones} detecciones "
        "mediante el modelo YOLO. Los resultados representan "
        "un analisis experimental de reconocimiento visual "
        "en el entorno de simulacion MAKO.",
        texto
    )
)

contenido.append(
    Paragraph("4. LIMITACIONES", subtitulo)
)

contenido.append(
    Paragraph(
        "Las detecciones generadas por inteligencia artificial "
        "son resultados experimentales y dependen del modelo, "
        "sus clases de entrenamiento y el umbral de confianza. "
        "No constituyen un diagnostico medico ni una validacion "
        "clinica o de seguridad quirurgica.",
        texto
    )
)


# ============================================================
# 16. GENERAR PDF Y COPIAR RESULTADOS
# ============================================================

NOMBRE_PDF = f"informe_MAKO_IA_{SESION}.pdf"

# PDF original
RUTA_PDF = SALIDA / NOMBRE_PDF

# Copia general
RUTA_PDF_GENERAL = RESULTADOS / NOMBRE_PDF

# Imagenes procesadas en carpeta comun
CARPETA_IMAGENES_GENERAL = (
    RESULTADOS / "imagenes_procesadas"
)

print("\nGENERANDO DOCUMENTO PDF...")

try:

    documento = SimpleDocTemplate(
        str(RUTA_PDF),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Informe MAKO PACS IA",
        author="MAKO PACS"
    )

    documento.build(contenido)

    # Verificar PDF original
    if not RUTA_PDF.exists():
        raise RuntimeError("El archivo PDF no existe.")

    if RUTA_PDF.stat().st_size == 0:
        raise RuntimeError("El archivo PDF esta vacio.")

    # Crear carpeta de imagenes procesadas
    CARPETA_IMAGENES_GENERAL.mkdir(
        parents=True,
        exist_ok=True
    )

    # Copiar PDF a carpeta general
    shutil.copy2(
        RUTA_PDF,
        RUTA_PDF_GENERAL
    )

    # Copiar imagenes procesadas por YOLO
    imagenes_copiadas = 0

    for item in resultados:

        ruta_procesada = Path(item["procesada"])

        if ruta_procesada.exists():

            destino = (
                CARPETA_IMAGENES_GENERAL /
                ruta_procesada.name
            )

            shutil.copy2(
                ruta_procesada,
                destino
            )

            imagenes_copiadas += 1

    # Verificar copia general
    if not RUTA_PDF_GENERAL.exists():
        raise RuntimeError(
            "No se pudo crear la copia del PDF general."
        )

    if RUTA_PDF_GENERAL.stat().st_size == 0:
        raise RuntimeError(
            "La copia general del PDF esta vacia."
        )

    print("\n==========================================")
    print("INFORME IA GENERADO CORRECTAMENTE")
    print("==========================================")

    print("PDF ORIGINAL:", RUTA_PDF)

    print("COPIA GENERAL:", RUTA_PDF_GENERAL)

    print("IMAGENES PROCESADAS:", imagenes_copiadas)

    print("CARPETA GENERAL:", RESULTADOS)

    print("SESION:", SESION)

    print("IMAGENES ANALIZADAS:", len(resultados))

    print("DETECCIONES:", total_detecciones)

    print("TAMANO:", RUTA_PDF.stat().st_size, "bytes")

    print("==========================================")

except Exception as e:

    print("\nERROR AL GENERAR PDF:", str(e))

    traceback.print_exc()

    sys.exit(1)


# ============================================================
# FIN DEL PROGRAMA
# ============================================================
