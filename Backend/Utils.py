import numpy as np
from matplotlib import pyplot as plt


class Utils:
    def getCenterOfImage(self,array):
        return np.floor(np.array(array.shape) / 2).astype(int)

    def getRadiusOfImage(self, array):
        return np.min(array.shape) // 2

    def padImageForCircle(self, imageArray: np.ndarray, center: tuple, radius: int):
        paddedImage = np.zeros((imageArray.shape[0] + 2 * radius, imageArray.shape[1] + 2 * radius))
        paddedImage[radius:-radius, radius:-radius] = imageArray

        newCenter = (center[0] + radius, center[1] + radius)
        newRadius = self.getRadiusOfImage(paddedImage)
        return paddedImage, newCenter, newRadius