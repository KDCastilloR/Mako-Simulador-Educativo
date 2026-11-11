
import requests
import os

# ==========================================
# CONFIGURACION DE ORTHANC
# ==========================================

ORTHANC_URL = "http://localhost:8042/instances"

# CARPETA PRINCIPAL DEL PROYECTO
CARPETA = r"C:\MAKO_PACS\datos_dicom"

# ARCHIVOS DICOM GENERADOS POR MAKO
archivos = [
    "camara doctor.dcm",
    "camara mako.dcm"
]

print("\n======================================")
print("       MAKO PACS - ENVIO A ORTHANC")
print("======================================")

# ==========================================
# VERIFICAR CONEXION CON ORTHANC
# ==========================================

try:
    conexion = requests.get(
        "http://localhost:8042/system",
        timeout=10
    )

    conexion.raise_for_status()

    print("Orthanc conectado correctamente")
    print("Servidor:", conexion.json().get("Name"))

except Exception as error:
    print("ERROR: No se pudo conectar con Orthanc")
    print(error)
    raise SystemExit

# ==========================================
# ENVIO DE LAS IMAGENES DICOM
# ==========================================

for nombre in archivos:

    ruta = os.path.join(CARPETA, nombre)

    print("\nProcesando:", nombre)

    if not os.path.isfile(ruta):
        print("NO ENCONTRADO:", ruta)
        continue

    try:
        with open(ruta, "rb") as archivo:

            respuesta = requests.post(
                ORTHANC_URL,
                data=archivo,
                headers={
                    "Content-Type": "application/dicom"
                },
                timeout=60
            )

        if respuesta.status_code in (200, 201):

            resultado = respuesta.json()

            print("ENVIADO CORRECTAMENTE")
            print("ID Orthanc:", resultado.get("ID"))

        else:

            print("ERROR EN EL ENVIO")
            print("Codigo:", respuesta.status_code)
            print("Detalle:", respuesta.text)

    except Exception as error:

        print("ERROR:", str(error))

# ==========================================
# FINALIZACION
# ==========================================

print("\n======================================")
print("       PROCESO FINALIZADO")
print("======================================")

