import numpy as np
from PIL import Image
from pydicom import dcmread
from skimage.exposure import rescale_intensity
from skimage.util import img_as_ubyte


class Converter:
    def JPGtoMatrix(self, filePath: str) -> np.ndarray:
        return np.array(Image.open(filePath).convert('L'))

    def readDicomFile(self, path):
        dicom = dcmread(path)

        keys = dicom.dir()
        meta = {x: getattr(dicom, x) for x in keys}

        image = dicom.pixel_array

        return image, meta

    def convertImageToUbyte(self, img):
        return img_as_ubyte(rescale_intensity(img, out_range=(0.0, 1.0)))