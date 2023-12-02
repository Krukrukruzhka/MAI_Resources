import matplotlib.pyplot as plt
import numpy as np
import customtkinter


def func(x, y, a: float, b: float):
    return (x/a)**2 + (y/b)**2 - 1


def draw(a: float, b: float, step: int = 10):
    x_min, x_max = -1.5, 1.5
    y_min, y_max = -1.5, 1.5
    step -= 1

    x = np.linspace(x_min, x_max, step)
    y = np.linspace(y_min, y_max, step)
    X, Y = np.meshgrid(x, y)

    plt.contour(X, Y, func(X, Y, a, b), levels=[0], colors='black')
    plt.axis('equal')
    plt.grid()
    plt.show()


def draw_plot():
    draw(a=float(entry1.get()), b=float(entry2.get()), step=int(entry3.get()))


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x400")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label1 = customtkinter.CTkLabel(master=frame, text="0 < a < 1.5")
label1.pack(pady=30, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="parameter a")
entry1.pack(pady=10, padx=10)

label2 = customtkinter.CTkLabel(master=frame, text="0 < b < 1.5")
label2.pack(pady=30, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="parameter b")
entry2.pack(pady=10, padx=10)

label3 = customtkinter.CTkLabel(master=frame, text="step >= 4")
label3.pack(pady=30, padx=10)

entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="step")
entry3.pack(pady=10, padx=10)

button = customtkinter.CTkButton(master=frame, text="Draw", command=draw_plot)
button.pack(pady=10, padx=10)

root.mainloop()
