from math import radians

import numpy as np
from matplotlib import pyplot as plt


class Tomograph:
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


    def bresenham(self, x1, y1, x2, y2):
        pass

    def createSinogram(self):
        pass

    def singleScan(self):
        pass

