#!/usr/bin/env python3

import math
import numpy as np
import matplotlib.pyplot as plt
import sympy

import geometrik.threed as g3d

from goto.globe.plot import GlobePlotMpl

Ex = g3d.Vector(1, 0, 0)
Ey = g3d.Vector(0, 1, 0)
Ez = g3d.Vector(0, 0, 1)

theta, psi = sympy.symbols('theta psi')

Nz = g3d.Vector(0, -sympy.sin(theta), sympy.cos(theta))
Ny = g3d.Vector(0, sympy.cos(theta), sympy.sin(theta))
Nx = g3d.Vector(1, 0, 0)

m_val = {'theta': math.pi / 4, 'psi': 0.3}

with GlobePlotMpl() as gpl :
    gpl.add_point(Nx.subs(m_val), 'Nx', 'r')
    gpl.add_point(Ny.subs(m_val), 'Ny', 'g')
    gpl.add_point(Nz.subs(m_val), 'Nz', 'b')
