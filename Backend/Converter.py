import numpy as np
from PIL import Image

class Converter:
    def JPGtoMatrix(self, filePath: str) -> np.ndarray:
        return np.array(Image.open(filePath).convert('L'))

    #TODO implement this method
    def DICOMtoMatrix(self, filePath: str) -> list:
        DicomData = dict()
        pass

