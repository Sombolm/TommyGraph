import numpy as np
from numpy import clip
from scipy.fftpack import fft, ifft, fftfreq

class Filter:

    def createFilter(self,size=21):
        k = np.arange(-size // 2, size // 2 + 1)
        kernel = np.zeros_like(k, dtype=np.float32)

        kernel[k == 0] = 1
        oddK = k[k % 2 != 0]
        kernel[k % 2 != 0] = -4 / (np.pi ** 2 * oddK ** 2)
        return kernel

    def filterSinogram(self, sinogram: np.ndarray, kernel) -> np.ndarray:
        for i in range(sinogram.shape[0]):
            sinogram[i, :] = np.convolve(sinogram[i, :], kernel, mode='same')
        #sinogram = clip(np.real(sinogram), 0, 1)
        return sinogram