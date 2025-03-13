import numpy as np


class Utils:

    def center_of(array):
        return np.floor(np.array(array.shape) / 2).astype(int)