import numpy as np


class Position3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.data = np.array([x, y, z], dtype=float)

    @property
    def x(self):
        return self.data[0]

    @property
    def y(self):
        return self.data[1]

    @property
    def z(self):
        return self.data[2]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @y.setter
    def y(self, value):
        self.data[1] = value

    @z.setter
    def z(self, value):
        self.data[2] = value

    def magnitude(self):
        return np.linalg.norm(self.data)

    def __sub__(self, other):
        return Position3(*(self.data - other.data))

    def __add__(self, other):
        return Position3(*(self.data + other.data))

    def __repr__(self):
        return f"Position3({self.data[0]}, {self.data[1]}, {self.data[2]})"

class Thetas:
    def __init__(self, angle1=0.0, angle2=0.0, angle3=0.0):
        self.angle = [angle1, angle2, angle3]

    def __repr__(self):
        return f"Thetas({self.angle[0]}, {self.angle[1]}, {self.angle[2]})"

class Velocity:
    def __init__(self, Vx=0.0, Vy=0.0, omega=0.0):
        self.Vx = Vx
        self.Vy = Vy
        self.omega = omega

    def __repr__(self):
        return f"Velocity(Vx={self.Vx}, Vy={self.Vy}, omega={self.omega})"