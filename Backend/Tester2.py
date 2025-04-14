from Backend.Tomograph import Tomograph
from Backend.Utils import Utils
from Backend.Converter import Converter
from Backend.Saver import Saver
import matplotlib.pyplot as plt
import os

class Tester:
    def __init__(self):
        self.tomograph = Tomograph()
        self.utils = Utils()
        self.converter = Converter()
        self.saver = Saver()

    # Test wpływu liczby detektorów na RMSE
    def test_rmse_vs_detectors(self, image_array, alpha, angular_spread, center, radius_x, radius_y, filter_sinogram=False):
        detectors_range = range(90, 721, 90)
        rmse_values = []

        for det_count in detectors_range:
            lines, sinogram = self.tomograph.createSinogram(
                image_array, alpha, det_count, angular_spread, center, radius_x, radius_y, filter_sinogram
            )
            recon = self.tomograph.createReconstruction(sinogram, alpha, det_count, radius_x, radius_y, lines, testing=True)

            rmse = self.utils.calculateRMSE(image_array, recon)
            rmse_values.append(rmse)
            print(f"Detektory: {det_count}, RMSE: {rmse}")

            # Zapis rekonstrukcji do pliku JPG
            filename = f"output/recon_detectors_{det_count}.jpg"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.saver.saveMatrixAsJPG(recon, filename)

        plt.plot(list(detectors_range), rmse_values, marker='o')
        plt.title("RMSE vs Liczba Detektorów")
        plt.xlabel("Liczba Detektorów")
        plt.ylabel("RMSE")
        plt.grid(True)
        plt.savefig("output/recon_detectors_chart.png")

    # Test wpływu liczby skanów (kątów) na RMSE
    def test_rmse_vs_scans(self, image_array, number_of_detectors, angular_spread, center, radius_x, radius_y, filter_sinogram=False):
        scans_range = range(90, 721, 90)
        rmse_values = []

        for scan_count in scans_range:
            alpha = 360 / scan_count
            lines, sinogram = self.tomograph.createSinogram(
                image_array, alpha, number_of_detectors, angular_spread, center, radius_x, radius_y, filter_sinogram
            )
            recon = self.tomograph.createReconstruction(sinogram, alpha, number_of_detectors, radius_x, radius_y, lines, testing=True)

            rmse = self.utils.calculateRMSE(image_array, recon)
            rmse_values.append(rmse)
            print(f"Skanów: {scan_count}, RMSE: {rmse}")

            # Zapis rekonstrukcji do pliku JPG
            filename = f"output/recon_scans_{scan_count}.jpg"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.saver.saveMatrixAsJPG(recon, filename)

        plt.plot(list(scans_range), rmse_values, marker='o')
        plt.title("RMSE vs Liczba Skanów")
        plt.xlabel("Liczba Skanów")
        plt.ylabel("RMSE")
        plt.grid(True)
        plt.savefig("output/recon_detectors_chart.png")

    # Test wpływu rozpiętości wachlarza na RMSE
    def test_rmse_vs_angular_spread(self, image_array, alpha, number_of_detectors, center, radius_x, radius_y, filter_sinogram=False):
        spread_range = range(45, 271, 45)
        rmse_values = []

        for spread in spread_range:
            lines, sinogram = self.tomograph.createSinogram(
                image_array, alpha, number_of_detectors, spread, center, radius_x, radius_y, filter_sinogram
            )
            recon = self.tomograph.createReconstruction(sinogram, alpha, number_of_detectors, radius_x, radius_y, lines, testing=True)

            rmse = self.utils.calculateRMSE(image_array, recon)
            rmse_values.append(rmse)
            print(f"Wachlarz: {spread}, RMSE: {rmse}")

            # Zapis rekonstrukcji do pliku JPG
            filename = f"output/recon_spread_{spread}.jpg"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.saver.saveMatrixAsJPG(recon, filename)

        plt.plot(list(spread_range), rmse_values, marker='o')
        plt.title("RMSE vs Rozpiętość Wachlarza")
        plt.xlabel("Rozpiętość [stopnie]")
        plt.ylabel("RMSE")
        plt.grid(True)
        plt.savefig("output/recon_detectors_chart.png")

    def run_all_tests(self, image_url):
        image_array = self.converter.JPGtoMatrix(image_url)
        center = self.utils.getCenterOfImage(image_array)
        radius_y, radius_x = self.utils.getRadiusOfImage(image_array)

        alpha = 2  # odpowiada 180 skanom
        detectors = 180
        angular_spread = 180

        self.test_rmse_vs_detectors(image_array, alpha, angular_spread, center, radius_x, radius_y)
        self.test_rmse_vs_scans(image_array, detectors, angular_spread, center, radius_x, radius_y)
        self.test_rmse_vs_angular_spread(image_array, alpha, detectors, center, radius_x, radius_y)

if __name__ == '__main__':
    tester = Tester()
    tester.run_all_tests("../ExampleImages/Shepp_logan.jpg")
