"""Sonde d'empreinte de K1 (remarque sur Python, docs/PYTHON.md 2) : octets par particule de 16 flottants, mesurés par
tracemalloc sur N particules (liste comprise) : classe ordinaire (le code publié), classe à __slots__, tableau plat
array('d') et array('f') de 16 N valeurs. Usage : python3.15 footprint.py [N]"""
import sys, tracemalloc
from array import array

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
F = ("x", "y", "z", "vx", "vy", "vz", "ax", "ay", "az", "mass", "charge", "radius", "temp", "pressure", "energy", "density")


class Particle:
    def __init__(self, x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.ax, self.ay, self.az = ax, ay, az
        self.mass, self.charge, self.radius = mass, charge, radius
        self.temp, self.pressure, self.energy, self.density = temp, pressure, energy, density


class Slotted:
    __slots__ = F

    def __init__(self, x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.ax, self.ay, self.az = ax, ay, az
        self.mass, self.charge, self.radius = mass, charge, radius
        self.temp, self.pressure, self.energy, self.density = temp, pressure, energy, density


def measure(make):
    tracemalloc.start()
    a = tracemalloc.get_traced_memory()[0]
    obj = make()
    b = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    del obj
    return (b - a) / N


vals = lambda i: [float(i + j) + 0.5 for j in range(16)]  # flottants distincts, non partagés
print(f"{sys.version.split()[0]} GIL={sys._is_gil_enabled()} N={N}")
print(f"classe ordinaire : {measure(lambda: [Particle(*vals(i)) for i in range(N)]):.1f} o/particule")
print(f"classe à __slots__ : {measure(lambda: [Slotted(*vals(i)) for i in range(N)]):.1f} o/particule")
print(f"array('d') : {measure(lambda: array('d', (x for i in range(N) for x in vals(i)))):.1f} o/particule")
print(f"array('f') : {measure(lambda: array('f', (x for i in range(N) for x in vals(i)))):.1f} o/particule")
print(f"sys.getsizeof : objet ordinaire {sys.getsizeof(Particle(*vals(0)))}, à __slots__ {sys.getsizeof(Slotted(*vals(0)))}, "
      f"flottant {sys.getsizeof(1.5)}")
