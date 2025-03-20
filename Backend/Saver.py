import numpy as np
from PIL import Image
from pydicom import dcmread


class Saver:
    def saveMatrixAsJPG(self, matrix: np.ndarray, filePath: str) -> None:
        Image.fromarray(matrix).save(filePath)

    #TODO: Implement this method
    def saveAsDicomFile(self, path, image, meta, dicomParams):
        dicom = dcmread(path)

        for key in meta:
            setattr(dicom, key, meta[key])

        dicom.PixelData = image.tobytes()

        dicom.save_as(path)
