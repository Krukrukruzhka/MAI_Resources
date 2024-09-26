import math


def target_method(
    a: float,
    b: float,
    n: int,
    f: function,
    kernel: function
):
    h = (b - a) / n

    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            x = a + i * h
            y = a + j * h
            A[i][j] = kernel(x, y)

    B = [0] * n
    for i in range(n):
        x = a + i * h
        B[i] = f(x)

    x = [0] * n
    for i in range(n):
        for j in range(n):
            x[i] += A[i][j] * B[j]

    integral = 0
    for i in range(n):
        integral += x[i] * h


if __name__ == "__main__":
    f = lambda x: x
    kern = lambda x, y: x+y
    integral = target_method(
        a=float(input()),
        b=float(input()),
        n = int(input()),
        f=f,
        kernel=kern
    )
