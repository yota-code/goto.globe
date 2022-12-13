#!/usr/bin/env python3

import math

import goto.globe

from goto.globe.blip import Blip
from goto.globe.segment.line import SegmentLine

def turn_3pt(A:Blip, B:Blip, C:Blip, radius:float, debug=False) :
	if debug : 
		from goto.globe.plot import GlobePlotMpl

	aperture = radius / goto.globe.earth_radius

	line_one = SegmentLine(B, A)
	line_two = SegmentLine(B, C)

	A, B, C = line_one.Bx, line_one.Ax, line_two.Bx

	q = line_one.Az.angle_to(line_two.Az, B)
	Q = (line_one.Az + line_two.Az).normalized()

	w = math.copysign(1.0, q)

	r = -(A * Q)**2 / (
		A.y**2*(-1+B.y**2) +
		2*A.x*A.z*B.x*B.z +
		2*A.y*B.y*(A.x*B.x+A.z*B.z) +
		A.z**2*(-1+B.z**2) -
		A.x**2*(B.y**2+B.z**2)
	)

	t = math.acos(math.sqrt(math.cos(aperture)**2 - r) / math.sqrt(1 - r))

	V = B.deflect(Q, t)

	E = V.project_normal(line_one.Ay).normalized()
	F = V.project_normal(line_two.Ay).normalized()

	VEa = V.angle_to(E)
	VFa = V.angle_to(F)

	try :
		assert(	math.isclose(VEa, VFa, rel_tol=1e-4) )
		assert(	math.isclose(VEa, aperture, rel_tol=1e-4) )
	except AssertionError :
		print(VEa, VFa, aperture)
		raise

	BEp = B.angle_to(E) / line_one.length
	BFp = B.angle_to(F) / line_two.length

	if debug :
		print("q = ", q)
		print("w = ", w)
		with GlobePlotMpl() as gpl :
			gpl.add_point(A, 'A', 'k')
			gpl.add_point(B, 'B', 'k')
			gpl.add_point(C, 'C', 'k')
			gpl.add_line(line_one.Ax, line_one.Bx, 'r')
			gpl.add_line(line_two.Ax, line_two.Bx, 'g')
			gpl.add_point(V, 'V', 'cyan')
			gpl.add_point(E, 'E', 'b')
			gpl.add_point(F, 'F', 'b')
			gpl.add_arc_from_center(E, F, V, 'magenta')

	return Blip.from_vector(E), Blip.from_vector(F), BEp, BFp, w

if __name__ == '__main__' :
	

	A = Blip(0.0, 0.0)
	B = Blip(45.0, 5.0)
	C = Blip(0.0, 70.0)

	turn_3pt(A, B, C, 2000000.0, True)

