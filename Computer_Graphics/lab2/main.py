import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import customtkinter


def draw_cube():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    length = float(entry1.get())

    vertices = np.array([
        [-length, -length, -length],
        [-length, -length, length],
        [-length, length, -length],
        [-length, length, length],
        [length, -length, -length],
        [length, -length, length],
        [length, length, -length],
        [length, length, length]
    ])

    faces = np.array([
        [0, 1, 3, 2],
        [0, 4, 5, 1],
        [0, 2, 6, 4],
        [1, 5, 7, 3],
        [2, 3, 7, 6],
        [4, 6, 7, 5]
    ])

    cube = [Poly3DCollection([vertices[face] for face in faces], alpha=1, facecolor='blue', edgecolor='k')]

    ax.add_collection3d(cube[0])
    length *= 1.5
    ax.auto_scale_xyz([-length, length], [-length, length], [-length, length])
    plt.show()


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

button = customtkinter.CTkButton(master=frame, text="Draw", command=draw_cube)
button.pack(pady=10, padx=10)

root.mainloop()
