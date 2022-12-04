#!/usr/bin/env python3

import math
import numpy as np
import matplotlib.pyplot as plt
import sympy

import geometrik.threed as g3d

from goto.globe.plot import GlobePlotMpl

theta, psi, R = sympy.symbols('theta psi R')

Nz = g3d.Vector(0, -sympy.sin(theta), sympy.cos(theta), is_unit=True)
Ny = g3d.Vector(0, sympy.cos(theta), sympy.sin(theta), is_unit=True)
Nx = g3d.Vector(1, 0, 0, is_unit=True)

Ux = g3d.Vector(sympy.cos(psi), sympy.sin(psi), 0, is_unit=True)

Mx = Ux.project_normal(Nz)

# psi_equ = Ux.angle_to(Mx).simplify()
# sympy.pprint(psi_equ)

# psi_sol = sympy.solve(psi_equ - R, psi)
# sympy.pprint(psi_sol[0])

psi_alt = sympy.asin(sympy.sin(R) / sympy.sin(theta))

m_val = {'theta': math.pi / 5, 'R': 0.3}
m_val['psi'] = float(psi_alt.subs(m_val))

r = Ux.angle_to(Mx)

with GlobePlotMpl() as gpl :
    gpl.add_point(Nx.res(m_val), 'Nx', 'r')
    gpl.add_point(Ny.res(m_val), 'Ny', 'g')
    gpl.add_point(Nz.res(m_val), 'Nz', 'b')
    gpl.add_great_circle(Nz.res(m_val), 'black')
    gpl.add_circle(Ux.res(m_val), float(r.subs(m_val)), 'orange')
    gpl.add_point(Ux.res(m_val), 'Ux', 'yellow')
    gpl.add_point(Mx.res(m_val), 'Mx', 'purple')