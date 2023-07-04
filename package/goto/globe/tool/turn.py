#!/usr/bin/env python3

import math

def revert_turn_3pt(A, E, F, C) :
	""" compute the point B which allowed the construction of the turn 3pt """
	U = (E @ A) # .normalized()
	V = (C @ F) # .normalized()

	print(U)
	print(V)

	N = E + F
	B = (V @ U).normalized()

	w = math.copysign(1.0, N * B)

	return w * B

if __name__ == '__main__' :
	from goto.globe.plot import GlobePlotMpl
	from goto.globe.blip import Blip
	
	A = Blip(0.0, 0.0).as_vector
	E = Blip(40.0, 0.0).as_vector
	F = Blip(45.0, -5.0).as_vector
	C = Blip(45.0, -50.0).as_vector

	A = Blip(43.555999, 5.289780).as_vector
	E = Blip(43.562706, 5.329391).as_vector
	F = Blip(43.558699, 5.336977).as_vector
	C = Blip(43.538373, 5.339280).as_vector

	B = revert_turn_3pt(A, E, F, C)
	print(B, Blip.from_vector(B))

	with GlobePlotMpl() as plt :
		plt.add_point(A, 'A', 'r')
		plt.add_point(E, 'E', 'r')
		plt.add_point(F, 'F', 'b')
		plt.add_point(C, 'C', 'b')
		plt.add_point(B, 'B', 'g')
