#!/usr/bin/env python3

val = {
	'A_x': A.x, 'A_y': A.y, 'A_z': A.z,
	'B_x': B.x, 'B_y': B.y, 'B_z': B.z,
	'I_x': I.x, 'I_y': I.y, 'I_z': I.z,
	'Q_x': Q.x, 'Q_y': Q.y, 'Q_z': Q.z,
}

# symbolic part

t = sympy.symbols('t')

A = g3d.Vector( * sympy.symbols('A_x A_y A_z'), True )
B = g3d.Vector( * sympy.symbols('B_x B_y B_z'), True )
C = g3d.Vector( * sympy.symbols('C_x C_y C_z'), True )

I = g3d.Vector( * sympy.symbols('I_x I_y I_z'), True )
Q = g3d.Vector( * sympy.symbols('Q_x Q_y Q_z'), True )

V = B * sympy.cos(t) + Q * sympy.sin(t)

Pab_Z = g3d.Vector( * sympy.symbols('PabZx PabZy PabZz'), True )
Pab_Y = (Pab_Z @ V).normalized()
Pab_X = (Pab_Y @ Pab_Z)

left_angle = (Pab_X * V)
center_angle = (I * V)

