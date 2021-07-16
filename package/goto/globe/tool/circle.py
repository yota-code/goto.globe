#!/usr/bin/env python3

import math

from goto.globe.plot import GlobePlotMpl

def circle_find_center(A, B, C) :

	Ix = (A + B).normalized()
	Jx = (B + C).normalized()

	Iz = (B @ A).normalized()
	Jz = (C @ B).normalized()

	Iy = Ix @ Iz
	Jy = Jx @ Jz

	w = math.copysign(1.0, B * (Jz @ Iz))

	V = w * (Jy @ Iy).normalized()

	with GlobePlotMpl() as plt :
		plt.add_point(A, 'A', 'r')
		plt.add_point(B, 'B', 'g')
		plt.add_point(C, 'C', 'b')

		plt.add_point(Ix, 'Ix', 'orange')
		plt.add_point(Iy, 'Iy', 'yellow')
		plt.add_point(Iz, 'Iz', 'orange')

		plt.add_point(Jx, 'Jx', 'dodgerblue')
		plt.add_point(Jy, 'Jy', 'cyan')
		plt.add_point(Jz, 'Jz', 'dodgerblue')

		plt.add_point(V, 'v', 'magenta')

		plt.add_circle(V, B)

	return V

if __name__ == '__main__' :
	from goto.globe.blip import Blip
	
	A = Blip(0.0, 0.0).as_vector
	B = Blip(30.0, 0.0).as_vector
	C = Blip(35.0, -15.0).as_vector

	circle_find_center(A, B, C)