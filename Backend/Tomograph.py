from math import radians
import numpy as np
from matplotlib import pyplot as plt
from skimage import exposure
from skimage.draw import line
from Backend.Converter import Converter
from Backend.Filter import Filter
from Backend.Utils import Utils

class Tomograph:
    def __init__(self):
        self.converter = Converter()
        self.utils = Utils()
        self.filter = Filter()
        self.kernel = self.filter.createFilter(21) # Tworzymy filtr (rozmiar 21)

    # Obliczanie pozycji emiterów i detektorów dla danego kąta obrotu tomografu
    # Emitery i detektory są symetryczne względem środka obrazu i obejmują zadany kąt angularSpread
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

        # Generowanie punktów dla emiterów i detektorów – detektory są naprzeciwko emiterów, model równoległy
        # Użycie radians(...) pozwala pracować w układzie biegunowym
        return (calculatePoints(radians(angle - angularSpread / 2), numberOfEmittersAndDetectors, radians(angularSpread), radiusX, radiusY, center),
            calculatePoints(radians(angle - angularSpread / 2 + 180), numberOfEmittersAndDetectors, radians(angularSpread), radiusX, radiusY, center)[::-1])

    # Zwracanie wszystkich pikseli na linii między dwoma punktami
    # (na podobieństwo algorytmu Bresenhama)
    # W naszym scenariuszu badamy pary emiter-detektor
    def bresenham(self, x1, y1, x2, y2) -> np.ndarray:
        rr, cc = line(y1, x1, y2, x2)
        return np.array([rr, cc])

    # Tworzenie sinogram z obrazu wejściowego przez obliczenie sum pikseli dla każdej pary emiter-detektor
    def createSinogram(self, imageArray: np.ndarray, alpha, numberOfEmittersAndDetectors: int,
                       angularSpread: int, center: tuple, radiusX: int,radiusY: int, filter: bool) -> tuple:
        sinogram = np.zeros((int(360 // alpha), numberOfEmittersAndDetectors)) # Inicjalizacja sinogramu

        linePointsDict = dict() # Słownik do przechowywania wszystkich linii dla późniejszej rekonstrukcji

        angles = np.linspace(0, 360, int(360 // alpha))

        for idx, angle in enumerate(angles):
            emitters, detectors = self.getEmitterAndDetectorPoints(angle, numberOfEmittersAndDetectors, angularSpread, radiusX, radiusY, center)

            for i in range(numberOfEmittersAndDetectors):
                emitter = emitters[i]
                detector = detectors[i]

                linePoints = self.bresenham(emitter[0], emitter[1], detector[0], detector[1])
                linePointsDict[(angle, i)] = linePoints

                # Sumujemy intensywność pikseli wzdłuż każdej linii
                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < imageArray.shape[0] and 0 <= y < imageArray.shape[1]:
                        sinogram[idx, i] += imageArray[x, y]

        # Jeśli wybrano filtrację, stosujemy ją
        if filter:
            sinogram = self.filter.filterSinogram(sinogram, self.kernel)

        return linePointsDict, sinogram

    # Tworzenie rekonstrukcji obrazu
    # Dla każdego rzędu sinogramu (kąta) symuluje odwrotny rzut
    # Odtwarza promień przez obraz i dodaje wartość z sinogramu wzdłuż linii
    # Sumowanie wszystkich takich rzutów daje końcową rekonstrukcję
    def createReconstruction(self, sinogram: np.ndarray, alpha, numberOfEmittersAndDetectors: int, radiusX: int, radiusY: int,
                             linePointsDict: dict, testing=False):

        imageSize = (radiusY * 2, radiusX * 2) # Rozmiar obrazu
        reconstructedImage = np.zeros(imageSize)
        reconstructedImages = dict()

        angles = np.linspace(0, 360, int(360 // alpha))
        # Rozwiązanie czysto wizualne dla poprawy nasycenia
        if len(angles) <= 2:
            percentiles = (30, 90)
        else:
            percentiles = (40, 80)

        for idx, angle in enumerate(angles):

            for i in range(numberOfEmittersAndDetectors):
                linePoints = linePointsDict[(angle, i)]

                # Nakładamy wartość z sinogramu na piksele leżące na linii
                for j in range(linePoints.shape[1]):
                    x, y = linePoints[:, j]

                    if 0 <= x < imageSize[0] and 0 <= y < imageSize[1]:
                        reconstructedImage[x, y] += sinogram[idx, i]

            # Normalizacja do zakresu 0-255
            reconstructedImageNormalized = 255 * (reconstructedImage - np.min(reconstructedImage)) / (
                        np.max(reconstructedImage) - np.min(reconstructedImage))
            # Przeskalowanie nasycenia obrazu
            low, high = np.percentile(reconstructedImageNormalized, percentiles)
            reconstructedImageNormalized = exposure.rescale_intensity(reconstructedImageNormalized,
                                                                      in_range=(low, high))
            if not testing:
                reconstructedImages[idx + 1] = reconstructedImageNormalized

        # Wyłącznie do testów
        # Zwrócenie tylko jednego obrazu, a nie każdej iteracji
        if testing:
            return reconstructedImageNormalized

        return reconstructedImages

    def displayImagesMatPlotLib(self, sinogram, reconstructedImages) -> None:
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

    # Packaging kolejnych wersji sinogramów i obrazów dla interaktywnego przeglądania
    def packageImages(self, sinogram: np.ndarray, reconstructedImages: dict):
        maxIter = sinogram.shape[0]
        dominantColor = np.median(sinogram)

        sinograms = dict()
        sinograms[maxIter] = sinogram
        for i in range(1, maxIter ):
            sinogramDisplay = np.full_like(sinogram, dominantColor)
            sinogramDisplay[-i:, :] = sinogram[-i:, :]
            sinograms[i] = sinogramDisplay

        return sinograms, reconstructedImages, maxIter

    # Główna metoda uruchamiająca cały pipeline tomografii: wczytanie, projekcja, rekonstrukcja
    def run(self, imageURL: str, alpha, numberOfEmittersAndDetectors: int, angularSpread: int, filterSinogram: bool,
            imageArray=None) -> tuple:

        # Dopuszczalne jest przekazanie do metody od razu gotowej macierzy obrazu
        if imageArray is None:
            imageArray = self.converter.JPGtoMatrix(imageURL)

        center = self.utils.getCenterOfImage(imageArray)
        radiusY, radiusX = self.utils.getRadiusOfImage(imageArray)

        linePointsDict, sinogram = self.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, filterSinogram)

        reconstructedImages = self.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, radiusX, radiusY, linePointsDict)

        sinogram, reconstructedImages, maxIter = self.packageImages(sinogram, reconstructedImages)

        return sinogram, reconstructedImages
