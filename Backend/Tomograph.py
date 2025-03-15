from math import radians
import numpy as np
from matplotlib import pyplot as plt
from skimage.draw import line

from Backend.Converter import Converter
from Backend.Filter import Filter
from Backend.Saver import Saver
from Backend.Utils import Utils


class Tomograph:
    def __init__(self):
        self.converter = Converter()
        self.utils = Utils()
        self.Fiter = Filter()
        self.Saver = Saver()

    def getEmitterAndDetectorPoints(self, angle: int, numberOfEmittersAndDetectors: int, angularSpread: int, radius: int, center: tuple):
        def calculatePoints(angle: float, numberOfEmittersAndDetectors: int, angularSpread: float, radius: int, center: tuple):
            points = []
            angle_step = angularSpread / (numberOfEmittersAndDetectors - 1) if numberOfEmittersAndDetectors > 1 else 0

            for i in range(numberOfEmittersAndDetectors):
                current_angle = angle + angle_step * i
                x = int(radius * np.cos(current_angle) + center[0])
                y = int(radius * np.sin(current_angle) + center[1])
                points.append((x, y))

            return np.array(points)

        return (calculatePoints(radians(angle - angularSpread / 2), numberOfEmittersAndDetectors, radians(angularSpread), radius, center),
            calculatePoints(radians(angle - angularSpread / 2 + 180), numberOfEmittersAndDetectors, radians(angularSpread), radius, center)[::-1])


    def bresenham(self, x1, y1, x2, y2) -> np.ndarray:
        rr, cc = line(y1, x1, y2, x2)
        return np.array([rr, cc])


    def createSinogram(self, imageArray: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int,
                       angularSpread: int, center: tuple, radius: int) -> tuple:
        sinogram = np.zeros((360 // alpha, numberOfEmittersAndDetectors))

        sinograms = dict()
        linePointsDict = dict()

        for idx,angle in enumerate(range(0, 360, alpha)):
            emitters, detectors = self.getEmitterAndDetectorPoints(angle, numberOfEmittersAndDetectors, angularSpread, radius, center)

            for i in range(numberOfEmittersAndDetectors):
                emitter = emitters[i]
                detector = detectors[i]

                linePoints = self.bresenham(emitter[0], emitter[1], detector[0], detector[1])
                linePointsDict[(angle, i)] = linePoints
                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < imageArray.shape[0] and 0 <= y < imageArray.shape[1]:
                        sinogram[angle // alpha, i] += imageArray[x, y]

            sinograms[idx + 1] = sinogram.copy()

        return linePointsDict, sinograms

    def createReconstruction(self, sinogram: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int, radius: int,
                             linePointsDict: dict) -> dict:

        filteredSinogram = sinogram

        image_size = (radius * 2, radius * 2)
        reconstructedImage = np.zeros(image_size)
        reconstructedImages = dict()

        for idx, angle in enumerate(range(0, 360, alpha)):

            for i in range(numberOfEmittersAndDetectors):
                linePoints = linePointsDict[(angle, i)]

                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < image_size[0] and 0 <= y < image_size[1]:
                        reconstructedImage[x, y] += filteredSinogram[angle // alpha, i]

            reconstructedImages[idx + 1] = reconstructedImage / np.max(reconstructedImage) * 255

        return reconstructedImages

    def displayImagesMatPlotLib(self,sinograms, reconstructedImages) -> None:

        plt.imshow(sinograms[max(sinograms.keys())], cmap='gray')
        plt.show()
        plt.imshow(reconstructedImages[max(sinograms.keys())], cmap='gray')
        plt.show()

        plt.imshow(sinograms[max(sinograms.keys()) // 2], cmap='gray')
        plt.show()
        plt.imshow(reconstructedImages[max(sinograms.keys()) // 2], cmap='gray')
        plt.show()

    #TODO implement filtering
    def run(self, imageURL: str,alpha: int, numberOfEmittersAndDetectors: int, angularSpread: int, filterSinogram: bool) -> tuple:
        imageArray = self.converter.JPGtoMatrix(imageURL)
        center = self.utils.getCenterOfImage(imageArray)
        radius = self.utils.getRadiusOfImage(imageArray)

        paddedImage, newCenter, newRadius = self.utils.padImageForCircle(imageArray, center, radius)

        linePointsDict, sinograms = self.createSinogram(paddedImage, alpha, numberOfEmittersAndDetectors, angularSpread, newCenter, newRadius)

        reconstructedImages = self.createReconstruction(sinograms[max(sinograms.keys())], alpha, numberOfEmittersAndDetectors, newRadius, linePointsDict)

        self.displayImagesMatPlotLib(sinograms, reconstructedImages)

        return sinograms, reconstructedImages



