import numpy as np

class Filter:
    # Tworzenie filtru wykorzystywanego opcjonalnie przy rekonstrukcji
    # Domyślnie rozmiar 21 - takiego użyto również finalnie
    def createFilter(self, size=21):
        k = np.arange(-size // 2, size // 2 + 1)
        kernel = np.zeros_like(k, dtype=np.float32)

        # Ustawienie wartości filtra wg. wzoru załączonego na prezentacji
        # k parzyste już mają wartość 0
        kernel[k == 0] = 1 # środkowy element

        odd_k = k[k % 2 != 0] # wyodrębnione k nieparzyste
        kernel[k % 2 != 0] = -4 / (np.pi ** 2 * odd_k ** 2) # k nieparzyste

        # Zwracamy gotowy filtr 1D
        return kernel

    # Nakładanie filtru na sinogram
    def filterSinogram(self, sinogram: np.ndarray, kernel) -> np.ndarray:
        # Iterowanie po wszystkich rzędach sinogramu
        for i in range(sinogram.shape[0]):
            # Nałożenie filtru za pomocą konwolucji
            sinogram[i, :] = np.convolve(sinogram[i, :], kernel, mode='same')
        # Zwracamy przefiltrowany sinogram
        return sinogram
