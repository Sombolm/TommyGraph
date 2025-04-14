import numpy as np
from PIL import Image
from pydicom import FileDataset, FileMetaDataset
from pydicom.dataset import validate_file_meta
from pydicom.uid import generate_uid, CTImageStorage
from pydicom.util.leanread import ExplicitVRLittleEndian

class Saver:

    # Zapis wygenerowanej rekonstrukcji do formatu .jpg
    # Używane na etapach testowych
    def saveMatrixAsJPG(self, matrix: np.ndarray, filePath: str) -> None:
        matrix = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255
        matrix = matrix.astype(np.uint8)
        Image.fromarray(matrix).save(filePath)

    # Zapis wygenerowanej rekonstrukcji (image)
    # oraz zadanych metadanych (dicomParams) do formatu .dcm
    def saveAsDicomFile(self, path, image, dicomParams):

        # Tworzenie struktury metadanych nagłówka DICOM
        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian

        # Tworzenie głównego obiektu pliku DICOM
        ds = FileDataset(path, {}, file_meta=meta, preamble=b'\0' * 128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        # Podstawowe identyfikatory i metadane
        ds.SOPClassUID = CTImageStorage
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID

        # Dane medyczne identyfikujące serię badań
        ds.Modality = "CT"
        ds.SeriesInstanceUID = generate_uid()
        ds.StudyInstanceUID = generate_uid()
        ds.FrameOfReferenceUID = generate_uid()

        # Ustawienia obrazu — format 16-bitów
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.SamplesPerPixel = 1
        ds.HighBit = 15

        ds.ImagesInAcquisition = 1 # Tylko jeden obraz w zestawie
        ds.InstanceNumber = 1

        ds.Rows, ds.Columns = image.shape # Rozmiar obrazu

        # Pozycja i orientacja obrazu w przestrzeni (domyślne)
        ds.ImagePositionPatient = [0.0, 0.0, 1.0]
        ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, -1.0, 0.0]

        # Typ obrazu w DICOM
        ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]

        # Parametry skalowania wartości pikseli (domyślne)
        ds.RescaleIntercept = 0
        ds.RescaleSlope = 1.0
        ds.PixelSpacing = [1.0, 1.0]
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.PixelRepresentation = 1

        # Uzupełnienie pól z formularza w aplikacji, tj. dodatkowe dane pacjenta
        for key, value in dicomParams.items():
            setattr(ds, key, value)

        # Walidacja danych (zgodność ze standardem)
        validate_file_meta(ds.file_meta, enforce_standard=True)

        # Konwersja pikseli do 16-bitowej tablicy bajtów, przypisanie do pliku
        ds.PixelData = image.astype(np.uint16).tobytes()

        # Zapis pliku
        ds.save_as(path)