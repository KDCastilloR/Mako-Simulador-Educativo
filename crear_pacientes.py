
import os
import json
from datetime import datetime

BASE = r"C:\MAKO_PACS\datos\pacientes"

os.makedirs(BASE, exist_ok=True)

fecha = datetime.now().strftime("%Y-%m-%d")

pacientes = [
    {
        "paciente_id": "FICT-MAKO-001",
        "nombre": "PACIENTE DEMOSTRACION 001",
        "tipo_registro": "FICTICIO",
        "edad": 45,
        "sexo": "No especificado",
        "region_anatomica": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Simulacion quirurgica MAKO",
        "descripcion": "Caso principal correspondiente al modelo de rodilla derecha desarrollado en CoppeliaSim.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": [
            "Camara Doctor",
            "Camara MAKO"
        ],
        "estado": "Simulacion realizada",
        "fecha_registro": fecha
    },
    {
        "paciente_id": "FICT-MAKO-002",
        "nombre": "PACIENTE DEMOSTRACION 002",
        "tipo_registro": "FICTICIO",
        "edad": 52,
        "sexo": "No especificado",
        "region_anatomica": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Planificacion quirurgica simulada",
        "descripcion": "Expediente ficticio para pruebas adicionales del sistema.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": [],
        "estado": "Expediente de demostracion",
        "fecha_registro": fecha
    },
    {
        "paciente_id": "FICT-MAKO-003",
        "nombre": "PACIENTE DEMOSTRACION 003",
        "tipo_registro": "FICTICIO",
        "edad": 38,
        "sexo": "No especificado",
        "region_anatomica": "Rodilla derecha",
        "lateralidad": "Derecha",
        "procedimiento": "Seguimiento de simulacion",
        "descripcion": "Expediente ficticio para pruebas y seguimiento del simulador.",
        "sistema": "CoppeliaSim MAKO",
        "modalidad": "OT",
        "imagenes": [],
        "estado": "Expediente de demostracion",
        "fecha_registro": fecha
    }
]

for paciente in pacientes:

    nombre = paciente["paciente_id"] + ".json"
    ruta = os.path.join(BASE, nombre)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(
            paciente,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print("Expediente creado:", nombre)

print("--------------------------------")
print("3 EXPEDIENTES GENERADOS")
print("Todos corresponden a rodilla derecha")
print("--------------------------------")
