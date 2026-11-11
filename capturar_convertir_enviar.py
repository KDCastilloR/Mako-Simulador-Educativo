
import os
import sys
import requests
from datetime import datetime
from PIL import Image

from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import (
    generate_uid,
    SecondaryCaptureImageStorage,
    ExplicitVRLittleEndian
)

BASE = r"C:\MAKO_PACS"
PNG_DIR = os.path.join(BASE, "capturas_png")
DICOM_DIR = os.path.join(BASE, "datos_dicom")
ORTHANC = "http://localhost:8042/instances"

os.makedirs(PNG_DIR, exist_ok=True)
os.makedirs(DICOM_DIR, exist_ok=True)


def convertir(nombre_png, descripcion, study_uid, timestamp, serie):

    ruta_png = os.path.join(PNG_DIR, nombre_png)

    if not os.path.isfile(ruta_png):
        raise FileNotFoundError("No existe: " + ruta_png)

    imagen = Image.open(ruta_png).convert("RGB")
    ancho, alto = imagen.size

    sop_uid = generate_uid()
    series_uid = generate_uid()

    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = sop_uid
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.ImplementationClassUID = generate_uid()

    nombre_dicom = descripcion.lower().replace(" ", "_") + "_" + timestamp + ".dcm"
    ruta_dicom = os.path.join(DICOM_DIR, nombre_dicom)

    ds = FileDataset(
        ruta_dicom,
        {},
        file_meta=meta,
        preamble=b"\0" * 128
    )

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Paciente ficticio
    ds.PatientName = "PACIENTE^DEMO"
    ds.PatientID = "FICT-MAKO-001"
    ds.PatientSex = "O"

    # Estudio y serie
    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = series_uid
    ds.SOPInstanceUID = sop_uid
    ds.SOPClassUID = SecondaryCaptureImageStorage

    ds.Modality = "OT"
    ds.StudyDescription = "SIMULACION QUIRURGICA MAKO"
    ds.SeriesDescription = descripcion
    ds.SeriesNumber = serie
    ds.InstanceNumber = 1
    ds.BodyPartExamined = "KNEE"

    fecha = datetime.now()
    ds.StudyDate = fecha.strftime("%Y%m%d")
    ds.StudyTime = fecha.strftime("%H%M%S")

    ds.Manufacturer = "MAKO PACS SIMULATOR"
    ds.ManufacturerModelName = "CoppeliaSim"
    ds.ConversionType = "WSD"
    ds.ImageType = ["DERIVED", "SECONDARY"]

    # Imagen RGB
    ds.SamplesPerPixel = 3
    ds.PhotometricInterpretation = "RGB"
    ds.PlanarConfiguration = 0
    ds.Rows = alto
    ds.Columns = ancho
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = imagen.tobytes()

    ds.save_as(ruta_dicom, write_like_original=False)

    print("DICOM creado:", nombre_dicom)
    return ruta_dicom


def enviar_orthanc(ruta):

    with open(ruta, "rb") as archivo:
        respuesta = requests.post(
            ORTHANC,
            data=archivo,
            headers={"Content-Type": "application/dicom"},
            timeout=60
        )

    respuesta.raise_for_status()
    resultado = respuesta.json()

    if resultado.get("Status") not in ("Success", "AlreadyStored"):
        raise RuntimeError("Orthanc no confirmó el almacenamiento: " + str(resultado))

    print("ENVIADO A ORTHANC:", os.path.basename(ruta))
    print("ID:", resultado.get("ID"))


def main():

    if len(sys.argv) < 2:
        raise ValueError("Falta el identificador de la captura.")

    marca = sys.argv[1]

    print("=== MAKO PACS: CAPTURA Y ENVIO ===")

    # Comprobar conexión
    respuesta = requests.get(
        "http://localhost:8042/system",
        timeout=10
    )
    respuesta.raise_for_status()

    print("Orthanc conectado:", respuesta.json().get("Name"))

    # Un estudio nuevo para cada captura simultánea
    study_uid = generate_uid()

    doctor = convertir(
        "doctor_" + marca + ".png",
        "CAMARA DOCTOR",
        study_uid,
        marca,
        1
    )

    mako = convertir(
        "mako_" + marca + ".png",
        "CAMARA MAKO",
        study_uid,
        marca,
        2
    )

    enviar_orthanc(doctor)
    enviar_orthanc(mako)

    print("================================")
    print("CAPTURA, CONVERSION Y ENVIO OK")
    print("================================")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR:", str(error))
        sys.exit(1)
