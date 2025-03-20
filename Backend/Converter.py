import numpy as np
from PIL import Image
from pydicom import dcmread


class Converter:
    def JPGtoMatrix(self, filePath: str) -> np.ndarray:
        return np.array(Image.open(filePath).convert('L'))

    def readDicomFile(self, path):
        dicom = dcmread(path)

        keys = dicom.dir()
        meta = {x: getattr(dicom, x) for x in keys}

        image = dicom.pixel_array

        return image, meta

