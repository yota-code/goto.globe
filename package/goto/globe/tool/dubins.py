#!/usr/bin/env python3

import math
import sys

import geometrik.threed as g3d

from goto.globe.plot import GlobePlotMpl


def compute_circle(A, B, r) :
	assert( r > 0 )

	Ex = 

def compute_internal(A, B, r) :
	# two point A and B, center of the circles of radius r

	assert( r > 0 )

	Cx = (A + B).normalized()
	Cz = (A @ B).normalized()
	Cy = (Cz @ Cx)

	psi = Cx.angle_to(B)
	
	theta = math.asin(math.sin(r) / math.sin(psi))

	P_pos = g3d.Plane( g3d.Vector.compose(Cz, Cy, - theta) )
	P_neg = g3d.Plane( g3d.Vector.compose(Cz, Cy, theta) )

	return [
		P_pos.project(A).normalized(),
		P_pos.project(B).normalized(),
		P_neg.project(A).normalized(),
		P_neg.project(B).normalized()
	]

def compute_external(A, B, r) :

	assert( r > 0 )

	Cx = (A + B).normalized()
	Cz = (A @ B).normalized()
	Cy = (Cz @ Cx)

	psi = (math.pi / 2) - Cx.angle_to(B)

	theta = math.asin(math.sin(r) / math.sin(psi))

	P_pos = g3d.Plane( g3d.Vector.compose(Cz, Cx, - theta) )
	P_neg = g3d.Plane( g3d.Vector.compose(Cz, Cx, theta) )

	return [
		P_pos.project(A).normalized(),
		P_pos.project(B).normalized(),
		P_neg.project(A).normalized(),
		P_neg.project(B).normalized()
	]

def compute(Px_ini, hdg_ini, Px_fin, hdg_fin, r) :
	Ny_ini, Nz_ini = Px_ini.frame(g3d.v_north)
	Ny_fin, Nz_fin = Px_fin.frame(g3d.v_north)

	Py_ini = g3d.Vector.compose(Ny_ini, -Nz_ini, hdg_ini)
	Pz_ini = g3d.Vector.compose(Nz_ini, Ny_ini, hdg_ini)

	Py_fin = g3d.Vector.compose(Ny_fin, -Nz_fin, hdg_fin)
	Pz_fin = g3d.Vector.compose(Nz_fin, Ny_fin, hdg_fin)

	C_il = g3d.Vector.compose(Px_ini, Py_ini, -r)
	C_ir = g3d.Vector.compose(Px_ini, Py_ini, r)

	C_fl = g3d.Vector.compose(Px_fin, Py_fin, -r)
	C_fr = g3d.Vector.compose(Px_fin, Py_fin, r)

	D_ell_lst = compute_external(C_il, C_fl, r)
	D_err_lst = compute_external(C_ir, C_fr, r)

	D_ilr_lst = compute_internal(C_il, C_fr, r)
	D_irl_lst = compute_internal(C_ir, C_fl, r)

	with GlobePlotMpl() as g :
		g.add_circle(C_il, r, 'cyan')
		g.add_circle(C_ir, r, 'cyan')
		g.add_circle(C_fl, r, 'cyan')
		g.add_circle(C_fr, r, 'cyan')
		g.add_point(Px_ini, 'Px_ini')
		g.add_point(Px_fin, 'Px_fin')

		g.add_signed_arc(Px_ini, D_ilr_lst[0], C_il, -1, 'r')
		g.add_line(D_ilr_lst[0], D_ilr_lst[1], 'r')
		g.add_signed_arc(D_ilr_lst[1], Px_fin, C_fr, 1, 'r')

	# with GlobePlotMpl() as g :
	# 	g.add_point(Px_ini, 'Px_ini')
	# 	g.add_point(Py_ini, 'Py_ini')
	# 	g.add_point(Pz_ini, 'Pz_ini')
	# 	g.add_point(Px_fin, 'Px_fin')
	# 	g.add_point(Py_fin, 'Py_fin')
	# 	g.add_point(Pz_fin, 'Pz_fin')



if __name__ == '__main__' :

	from goto.globe.blip import Blip

	r = 0.3

	A = Blip(0.0, 0.0).as_vector
	B = Blip(45.0, 45.0).as_vector


	compute(A, -0.2, B, 0.5, r)

	sys.exit(0)

	I_pos, I_neg, (i0, i1, i2, i3) = compute_internal(A, B, r)
	E_pos, E_neg, (e0, e1, e2, e3) = compute_external(A, B, r)

	with GlobePlotMpl() as g :
		g.add_point(A, 'A')
		g.add_point(B, 'B')
		g.add_circle(A, r)
		g.add_circle(B, r)

		g.add_point(i0, 'I_0')
		g.add_point(i1, 'I_1')
		g.add_point(i2, 'I_2')
		g.add_point(i3, 'I_3')

		g.add_point(e0, 'E_0')
		g.add_point(e1, 'E_1')
		g.add_point(e2, 'E_2')
		g.add_point(e3, 'E_3')

		g.add_line(i0, i1, 'cyan')
		g.add_line(i2, i3, 'cyan')

		g.add_line(e0, e1, 'magenta')
		g.add_line(e2, e3, 'magenta')
