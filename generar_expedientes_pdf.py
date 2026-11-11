
import os
import json
import glob
import requests
from datetime import datetime
from xml.sax.saxutils import escape

from ultralytics import YOLO
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, Image
)

# ==================================================
# 1. CONFIGURACION GENERAL
# ==================================================

BASE = r"C:\MAKO_PACS"

CARPETA_CAPTURAS = os.path.join(BASE, "capturas_png")
CARPETA_JSON = os.path.join(BASE, "datos", "pacientes")
CARPETA_PDF = os.path.join(BASE, "datos", "expedientes_pdf")
CARPETA_PDF = os.path.join(BASE, "datos", "RESULTADOS_MAKO")
CARPETA_IA = os.path.join(CARPETA_PDF, "analisis_IA")

MODELO_IA = os.path.join(
    BASE, "IA", "runs", "detect",
    "segundo_entrenamiento", "weights", "best.pt"
)

ORTHANC_URL = "http://localhost:8042"

STUDY_ID = "be4ed1b9-9bb802f6-7d7f9ca3-edbd0fbf-c130c7b9"

CONFIANZA = 0.25

os.makedirs(CARPETA_CAPTURAS, exist_ok=True)
os.makedirs(CARPETA_JSON, exist_ok=True)
os.makedirs(CARPETA_PDF, exist_ok=True)
os.makedirs(CARPETA_IA, exist_ok=True)

fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==================================================
# 2. CONECTAR CON ORTHANC
# ==================================================

orthanc_study_uid = ""
orthanc_patient_id = ""

try:
    r = requests.get(
        ORTHANC_URL + "/studies/" + STUDY_ID,
        timeout=10
    )
    r.raise_for_status()

    info = r.json()
    tags = info.get("MainDicomTags", {})

    orthanc_study_uid = tags.get("StudyInstanceUID", "")
    orthanc_patient_id = info.get("ParentPatient", "")

    print("ORTHANC: estudio consultado correctamente")

except Exception as error:
    print("AVISO ORTHANC:", error)

# ==================================================
# 3. CARGAR MODELO YOLO
# ==================================================

print("Cargando modelo de inteligencia artificial...")

if not os.path.isfile(MODELO_IA):
    raise FileNotFoundError(
        "No se encontro el modelo YOLO: " + MODELO_IA
    )

modelo = YOLO(MODELO_IA)

print("MODELO YOLO CARGADO CORRECTAMENTE")
print("Clases:", modelo.names)

# ==================================================
# 4. LOCALIZAR LAS TRES CAPTURAS
# ==================================================

def buscar_capturas():

    archivos = {}

    for camara in ["doctor", "mako", "lampara"]:

        patron = os.path.join(
            CARPETA_CAPTURAS,
            camara + "_*.png"
        )

        encontrados = glob.glob(patron)

        if encontrados:
            archivos[camara] = encontrados

    # Buscar una marca de tiempo compartida
    marcas = []

    if len(archivos) == 3:

        for ruta in archivos["doctor"]:
            marca = os.path.basename(ruta)[7:-4]

            ruta_mako = os.path.join(
                CARPETA_CAPTURAS,
                "mako_" + marca + ".png"
            )

            ruta_lampara = os.path.join(
                CARPETA_CAPTURAS,
                "lampara_" + marca + ".png"
            )

            if os.path.isfile(ruta_mako) and os.path.isfile(ruta_lampara):
                marcas.append(marca)

    if not marcas:
        raise FileNotFoundError(
            "No se encontro un grupo completo de capturas "
            "Doctor, MAKO y Lampara con la misma fecha. "
            "Presiona CAPTURAR LAS 3 CAMARAS en CoppeliaSim."
        )

    marca = sorted(marcas)[-1]

    resultado = {
        "doctor": os.path.join(
            CARPETA_CAPTURAS, "doctor_" + marca + ".png"
        ),
        "mako": os.path.join(
            CARPETA_CAPTURAS, "mako_" + marca + ".png"
        ),
        "lampara": os.path.join(
            CARPETA_CAPTURAS, "lampara_" + marca + ".png"
        )
    }

    return marca, resultado


# ==================================================
# 5. ANALISIS DE IMAGENES CON YOLO
# ==================================================

def analizar_imagen(nombre, ruta, marca):

    print("Analizando:", nombre)

    resultados = modelo.predict(
        source=ruta,
        conf=CONFIANZA,
        save=False,
        verbose=False
    )

    resultado = resultados[0]

    # Obtener imagen con recuadros de deteccion
    imagen_anotada = resultado.plot()

    ruta_anotada = os.path.join(
        CARPETA_IA,
        nombre + "_" + marca + "_IA.png"
    )

    # YOLO entrega la imagen en BGR.
    # Se convierte a RGB para guardarla con Pillow.
    PILImage.fromarray(
        imagen_anotada[:, :, ::-1]
    ).save(ruta_anotada)

    detecciones = []

    if resultado.boxes is not None:

        for caja in resultado.boxes:

            clase_id = int(caja.cls[0].item())
            confianza = float(caja.conf[0].item())

            nombre_clase = modelo.names[clase_id]

            coordenadas = [
                round(float(v), 2)
                for v in caja.xyxy[0].tolist()
            ]

            detecciones.append({
                "clase": nombre_clase,
                "confianza": round(confianza * 100, 2),
                "coordenadas": coordenadas
            })

    print(
        nombre,
        "- Detecciones:",
        len(detecciones)
    )

    return {
        "camara": nombre,
        "imagen_original": ruta,
        "imagen_analizada": ruta_anotada,
        "cantidad_detecciones": len(detecciones),
        "detecciones": detecciones
    }


# ==================================================
# 6. ESTILOS DEL DOCUMENTO
# ==================================================

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="TituloMAKO",
    parent=styles["Title"],
    alignment=TA_CENTER,
    textColor=colors.HexColor("#24547A"),
    fontSize=19,
    spaceAfter=18
))

styles.add(ParagraphStyle(
    name="AvisoMAKO",
    parent=styles["Normal"],
    textColor=colors.HexColor("#A33A2B"),
    alignment=TA_CENTER,
    fontSize=9
))

def texto(valor):
    return escape(str(valor))


# ==================================================
# 7. EXPEDIENTES DE DEMOSTRACION
# ==================================================

pacientes = [

    {
        "paciente_id": "FICT-MAKO-001",
        "nombre": "PACIENTE DEMO 001",
        "tipo": "FICTICIO - SIMULACION",
        "edad": 45,
        "sexo": "No especificado",
        "region": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Simulacion quirurgica MAKO",
        "descripcion": "Caso principal correspondiente al modelo de rodilla derecha desarrollado en CoppeliaSim.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": ["Camara Doctor", "Camara MAKO"],
        "orthanc_study_id": STUDY_ID,
        "dicom_study_uid": orthanc_study_uid,
        "orthanc_patient_internal_id": orthanc_patient_id,
        "fecha_registro": fecha
    },

    {
        "paciente_id": "FICT-MAKO-002",
        "nombre": "PACIENTE DEMO 002",
        "tipo": "FICTICIO - SIMULACION",
        "edad": 52,
        "sexo": "No especificado",
        "region": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Planificacion quirurgica simulada",
        "descripcion": "Expediente de demostracion para pruebas del sistema.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": [],
        "orthanc_study_id": "",
        "dicom_study_uid": "",
        "orthanc_patient_internal_id": "",
        "fecha_registro": fecha
    },

    {
        "paciente_id": "FICT-MAKO-003",
        "nombre": "PACIENTE DEMO 003",
        "tipo": "FICTICIO - SIMULACION",
        "edad": 38,
        "sexo": "No especificado",
        "region": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Seguimiento de simulacion",
        "descripcion": "Expediente de demostracion para seguimiento del simulador.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": [],
        "orthanc_study_id": "",
        "dicom_study_uid": "",
        "orthanc_patient_internal_id": "",
        "fecha_registro": fecha
    }
]


# ==================================================
# 8. GENERAR PDF DE LOS TRES EXPEDIENTES
# ==================================================

def crear_pdf(paciente, ruta):

    doc = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48
    )

    contenido = []

    contenido.append(Paragraph(
        "MAKO PACS - EXPEDIENTE DE SIMULACION",
        styles["TituloMAKO"]
    ))

    contenido.append(Paragraph(
        "DOCUMENTO FICTICIO - NO ES UN EXPEDIENTE CLINICO REAL",
        styles["AvisoMAKO"]
    ))

    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "1. Identificacion del paciente",
        styles["Heading2"]
    ))

    datos = [
        ["Campo", "Informacion"],
        ["Identificador", paciente["paciente_id"]],
        ["Nombre", paciente["nombre"]],
        ["Edad", str(paciente["edad"]) + " años"],
        ["Sexo", paciente["sexo"]],
        ["Tipo", paciente["tipo"]]
    ]

    tabla = Table(datos, colWidths=[150, 330])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24547A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    contenido.append(tabla)
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "2. Informacion del procedimiento",
        styles["Heading2"]
    ))

    procedimiento = [
        ["Region anatomica", paciente["region"]],
        ["Lateralidad", paciente["lateralidad"]],
        ["Procedimiento", paciente["procedimiento"]],
        ["Sistema", paciente["sistema"]],
        ["Modalidad", paciente["modalidad"]],
        ["Descripcion", paciente["descripcion"]]
    ]

    tabla = Table(procedimiento, colWidths=[150, 330])

    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    contenido.append(tabla)
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "3. Almacenamiento DICOM",
        styles["Heading2"]
    ))

    contenido.append(Paragraph(
        "Orthanc: " + texto(paciente["orthanc_study_id"] or "No asociado"),
        styles["Normal"]
    ))

    contenido.append(Paragraph(
        "Study Instance UID: " + texto(
            paciente["dicom_study_uid"] or "No disponible"
        ),
        styles["Normal"]
    ))

    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "4. Registro del sistema",
        styles["Heading2"]
    ))

    contenido.append(Paragraph(
        "Fecha: " + texto(paciente["fecha_registro"]),
        styles["Normal"]
    ))

    contenido.append(Spacer(1, 20))

    contenido.append(Paragraph(
        "Documento de demostracion academica. No constituye "
        "diagnostico ni recomendacion medica.",
        styles["AvisoMAKO"]
    ))

    doc.build(contenido)


# ==================================================
# 9. GENERAR EXPEDIENTE DE SESION CON IA
# ==================================================

def crear_pdf_sesion(marca, capturas, analisis):

    ruta_pdf = os.path.join(
        CARPETA_PDF,
        "expediente_sesion_MAKO_" + marca + ".pdf"
    )

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    contenido = []

    contenido.append(Paragraph(
        "MAKO PACS - EXPEDIENTE DE SESION",
        styles["TituloMAKO"]
    ))

    contenido.append(Paragraph(
        "INFORME DE SIMULACION Y ANALISIS AUTOMATIZADO POR IA",
        styles["AvisoMAKO"]
    ))

    contenido.append(Spacer(1, 15))

    contenido.append(Paragraph(
        "1. Datos de la sesion",
        styles["Heading2"]
    ))

    contenido.append(Paragraph(
        "Identificador de sesion: " + texto(marca),
        styles["Normal"]
    ))

    contenido.append(Paragraph(
        "Fecha de procesamiento: " + texto(fecha),
        styles["Normal"]
    ))

    contenido.append(Paragraph(
        "Modelo: YOLO - " + texto(os.path.basename(MODELO_IA)),
        styles["Normal"]
    ))

    contenido.append(Spacer(1, 15))

    contenido.append(Paragraph(
        "2. Resultados de inteligencia artificial",
        styles["Heading2"]
    ))

    for item in analisis:

        contenido.append(Paragraph(
            "Camara: " + texto(item["camara"]),
            styles["Heading3"]
        ))

        contenido.append(Paragraph(
            "Total de detecciones: " +
            str(item["cantidad_detecciones"]),
            styles["Normal"]
        ))

        if item["detecciones"]:

            filas = [
                ["Clase detectada", "Confianza", "Coordenadas"]
            ]

            for d in item["detecciones"]:
                filas.append([
                    texto(d["clase"]),
                    str(d["confianza"]) + "%",
                    texto(d["coordenadas"])
                ])

            tabla = Table(
                filas,
                colWidths=[150, 85, 235],
                repeatRows=1
            )

            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#24547A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ]))

            contenido.append(tabla)

        else:
            contenido.append(Paragraph(
                "No se detectaron objetos con el umbral configurado.",
                styles["Normal"]
            ))

        contenido.append(Spacer(1, 10))

    contenido.append(PageBreak())

    contenido.append(Paragraph(
        "3. Evidencia fotografica",
        styles["Heading2"]
    ))

    for item in analisis:

        contenido.append(Paragraph(
            "Camara " + texto(item["camara"]),
            styles["Heading3"]
        ))

        contenido.append(Paragraph(
            "Imagen original",
            styles["Normal"]
        ))

        imagen_original = Image(
            item["imagen_original"],
            width=430,
            height=250,
            kind="proportional"
        )

        contenido.append(imagen_original)
        contenido.append(Spacer(1, 10))

        contenido.append(Paragraph(
            "Imagen procesada mediante YOLO",
            styles["Normal"]
        ))

        imagen_ia = Image(
            item["imagen_analizada"],
            width=430,
            height=250,
            kind="proportional"
        )

        contenido.append(imagen_ia)
        contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "4. Almacenamiento y trazabilidad",
        styles["Heading2"]
    ))

    contenido.append(Paragraph(
        "Identificador de estudio Orthanc: " +
        texto(STUDY_ID),
        styles["Normal"]
    ))

    contenido.append(Paragraph(
        "Este informe corresponde a una simulacion academica. "
        "Las detecciones de YOLO representan resultados de "
        "vision artificial y no constituyen una evaluacion "
        "clinica ni una recomendacion quirurgica.",
        styles["AvisoMAKO"]
    ))

    doc.build(contenido)

    return ruta_pdf


# ==================================================
# 10. EJECUTAR PROCESAMIENTO
# ==================================================

print("\nGENERANDO EXPEDIENTES MAKO PACS")

# Crear los tres expedientes originales
for paciente in pacientes:

    identificador = paciente["paciente_id"]

    ruta_json = os.path.join(
        CARPETA_JSON,
        identificador + ".json"
    )

    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(
            paciente,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    ruta_pdf = os.path.join(
        CARPETA_PDF,
        identificador + ".pdf"
    )

    crear_pdf(paciente, ruta_pdf)

    print("Expediente creado:", ruta_pdf)


# Buscar y analizar las tres capturas
marca, capturas = buscar_capturas()

print("\nSESION:", marca)

analisis = []

for nombre, ruta in capturas.items():

    resultado = analizar_imagen(
        nombre,
        ruta,
        marca
    )

    analisis.append(resultado)


# Crear JSON de resultados de IA
ruta_json_ia = os.path.join(
    CARPETA_IA,
    "analisis_MAKO_" + marca + ".json"
)

with open(ruta_json_ia, "w", encoding="utf-8") as archivo:

    json.dump(
        {
            "sesion": marca,
            "fecha": fecha,
            "modelo": MODELO_IA,
            "confianza_minima": CONFIANZA,
            "resultados": analisis
        },
        archivo,
        indent=4,
        ensure_ascii=False
    )


# Generar PDF de la sesion
ruta_pdf_sesion = crear_pdf_sesion(
    marca,
    capturas,
    analisis
)

print("\nPDF DE SESION:", ruta_pdf_sesion)


# ==================================================
# 11. CATALOGO GENERAL
# ==================================================

ruta_general = os.path.join(
    CARPETA_PDF,
    "catalogo_expedientes_MAKO.pdf"
)

doc = SimpleDocTemplate(
    ruta_general,
    pagesize=letter
)

contenido = [
    Paragraph(
        "MAKO PACS - CATALOGO DE EXPEDIENTES",
        styles["TituloMAKO"]
    ),
    Paragraph(
        "DOCUMENTO DE DEMOSTRACION - PACIENTES FICTICIOS",
        styles["AvisoMAKO"]
    ),
    Spacer(1, 20)
]

for paciente in pacientes:

    contenido.append(Paragraph(
        texto(paciente["paciente_id"]) + " - " +
        texto(paciente["nombre"]),
        styles["Heading2"]
    ))

    contenido.append(Paragraph(
        "Region: " + texto(paciente["region"]) +
        " | Procedimiento: " +
        texto(paciente["procedimiento"]),
        styles["Normal"]
    ))

    contenido.append(Spacer(1, 12))

contenido.append(PageBreak())

contenido.append(Paragraph(
    "ULTIMA SESION ANALIZADA",
    styles["Heading2"]
))

contenido.append(Paragraph(
    "Identificador: " + texto(marca),
    styles["Normal"]
))

contenido.append(Paragraph(
    "Expediente: " + texto(os.path.basename(ruta_pdf_sesion)),
    styles["Normal"]
))

doc.build(contenido)

print("\nPDF GENERAL:", ruta_general)
print("\nEXPEDIENTES Y PDF GENERADOS CORRECTAMENTE")
