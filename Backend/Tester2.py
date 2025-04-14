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

    # Test RMSE w kolejnych iteracjach rekonstrukcji
    def test_rmse_vs_iterations(self, image_array, alpha, number_of_detectors, angular_spread, center, radius_x, radius_y, filter_sinogram=False):
        rmse_values = []

        # Generuj pełny sinogram i mapę linii
        lines, sinogram = self.tomograph.createSinogram(
            image_array, alpha, number_of_detectors, angular_spread, center, radius_x, radius_y, filter_sinogram
        )

        # Rekonstruuj wszystkie iteracje
        reconstructed_images = self.tomograph.createReconstruction(
            sinogram, alpha, number_of_detectors, radius_x, radius_y, lines
        )

        # Oblicz RMSE dla każdej iteracji
        for i in range(1, len(reconstructed_images) + 1):
            rmse = self.utils.calculateRMSE(image_array, reconstructed_images[i])
            rmse_values.append(rmse)
            print(f"Iteracja: {i}, RMSE: {rmse}")

        # Wykres RMSE vs iteracja
        plt.plot(range(1, len(reconstructed_images) + 1), rmse_values, marker='o')
        plt.title("RMSE vs Iteracja rekonstrukcji")
        plt.xlabel("Numer iteracji")
        plt.ylabel("RMSE")
        plt.grid(True)
        plt.savefig("output/recon_iterations_chart.png")

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
        plt.savefig("output/recon_scans_chart.png")

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
        plt.savefig("output/recon_angular_chart.png")

    # Test porównujący filtrację i brak filtracji dla dwóch obrazów
    def test_filtering_comparison(self, image_paths):
        alpha = 1
        detectors = 360
        spread = 180 # Zmiana, ponieważ robimy równolegle

        for image_path in image_paths:
            image_array = self.converter.JPGtoMatrix(image_path)
            center = self.utils.getCenterOfImage(image_array)
            radius_y, radius_x = self.utils.getRadiusOfImage(image_array)

            # Z filtrem
            lines_f, sinogram_f = self.tomograph.createSinogram(
                image_array, alpha, detectors, spread, center, radius_x, radius_y, filter=True
            )
            recon_f = self.tomograph.createReconstruction(sinogram_f, alpha, detectors, radius_x, radius_y, lines_f,
                                                          testing=True)

            # Bez filtra
            lines_nf, sinogram_nf = self.tomograph.createSinogram(
                image_array, alpha, detectors, spread, center, radius_x, radius_y, filter=False
            )
            recon_nf = self.tomograph.createReconstruction(sinogram_nf, alpha, detectors, radius_x, radius_y,
                                                           lines_nf, testing=True)

            # RMSE względem oryginału
            rmse_f = self.utils.calculateRMSE(image_array, recon_f)
            rmse_nf = self.utils.calculateRMSE(image_array, recon_nf)

            print(f"Obraz: {os.path.basename(image_path)}")
            print(f"RMSE z filtrem: {rmse_f:.4f}")
            print(f"RMSE bez filtra: {rmse_nf:.4f}")

            # Zapisz obrazy wynikowe
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            self.saver.saveMatrixAsJPG(recon_f, f"output/{base_name}_filtered.jpg")
            self.saver.saveMatrixAsJPG(recon_nf, f"output/{base_name}_no_filter.jpg")

    def run_all_tests(self, image_url):
        image_array = self.converter.JPGtoMatrix(image_url)
        center = self.utils.getCenterOfImage(image_array)
        radius_y, radius_x = self.utils.getRadiusOfImage(image_array)

        alpha = 2  # odpowiada 180 skanom
        detectors = 180
        angular_spread = 180

        self.test_rmse_vs_iterations(image_array, alpha, detectors, angular_spread, center, radius_x, radius_y)
        self.test_rmse_vs_detectors(image_array, alpha, angular_spread, center, radius_x, radius_y)
        self.test_rmse_vs_scans(image_array, detectors, angular_spread, center, radius_x, radius_y)
        self.test_rmse_vs_angular_spread(image_array, alpha, detectors, center, radius_x, radius_y)

        image_paths = [
            "../ExampleImages/Shepp_logan.jpg",
            "../ExampleImages/CT_ScoutView.jpg"
        ]
        self.test_filtering_comparison(image_paths)

if __name__ == '__main__':
    tester = Tester()
    tester.run_all_tests("../ExampleImages/Shepp_logan.jpg")
