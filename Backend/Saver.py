import numpy as np
from PIL import Image

class Saver:
    def SaveMatrixAsJPG(self, matrix: np.ndarray, filePath: str) -> None:
        Image.fromarray(matrix).save(filePath)

    #TODO: Implement this method
    def SaveMatrixAsDICOM(self, name: str, matrix: np.ndarray, patientData: dict) -> None:
        pass
