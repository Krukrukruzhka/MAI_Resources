""""
Реализация метода дихотомии (половинного деления)

Даннаый метод хорошо и достаточно быстро ищет точки локального минимуа/максимума в тех случаях, где таких экстремумов
не более одного. В остальных случаях алгоритм может давать далеко не самый оптимальный результат.

Например, если в функции содержатся функции синуса/косинуса, то алгоритм может выдать вместо локального минимума
локальный максимум (и наоборот). Поэтому перед использованием стоит заранее построить график и удачно выбрать начальные
значения левой и правой границы.
"""


import math
import numpy as np
import matplotlib.pyplot as plt


def func(x: float) -> float:
    # Заданная функция
    # return (x+2)**3/5 - math.sin(10*x-1)/2 + 3
    return (x+2)**2/5


if __name__ == "__main__":
    left, right = -20, 100  # Диапазон функции
    interval_length, eps = 1e-7, 1e-8  # Эпсиллон и минимальный размер интервала
    step = 10_000  # Число узлов графика (частота дискретизации)
    find_min = True  # True если ищем глобальный минимум, False если максимум

    # Проверка заданных значений на корректность
    assert left < right, "Правая граница должна быть больше левой"
    assert interval_length > 0 and eps > 0, "Минимальный размер интервала должен быть положителен"
    assert eps < 2*interval_length, "Для корректной работы алгоритма эпсилон должен быть меньше точности интервала не более чем в 2 раза"
    assert step > 0 and type(step) == int, "Параметр step должен быть положительным целым числом"

    # Отрисовка графика функции и граничных точек
    x_vect = np.linspace(left, right, step)
    y_vect = np.vectorize(func)(x_vect)

    plt.plot(x_vect, y_vect)
    plt.plot(left, func(left), 'ro')
    plt.plot(right, func(right), 'ro')

    # Реализация метода дихотомии
    while abs(right - left) > interval_length:
        if func((left+right-eps)/2) > func((left+right+eps)/2) and find_min:
            left = (left+right-eps)/2
            plt.plot(left, func(left), 'go')
        else:
            right = (left+right+eps)/2
            plt.plot(right, func(right), 'go')

    # Вывод результатов и построение графика
    res = (left+right)/2, func((left+right)/2)
    print(f"Точка локального {'минимума' if find_min else 'максимума'} (x, y) = {res}")
    plt.show()
