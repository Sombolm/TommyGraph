from Backend.Tomograph import Tomograph
from Backend.Utils import Utils


class Tester:
    def __init__(self):
        self.tomograph = Tomograph()
        self.utils = Utils()

    def testMSEForIterations(self, imageArray, alpha, numberOfEmittersAndDetectors, angularSpread,center, radiusX, radiusY, filterSinogram = False):

        linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors, angularSpread,
                                                       center, radiusX, radiusY, filterSinogram)

        reconstructedImages = self.tomograph.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, radiusX, radiusY,
                                                        linePointsDict)

        for i in range(1, len(reconstructedImages)):
            mse = self.utils.calculateMSE(imageArray, reconstructedImages[i])
            rmse = self.utils.calculateRMSE(imageArray, reconstructedImages[i])
            print("MSE for iteration " + str(i) + ": " + str(mse))
            print("RMSE for iteration " + str(i) + ": " + str(rmse))

        return reconstructedImages[len(reconstructedImages)]

    def testIncreasingAccuracy(self, imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, filterSinogram = False):


        numberOfEmittersAndDetectorsRange = list(range(90, 720, 90))
        numberOfScansRange = list(range(90, 720, 90))
        alphas = [int(360 // i) for i in numberOfScansRange]
        angularSpreadRange = list(range(45, 270, 45))
        testing = True

        print("Running test for increasing accuracy")
        print("Increasing number of emitters and detectors")

        for numberOfEmittersAndDetectorsIter in numberOfEmittersAndDetectorsRange:
            linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alpha, numberOfEmittersAndDetectorsIter, angularSpread,
                                                           center, radiusX, radiusY, filterSinogram)

            reconstructedImages = self.tomograph.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectorsIter, radiusX, radiusY,
                                                            linePointsDict, testing)

            mse = self.utils.calculateMSE(imageArray, reconstructedImages)
            rmse = self.utils.calculateRMSE(imageArray, reconstructedImages)
            print("Testing for number of emitters and detectors " + str(numberOfEmittersAndDetectors))
            print("MSE for number of emitters and detectors " + str(numberOfEmittersAndDetectors) + ": " + str(mse))
            print("RMSE for number of emitters and detectors " + str(numberOfEmittersAndDetectors) + ": " + str(rmse))


        print("Increasing number of scans")
        for alphaIter in alphas:
            linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alphaIter, numberOfEmittersAndDetectors, angularSpread,
                                                           center, radiusX, radiusY, filterSinogram)

            reconstructedImages = self.tomograph.createReconstruction(sinogram, alphaIter, numberOfEmittersAndDetectors, radiusX, radiusY,
                                                            linePointsDict, testing)

            mse = self.utils.calculateMSE(imageArray, reconstructedImages)
            rmse = self.utils.calculateRMSE(imageArray, reconstructedImages)
            print("Testing for alpha " + str(alphaIter))
            print("MSE for alpha " + str(alphaIter) + ": " + str(mse))
            print("RMSE for alpha " + str(alphaIter) + ": " + str(rmse))

        print("Increasing angular spread")
        for angularSpreadIter in angularSpreadRange:
            linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors, angularSpreadIter,
                                                           center, radiusX, radiusY, filterSinogram)

            reconstructedImages = self.tomograph.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors, radiusX, radiusY,
                                                            linePointsDict, testing)

            mse = self.utils.calculateMSE(imageArray, reconstructedImages)
            rmse = self.utils.calculateRMSE(imageArray, reconstructedImages)
            print("Testing for angular spread " + str(angularSpreadIter))
            print("MSE for angular spread " + str(angularSpreadIter) + ": " + str(mse))
            print("RMSE for angular spread " + str(angularSpreadIter) + ": " + str(rmse))

    def testFiltering(self, imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, filterSinogram):
        #Filtered
        linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors,
                                                                 angularSpread,
                                                                 center, radiusX, radiusY, True)

        reconstructedImagesFiltered = self.tomograph.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors,
                                                                  radiusX, radiusY,
                                                                  linePointsDict, True)

        #Unfiltered
        linePointsDict, sinogram = self.tomograph.createSinogram(imageArray, alpha, numberOfEmittersAndDetectors,
                                                                 angularSpread,
                                                                 center, radiusX, radiusY, False)

        reconstructedImagesUnfiltered = self.tomograph.createReconstruction(sinogram, alpha, numberOfEmittersAndDetectors,
                                                                  radiusX, radiusY,
                                                                  linePointsDict, True)

        mse = self.utils.calculateMSE(reconstructedImagesUnfiltered[len(reconstructedImagesUnfiltered)], reconstructedImagesFiltered[len(reconstructedImagesFiltered)])
        rmse = self.utils.calculateRMSE(reconstructedImagesUnfiltered[len(reconstructedImagesUnfiltered)], reconstructedImagesFiltered[len(reconstructedImagesFiltered)])
        print("MSE: " + str(mse))
        print("RMSE: " + str(rmse))

    def runTests(self, imageURL, alpha, numberOfEmittersAndDetectors, angularSpread, filterSinogram = False):


        imageArray = self.converter.JPGtoMatrix(imageURL)
        center = self.utils.getCenterOfImage(imageArray)
        radiusY, radiusX = self.utils.getRadiusOfImage(imageArray)

        print("Running tests for image: " + imageURL)

        print("Running test 1")
        #test1
        self.testMSEForIterations(imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, filterSinogram)

        print("Running test 2")
        #test2
        self.testFiltering(imageArray, 1, 360, 270, center, radiusX, radiusY, False)

        print("Running test 3")
        #test3
        self.testFiltering(imageArray, alpha, numberOfEmittersAndDetectors, angularSpread, center, radiusX, radiusY, True)



    pass

if __name__ == '__main__':
    imageURL = "../ExampleDICOM/Kropka.dcm"
    alpha = 2
    numberOfEmittersAndDetectors = 180
    angularSpread = 180

    tester = Tester()
    tester.runTests(imageURL, alpha, numberOfEmittersAndDetectors, angularSpread)