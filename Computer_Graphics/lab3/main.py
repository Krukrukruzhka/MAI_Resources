import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import cos, sin, radians
import customtkinter


def rotate_matrix(x: float = 360, y: float = 360, z: float = 360) -> np.array:
    x, y, z = radians(x), radians(y), radians(z)
    return np.array([[round(cos(y)*cos(z), 14), round(sin(x)*sin(y)*cos(z)-cos(x)*sin(z), 14), round(cos(x)*sin(y)*cos(z)+sin(x)*sin(z), 14)],
                     [round(cos(y)*sin(z), 14), round(sin(x)*sin(y)*sin(z)+cos(x)*cos(z), 14), round(cos(x)*sin(y)*sin(z)-sin(x)*cos(z), 14)],
                     [round(-sin(y), 14), round(sin(x)*cos(y), 14), round(cos(x)*cos(y), 14)]])


class Taper:
    def __init__(self,
                 height: float, top_radius: float, bottom_radius: float,
                 sides: int = 10,
                 x0: float = 0, y0: float = 0, z0: float = 0,):
        self.height = height
        self.top_radius = top_radius
        self.bottom_radius = bottom_radius
        self.sides = sides
        angle_step = 360 / sides
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0

        self.top_center = np.array([0, height/2, z0])
        self.bottom_center = np.array([0, -height/2, z0])

        self.top_coordinates = np.array([[x0 + top_radius * cos(radians(i*angle_step)),
                                          y0 + height/2,
                                          z0 + top_radius * sin(radians(i*angle_step))] for i in range(sides+1)])
        self.bottom_coordinates = np.array([[x0 + bottom_radius * cos(radians(i*angle_step)),
                                             y0 - height/2,
                                             z0 + bottom_radius * sin(radians(i*angle_step))] for i in range(sides+1)])

    def rotate(self, x: float = 360, y: float = 360, z: float = 360):
        self.top_center = np.dot(self.top_center, rotate_matrix(x, y, z))
        self.bottom_center = np.dot(self.bottom_center, rotate_matrix(x, y, z))
        self.top_coordinates = np.dot(self.top_coordinates, rotate_matrix(x, y, z))
        self.bottom_coordinates = np.dot(self.bottom_coordinates, rotate_matrix(x, y, z))

    def scale(self, value: float):
        self.top_coordinates *= value
        self.bottom_center *= value
        self.bottom_coordinates *= value
        self.top_center *= value


def move(taper: Taper, dx: float = 0, dy: float = 0, dz: float = 0):

    taper.top_coordinates[:, 0] += dx
    taper.bottom_coordinates[:, 0] += dx
    taper.top_center[0] += dx
    taper.bottom_center[0] += dx

    taper.top_coordinates[:, 1] += dy
    taper.bottom_coordinates[:, 1] += dy
    taper.top_center[1] += dy
    taper.bottom_center[1] += dy

    taper.top_coordinates[:, 2] += dz
    taper.bottom_coordinates[:, 2] += dz
    taper.top_center[2] += dz
    taper.bottom_center[2] += dz


def draw_taper(figure: Taper):
    top, bottom = figure.top_coordinates, figure.bottom_coordinates

    glBegin(GL_TRIANGLE_STRIP)
    for i in range(figure.sides+1):
        glVertex3f(top[i][0], top[i][1], top[i][2])
        glVertex3f(bottom[i][0], bottom[i][1], bottom[i][2])
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(*figure.top_center)
    for i in range(figure.sides+1):
        glVertex3f(top[i][0], top[i][1], top[i][2])
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(*figure.bottom_center)
    for i in range(figure.sides+1):
        glVertex3f(bottom[i][0], bottom[i][1], bottom[i][2])
    glEnd()


def key_handler(pressed_keys, taper: Taper):
    alpha, betta, gamma = 0, 0, 0
    speed = 3

    if pressed_keys[pygame.K_d]:
        betta += speed
    if pressed_keys[pygame.K_a]:
        betta -= speed
    if pressed_keys[pygame.K_s]:
        alpha -= speed
    if pressed_keys[pygame.K_w]:
        alpha += speed
    if pressed_keys[pygame.K_q]:
        gamma -= speed
    if pressed_keys[pygame.K_e]:
        gamma += speed

    if pressed_keys[pygame.K_UP]:
        move(taper, dy=0.02)
    if pressed_keys[pygame.K_DOWN]:
        move(taper, dy=-0.02)
    if pressed_keys[pygame.K_LEFT]:
        move(taper, dx=0.02)
    if pressed_keys[pygame.K_RIGHT]:
        move(taper, dx=-0.02)
    if pressed_keys[pygame.K_LCTRL]:
        move(taper, dz=0.02)
    if pressed_keys[pygame.K_SPACE]:
        move(taper, dz=-0.02)

    if pressed_keys[pygame.K_EQUALS]:
        taper.scale(1.01)
    if pressed_keys[pygame.K_MINUS]:
        taper.scale(0.99)

    taper.rotate(alpha, betta, gamma)


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x400")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label1 = customtkinter.CTkLabel(master=frame, text="height")
label1.pack(pady=30, padx=10)

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="height")
entry1.pack(pady=10, padx=10)

label2 = customtkinter.CTkLabel(master=frame, text="top radius")
label2.pack(pady=30, padx=10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="top")
entry2.pack(pady=10, padx=10)

label3 = customtkinter.CTkLabel(master=frame, text="bottom radius")
label3.pack(pady=30, padx=10)

entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="bottom radius")
entry3.pack(pady=10, padx=10)

label4 = customtkinter.CTkLabel(master=frame, text="sides")
label4.pack(pady=30, padx=10)

entry4 = customtkinter.CTkEntry(master=frame, placeholder_text="sides")
entry4.pack(pady=10, padx=10)


def main():
    taper = Taper(height=float(entry1.get()), top_radius=float(entry2.get()), bottom_radius=float(entry3.get()), sides=int(entry4.get()))

    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5.0)

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

    glLightfv(GL_LIGHT0, GL_POSITION, [0.4, 0.8, 1, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glEnable(GL_LIGHT0)

    glMaterial(GL_FRONT, GL_DIFFUSE, [1.0, 0.0, 0.0, 1.0])
    glMaterial(GL_FRONT, GL_AMBIENT, [1.0, 0.0, 1.0, 0.5])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        key_handler(pygame.key.get_pressed(), taper)
        draw_taper(taper)

        pygame.display.flip()
        pygame.time.wait(10)


button = customtkinter.CTkButton(master=frame, text="Draw", command=main)
button.pack(pady=10, padx=10)

root.mainloop()
