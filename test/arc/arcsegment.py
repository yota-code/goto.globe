#!/usr/bin/env python3

import math

import geometrik.threed as g3d

from goto.globe.blip import Blip
from goto.globe.arc import ArcSegment

from goto.globe.plot import GlobePlotMpl


A = Blip(0.0, -90.0).as_vector
B = Blip(0.0, -35.0).as_vector

for i in [True, False] :

	if i :
		print("right turn")
		M = Blip(15.0, -45.0).as_vector
		arc = ArcSegment(A, B, 0.55)
	else :
		print("left turn")
		M = Blip(-15.0, -45.0).as_vector
		arc = ArcSegment(A, B, -0.55)

	P, t, h, d = arc.status(M)

	print(f"HDG = {h}")
	print(f"adv = {t*100:0.1f}%")
	print(f"dev = {d}")

	with GlobePlotMpl() as u :
		u.add_point(A, "A", 'purple')
		u.add_point(B, "B", 'purple')
		u.add_point(M, "M", 'yellow')
		u.add_point(P, "P", 'orange')
		# u.add_point(arc.Vx, "Vx", 'magenta')
		# u.add_point(arc.Vy, "Vy", 'cyan')
		# u.add_point(arc.Vz, "Vz", 'yellow')
		# u.add_point(arc.Ax, "Ax", 'r')
		# u.add_point(arc.Ay, "Ay", 'g')
		# u.add_point(arc.Az, "Az", 'b')
		# u.add_point(arc.Bx, "Bx", 'r')
		# u.add_point(arc.By, "By", 'g')
		# u.add_point(arc.Bz, "Bz", 'b')
		u.add_point(arc.Ux, "Ux", 'r')
		u.add_point(arc.Uy, "Uy", 'g')
		u.add_point(arc.Uz, "Uz", 'b')

		u.add_segment(arc)