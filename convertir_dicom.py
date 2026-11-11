
import os
from datetime import datetime
from PIL import Image
import pydicom

from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import (
    generate_uid,
    SecondaryCaptureImageStorage,
    ExplicitVRLittleEndian
)

# =====================================
# CONFIGURACION DEL PROYECTO MAKO PACS
# =====================================

BASE = os.path.dirname(os.path.abspath(__file__))

CARPETA_PNG = os.path.join(BASE, "capturas_png")
CARPETA_DICOM = os.path.join(BASE, "datos_dicom")

os.makedirs(CARPETA_DICOM, exist_ok=True)

# Expediente ficticio
PACIENTE_ID = "FICT-MAKO-001"
PACIENTE_NOMBRE = "PACIENTE^DEMO"
FECHA = datetime.now()

STUDY_UID = generate_uid()


def convertir(imagen_nombre, descripcion):

    ruta_png = os.path.join(CARPETA_PNG, imagen_nombre)

    if not os.path.exists(ruta_png):
        raise FileNotFoundError(
            "No se encontro: " + ruta_png
        )

    # Leer imagen y convertir a RGB
    imagen = Image.open(ruta_png).convert("RGB")

    ancho, alto = imagen.size
    pixel_data = imagen.tobytes()

    # Crear identificadores DICOM
    SOP_UID = generate_uid()
    SERIES_UID = generate_uid()

    # Metadatos del archivo
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = SOP_UID
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.ImplementationClassUID = generate_uid()

    # Crear archivo DICOM
    nombre_salida = descripcion.lower() + ".dcm"
    ruta_salida = os.path.join(CARPETA_DICOM, nombre_salida)

    ds = FileDataset(
        ruta_salida,
        {},
        file_meta=meta,
        preamble=b"\0" * 128
    )

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Informacion del paciente
    ds.PatientName = PACIENTE_NOMBRE
    ds.PatientID = PACIENTE_ID
    ds.PatientBirthDate = "20000101"
    ds.PatientSex = "O"

    # Informacion del estudio
    ds.StudyInstanceUID = STUDY_UID
    ds.SeriesInstanceUID = SERIES_UID
    ds.SOPInstanceUID = SOP_UID
    ds.SOPClassUID = SecondaryCaptureImageStorage

    ds.Modality = "OT"
    ds.StudyDescription = "SIMULACION QUIRURGICA MAKO"
    ds.SeriesDescription = descripcion
    ds.BodyPartExamined = "KNEE"

    ds.StudyDate = FECHA.strftime("%Y%m%d")
    ds.StudyTime = FECHA.strftime("%H%M%S")
    ds.SeriesNumber = 1 if descripcion == "CAMARA DOCTOR" else 2
    ds.InstanceNumber = 1

    ds.Manufacturer = "MAKO PACS SIMULATOR"
    ds.ManufacturerModelName = "CoppeliaSim"
    ds.ConversionType = "WSD"
    ds.ImageType = ["DERIVED", "SECONDARY"]

    # Caracteristicas de la imagen
    ds.SamplesPerPixel = 3
    ds.PhotometricInterpretation = "RGB"
    ds.PlanarConfiguration = 0
    ds.Rows = alto
    ds.Columns = ancho
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_data

    ds.save_as(ruta_salida, write_like_original=False)

    print("DICOM generado:", ruta_salida)


# =====================================
# CONVERTIR LAS DOS CAMARAS
# =====================================

if __name__ == "__main__":

    print("INICIANDO CONVERSION MAKO PACS")

    convertir(
        "doctor_20261107_223342.png",
        "CAMARA DOCTOR"
    )

    convertir(
        "mako_20261107_223342.png",
        "CAMARA MAKO"
    )

    print("--------------------------------")
    print("CONVERSION COMPLETADA")
    print("Archivos guardados en datos_dicom")
    print("--------------------------------")
