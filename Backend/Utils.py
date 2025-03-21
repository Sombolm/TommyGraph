import numpy as np
from matplotlib import pyplot as plt


class Utils:
    def getCenterOfImage(self,array):
        return np.floor(np.array(array.shape) / 2).astype(int)

    def getRadiusOfImage(self, array):
        return np.shape(array)[0] // 2, np.shape(array)[1] // 2

    def padImageToSquare(self, imageArray: np.ndarray):
        paddedImage = np.zeros((max(imageArray.shape), max(imageArray.shape)))
        paddedImage[:imageArray.shape[0], :imageArray.shape[1]] = imageArray

        #plot the padded image
        plt.imshow(paddedImage, cmap='gray')
        plt.show()
        return paddedImage

    def padImageForCircle(self, imageArray: np.ndarray, center: tuple, radius: int):
        paddedImage = np.zeros((imageArray.shape[0] + 2 * radius, imageArray.shape[1] + 2 * radius))
        paddedImage[radius:-radius, radius:-radius] = imageArray

        newCenter = (center[0] + radius, center[1] + radius)
        newRadius = self.getRadiusOfImage(paddedImage)
        return paddedImage, newCenter, newRadius

    def calculateMSE(self, originalImage, reconstructedImage):
        return np.square(np.subtract(originalImage, reconstructedImage)).mean()

    def calculateRMSE(self, originalImage, reconstructedImage):
        return np.sqrt(self.calculateMSE(originalImage, reconstructedImage))