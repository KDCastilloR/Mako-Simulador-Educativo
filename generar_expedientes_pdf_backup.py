import hashlib

# Compatibilidad con Python 3.8
_md5_original = hashlib.md5

def md5_compatible(data=b'', **kwargs):
    return _md5_original(data)

hashlib.md5 = md5_compatible
import os
import json
import requests
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak
)

BASE = r"C:\MAKO_PACS"
CARPETA_JSON = os.path.join(BASE, "datos", "pacientes")
CARPETA_PDF = os.path.join(BASE, "datos", "expedientes_pdf")

ORTHANC_URL = "http://localhost:8042"
STUDY_ID = "be4ed1b9-9bb802f6-7d7f9ca3-edbd0fbf-c130c7b9"

os.makedirs(CARPETA_JSON, exist_ok=True)
os.makedirs(CARPETA_PDF, exist_ok=True)

fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Consultar el estudio principal existente en Orthanc
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
except Exception as error:
    print("Aviso: no se pudo consultar el estudio:", error)

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
    name="Aviso",
    parent=styles["Normal"],
    textColor=colors.HexColor("#A33A2B"),
    alignment=TA_CENTER,
    fontSize=9
))

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
        "DOCUMENTO FICTICIO - NO CORRESPONDE A UN EXPEDIENTE CLINICO REAL",
        styles["Aviso"]
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
        ["Tipo de registro", paciente["tipo"]]
    ]

    tabla = Table(datos, colWidths=[150, 330])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24547A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
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
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    contenido.append(tabla)
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "3. Imagenes y almacenamiento DICOM",
        styles["Heading2"]
    ))

    imagenes = ", ".join(paciente["imagenes"]) or "Sin imagenes asociadas"
    contenido.append(Paragraph("Camaras: " + imagenes, styles["Normal"]))
    contenido.append(Spacer(1, 8))

    contenido.append(Paragraph(
        "Identificador del estudio Orthanc: " +
        (paciente["orthanc_study_id"] or "No asociado"),
        styles["Normal"]
    ))
    contenido.append(Paragraph(
        "Study Instance UID: " +
        (paciente["dicom_study_uid"] or "No disponible"),
        styles["Normal"]
    ))
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph(
        "4. Registro del sistema",
        styles["Heading2"]
    ))
    contenido.append(Paragraph(
        "Fecha de registro: " + paciente["fecha_registro"],
        styles["Normal"]
    ))
    contenido.append(Spacer(1, 20))

    contenido.append(Paragraph(
        "Este documento se genera exclusivamente para demostracion "
        "academica del simulador MAKO PACS. No representa una evaluacion, "
        "diagnostico ni recomendacion medica.",
        styles["Aviso"]
    ))

    doc.build(contenido)


print("GENERANDO EXPEDIENTES MAKO PACS")

for paciente in pacientes:
    identificador = paciente["paciente_id"]

    ruta_json = os.path.join(
        CARPETA_JSON, identificador + ".json"
    )
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(
            paciente, archivo, indent=4, ensure_ascii=False
        )

    ruta_pdf = os.path.join(
        CARPETA_PDF, identificador + ".pdf"
    )
    crear_pdf(paciente, ruta_pdf)

    print("JSON creado:", ruta_json)
    print("PDF creado:", ruta_pdf)

# PDF general
ruta_general = os.path.join(
    CARPETA_PDF, "catalogo_expedientes_MAKO.pdf"
)

doc = SimpleDocTemplate(ruta_general, pagesize=letter)
contenido = [
    Paragraph("MAKO PACS - CATALOGO DE EXPEDIENTES",
              styles["TituloMAKO"]),
    Paragraph(
        "DOCUMENTO DE DEMOSTRACION - PACIENTES FICTICIOS",
        styles["Aviso"]
    ),
    Spacer(1, 20)
]

for paciente in pacientes:
    contenido.append(Paragraph(
        paciente["paciente_id"] + " - " + paciente["nombre"],
        styles["Heading2"]
    ))
    contenido.append(Paragraph(
        "Region: " + paciente["region"] +
        " | Procedimiento: " + paciente["procedimiento"],
        styles["Normal"]
    ))
    contenido.append(Spacer(1, 12))

doc.build(contenido)

print("PDF GENERAL:", ruta_general)
print("EXPEDIENTES Y PDF GENERADOS CORRECTAMENTE")
