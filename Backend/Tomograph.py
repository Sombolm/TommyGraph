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

    #TODO reuse emitters, detectors, linePoints
    def createSinogram(self, imageArray: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int, angularSpread: int, center: tuple, radius: int):
        sinogram = np.zeros((360 // alpha, numberOfEmittersAndDetectors))
        #sinograms = []
        for angle in range(0, 360, alpha):
            emitters, detectors = self.getEmitterAndDetectorPoints(angle, numberOfEmittersAndDetectors, angularSpread, radius, center)

            for i in range(numberOfEmittersAndDetectors):
                emitter = emitters[i]
                detector = detectors[i]

                linePoints = self.bresenham(emitter[0], emitter[1], detector[0], detector[1])
                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < imageArray.shape[0] and 0 <= y < imageArray.shape[1]:
                        sinogram[angle // alpha, i] += imageArray[x, y]

            #sinograms.append(sinogram)

        return sinogram, emitters, detectors, linePoints

    def createReconstruction(self, sinogram: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int,
                             angularSpread: int, center: tuple, radius: int, emitters: np.ndarray,
                             detectors: np.ndarray, linePoints: np.ndarray) -> np.ndarray:

        filtered_sinogram = sinogram

        image_size = (radius * 2, radius * 2)
        reconstructed_image = np.zeros(image_size)

        for angle in range(0, 360, alpha):
            emitters, detectors = self.getEmitterAndDetectorPoints(angle, numberOfEmittersAndDetectors, angularSpread,
                                                                   radius, center)

            for i in range(numberOfEmittersAndDetectors):
                emitter = emitters[i]
                detector = detectors[i]

                line_points = self.bresenham(emitter[0], emitter[1], detector[0], detector[1])

                for j in range(line_points.shape[1]):
                    x, y = line_points[:, j]

                    if 0 <= x < image_size[0] and 0 <= y < image_size[1]:
                        reconstructed_image[x, y] += filtered_sinogram[angle // alpha, i]

        reconstructed_image = reconstructed_image / np.max(reconstructed_image) * 255

        return reconstructed_image

    def displayImagesMatPlotLib(self):
        pass

    def run(self, imageURL: str,alpha: int, numberOfEmittersAndDetectors: int, angularSpread: int, filterSinogram: bool):
        imageArray = self.converter.JPGtoMatrix(imageURL)
        center = self.utils.getCenterOfImage(imageArray)
        radius = self.utils.getRadiusOfImage(imageArray)

        paddedImage, newCenter, newRadius = self.utils.padImageForCircle(imageArray, center, radius)

        sinogram, emitters, detectors, linePoints = self.createSinogram(paddedImage, alpha, numberOfEmittersAndDetectors, angularSpread, newCenter, newRadius)
        reconstructedImage = self.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, angularSpread,
                                                       newCenter, newRadius, emitters, detectors, linePoints)

        plt.imshow(sinogram, cmap='gray')
        plt.show()
        plt.imshow(reconstructedImage, cmap='gray')
        plt.show()



