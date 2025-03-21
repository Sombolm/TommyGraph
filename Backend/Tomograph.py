from math import radians

import numpy as np
from matplotlib import pyplot as plt
from numpy import ndarray
from skimage.draw import line

from Backend.Converter import Converter
from Backend.Filter import Filter
from Backend.Saver import Saver
from Backend.Utils import Utils

class Tomograph:
    def __init__(self):
        self.converter = Converter()
        self.utils = Utils()
        self.filter = Filter()
        self.saver = Saver()
        self.kernel = self.filter.createFilter(21)

    def getEmitterAndDetectorPoints(self, angle: int, numberOfEmittersAndDetectors: int, angularSpread: int, radiusX: int, radiusY, center: tuple):
        def calculatePoints(angle: float, numberOfEmittersAndDetectors: int, angularSpread: float, radiusX: int, radiusY: int ,center: tuple):
            points = []
            angle_step = angularSpread / (numberOfEmittersAndDetectors - 1) if numberOfEmittersAndDetectors > 1 else 0

            for i in range(numberOfEmittersAndDetectors):
                current_angle = angle + angle_step * i
                x = int(radiusX * np.cos(current_angle) + center[1])
                y = int(radiusY * np.sin(current_angle) + center[0])
                points.append((x, y))

            return np.array(points)

        return (calculatePoints(radians(angle - angularSpread / 2), numberOfEmittersAndDetectors, radians(angularSpread), radiusX, radiusY, center),
            calculatePoints(radians(angle - angularSpread / 2 + 180), numberOfEmittersAndDetectors, radians(angularSpread), radiusX, radiusY, center)[::-1])


    def bresenham(self, x1, y1, x2, y2) -> np.ndarray:
        rr, cc = line(y1, x1, y2, x2)
        return np.array([rr, cc])


    def createSinogram(self, imageArray: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int,
                       angularSpread: int, center: tuple, radiusX: int,radiusY: int, filter: bool) -> tuple:
        sinogram = np.zeros((360 // alpha, numberOfEmittersAndDetectors))

        linePointsDict = dict()

        for idx,angle in enumerate(range(0, 360, alpha)):
            emitters, detectors = self.getEmitterAndDetectorPoints(angle, numberOfEmittersAndDetectors, angularSpread, radiusX, radiusY, center)

            for i in range(numberOfEmittersAndDetectors):
                emitter = emitters[i]
                detector = detectors[i]

                linePoints = self.bresenham(emitter[0], emitter[1], detector[0], detector[1])
                linePointsDict[(angle, i)] = linePoints
                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < imageArray.shape[0] and 0 <= y < imageArray.shape[1]:
                        sinogram[angle // alpha, i] += imageArray[x, y]

        if filter:
            sinogram = self.filter.filterSinogram(sinogram, self.kernel)


            #plt.imshow(sinogram, cmap='gray')
            #plt.show()


        return linePointsDict, sinogram

    def createReconstruction(self, sinogram: np.ndarray, alpha: int, numberOfEmittersAndDetectors: int, radiusX: int, radiusY: int,
                             linePointsDict: dict) -> dict:

        image_size = (radiusY * 2, radiusX * 2)
        reconstructedImage = np.zeros(image_size)
        reconstructedImages = dict()

        for idx, angle in enumerate(range(0, 360, alpha)):

            for i in range(numberOfEmittersAndDetectors):
                linePoints = linePointsDict[(angle, i)]

                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < image_size[0] and 0 <= y < image_size[1]:
                        reconstructedImage[x, y] += sinogram[angle // alpha, i]

            reconstructedImageNormalized = 255 * (reconstructedImage - np.min(reconstructedImage)) / (
                        np.max(reconstructedImage) - np.min(reconstructedImage))

            reconstructedImages[idx + 1] = reconstructedImageNormalized

        return reconstructedImages

    def displayImagesMatPlotLib(self,sinogram, reconstructedImages) -> None:
        maxIter = sinogram.shape[0]

        plt.imshow(sinogram, cmap='gray')
        plt.title('Sinogram')
        plt.show()

        plt.imshow(reconstructedImages[maxIter], cmap='gray')
        plt.title('Reconstructed Image')
        plt.show()

        dominantColor = np.mean(sinogram)

        for i in range(1, maxIter + 1):
            sinogramDisplay = np.full_like(sinogram, dominantColor)
            sinogramDisplay[-i:, :] = sinogram[-i:, :]

            plt.imshow(sinogramDisplay, cmap='gray')
            plt.title(f'Sinogram {i}')
            plt.show()

            plt.imshow(reconstructedImages[i], cmap='gray')
            plt.title(f'Reconstructed Image {i}')
            plt.show()

    def packageImages(self, sinogram: np.ndarray, reconstructedImages: dict):
        maxIter = sinogram.shape[0]
        dominantColor = np.median(sinogram)

        sinograms = dict()
        sinograms[maxIter] = sinogram
        for i in range(1, maxIter ):
            sinogramDisplay = np.full_like(sinogram, dominantColor)
            sinogramDisplay[-i:, :] = sinogram[-i:, :]
            sinograms[i] = sinogramDisplay


        plt.imshow(sinograms[maxIter], cmap='gray')
        plt.title('Sinogram')
        plt.show()

        plt.imshow(reconstructedImages[maxIter], cmap='gray')
        plt.title('Reconstructed Image')
        plt.show()

        return sinograms, reconstructedImages, maxIter
    #TODO: DICOM
    def run(self, imageURL: str,alpha: int, numberOfEmittersAndDetectors: int, angularSpread: int, filterSinogram: bool,
            imageArray, saveAsDicom: bool, dicomParams: dict, savePath: str) -> tuple:

        if imageArray is None:
            imageArray = self.converter.JPGtoMatrix(imageURL)


        center = self.utils.getCenterOfImage(imageArray)
        radiusY, radiusX = self.utils.getRadiusOfImage(imageArray)

        #paddedImage, newCenter, newRadius = self.utils.padImageForCircle(imageArray, center, radius)


        linePointsDict, sinogram = self.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, filterSinogram)

        reconstructedImages = self.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, radiusX, radiusY, linePointsDict)

        #self.displayImagesMatPlotLib(sinogram, reconstructedImages)
        sinogram, reconstructedImages, maxIter = self.packageImages(sinogram, reconstructedImages)

        if saveAsDicom:
            self.saver.saveAsDicomFile(savePath, reconstructedImages[maxIter], dicomParams)
        else:
            self.saver.saveMatrixAsJPG(reconstructedImages[maxIter], savePath)

        return sinogram, reconstructedImages

    def viewDicom(self, path: str):
        img, meta = self.converter.readDicomFile(path)
        return img, meta

    def test(self):
        pass

    def runTest(self):
        pass

