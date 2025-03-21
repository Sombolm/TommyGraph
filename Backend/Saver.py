import datetime

import numpy as np
import pydicom
from PIL import Image
from matplotlib.testing.compare import converter
from pydicom import Dataset, FileDataset, FileMetaDataset
from pydicom.dataset import validate_file_meta
from pydicom.uid import generate_uid, CTImageStorage
from pydicom.util.leanread import ExplicitVRLittleEndian

from Backend.Converter import Converter


class Saver:

    def saveMatrixAsJPG(self, matrix: np.ndarray, filePath: str) -> None:
        matrix = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255
        matrix = matrix.astype(np.uint8)
        Image.fromarray(matrix).save(filePath)

    def saveAsDicomFile(self,path, image, dicomParams):

        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian


        ds = FileDataset(path, {}, file_meta=meta, preamble=b'\0' * 128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        ds.SOPClassUID = CTImageStorage
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID

        ds.Modality = "CT"
        ds.SeriesInstanceUID = generate_uid()
        ds.StudyInstanceUID = generate_uid()
        ds.FrameOfReferenceUID = generate_uid()

        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.SamplesPerPixel = 1
        ds.HighBit = 15

        ds.ImagesInAcquisition = 1
        ds.InstanceNumber = 1

        ds.Rows, ds.Columns = image.shape

        ds.ImagePositionPatient = [0.0, 0.0, 1.0]
        ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, -1.0, 0.0]

        ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]

        ds.RescaleIntercept = 0
        ds.RescaleSlope = 1.0
        ds.PixelSpacing = [1.0, 1.0]
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.PixelRepresentation = 1

        for key, value in dicomParams.items():
            setattr(ds, key, value)

        validate_file_meta(ds.file_meta, enforce_standard=True)

        ds.PixelData = image.astype(np.uint16).tobytes()

        ds.save_as(path)
'''
saver = Saver()
converter = Converter()
img, meta = converter.readDicomFile("../ExampleDICOM/Kropka.dcm")
#img = converter.convertImageToUbyte(img)

saver.saveAsDicomFile("../ExampleImages/Kropka2.dcm", img, dict(
    PatientName='Test',
    PatientID='001',
    ImageComments='Comment',
    StudyDate='20250321',
))

image, meta = converter.readDicomFile("../ExampleImages/Kropka2.dcm")

print(meta)'''