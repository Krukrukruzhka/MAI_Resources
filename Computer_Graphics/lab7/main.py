import customtkinter
import matplotlib.pyplot as plt
from random import uniform
import numpy as np

points = [(uniform(-5, 5), uniform(-5, 5)) for i in range(5)]


def func(x: float, coordinates: list[tuple[float, float]]):
    y = 0
    n = len(coordinates)
    for i in range(n):
        l_i = 1
        for j in range(n):
            if j != i:
                l_i *= (x - coordinates[j][0])/(coordinates[i][0] - coordinates[j][0])
        y += coordinates[i][1]*l_i
    return y


print(*points, sep='\n')

count = 10
X, Y = zip(*points)
plt.plot(X, Y, 'ro')
X = list(np.linspace(min(X)-0.5, max(X)+0.5, count))
Y = [func(x=x, coordinates=points) for x in X]
plt.plot(X, Y)
plt.show()