import numpy as np
from PIL import Image

class Converter:
    def JPGtoMatrix(self, filePath: str) -> np.ndarray:
        return np.array(Image.open(filePath).convert('L'))


