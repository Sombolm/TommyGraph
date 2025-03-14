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

    #TODO fix sinograms and reconstructed images
    def createSinogram(self, imageArray: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int,
                       angularSpread: int, center: tuple, radius: int):
        sinogram = np.zeros((360 // alpha, numberOfEmittersAndDetectors))

        sinograms = dict()
        linePointsDict = dict()

        for angle in range(0, 360, alpha):
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
            if angle == 0:
                angle = 1

            sinograms[360 // angle] = sinogram


        return sinogram, linePointsDict, sinograms

    def createReconstruction(self, sinogram: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int, radius: int,
                             linePointsDict: dict):

        filteredSinogram = sinogram

        image_size = (radius * 2, radius * 2)
        reconstructedImage = np.zeros(image_size)
        reconstructedImages = dict()

        for angle in range(0, 360, alpha):

            for i in range(numberOfEmittersAndDetectors):
                linePoints = linePointsDict[(angle, i)]

                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < image_size[0] and 0 <= y < image_size[1]:
                        reconstructedImage[x, y] += filteredSinogram[angle // alpha, i]

            if angle == 0:
                angle = 1
            reconstructedImages[360 // angle] = reconstructedImage / np.max(reconstructedImage) * 255

        reconstructedImage = reconstructedImage / np.max(reconstructedImage) * 255

        return reconstructedImage, reconstructedImages

    def displayImagesMatPlotLib(self):
        pass

    def run(self, imageURL: str,alpha: int, numberOfEmittersAndDetectors: int, angularSpread: int, filterSinogram: bool):
        imageArray = self.converter.JPGtoMatrix(imageURL)
        center = self.utils.getCenterOfImage(imageArray)
        radius = self.utils.getRadiusOfImage(imageArray)

        paddedImage, newCenter, newRadius = self.utils.padImageForCircle(imageArray, center, radius)

        sinogram, linePointsDict, sinograms = self.createSinogram(paddedImage, alpha, numberOfEmittersAndDetectors, angularSpread, newCenter, newRadius)
        reconstructedImage, reconstructedImages = self.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, newRadius, linePointsDict)

        plt.imshow(sinogram, cmap='gray')
        plt.show()
        plt.imshow(reconstructedImage, cmap='gray')
        plt.show()

        for key in sinograms.keys():
            plt.imshow(sinograms[key], cmap='gray')
            plt.show()
            plt.imshow(reconstructedImages[key], cmap='gray')
            plt.show()




