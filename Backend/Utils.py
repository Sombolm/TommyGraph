import numpy as np


class Utils:
    def getCenterOfImage(self,array):
        return np.floor(np.array(array.shape) / 2).astype(int)

    def getRadiusOfImage(self, array):
        return np.min(array.shape) // 2