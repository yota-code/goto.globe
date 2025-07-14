#!/usr/bin/env python3C

import math

import goto.globe

from goto.globe.blip import Blip
from goto.globe.segment.line import SegmentLine

def turn_3pt(A:Blip, B:Blip, C:Blip, radius:float, debug=None) :
	"""
	radius is expected in meters
	"""

	# aperture is in radians
	aperture = radius / goto.globe.earth_radius

	line_one = SegmentLine(B, A)
	line_two = SegmentLine(B, C)

	P, R, S = line_one.Bx, line_one.Ax, line_two.Bx

	q = line_one.Az.angle_to(line_two.Az, line_one.Ax)
	Q = (line_one.Az + line_two.Az).normalized()

	w = math.copysign(1.0, q)

	r = -(P * Q)**2 / (
		P.y**2*(-1+R.y**2) +
		2*P.x*P.z*R.x*R.z +
		2*P.y*R.y*(P.x*R.x+P.z*R.z) +
		P.z**2*(-1+R.z**2) -
		P.x**2*(R.y**2+R.z**2)
	)

	t = math.acos(math.sqrt(math.cos(aperture)**2 - r) / math.sqrt(1 - r))

	V = R.deflect(Q, t)

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

	BEp = R.angle_to(E) / line_one.length
	BFp = R.angle_to(F) / line_two.length

	if debug :
		if isinstance(debug, Path) :
			from goto.globe.plot import GlobePlotGps as GlobePlot
		else :
			from goto.globe.plot import GlobePlotMpl as GlobePlot
		
		print("q = ", q)
		print("w = ", w)
		with GlobePlot() as gpl :
			gpl.add_point(P, 'A', 'k')
			gpl.add_point(R, 'B', 'k')
			gpl.add_point(S, 'C', 'k')
			gpl.add_line(line_one.Ax, line_one.Bx, 'r')
			gpl.add_line(line_two.Ax, line_two.Bx, 'g')
			gpl.add_point(V, 'V', 'cyan')
			gpl.add_point(E, 'E', 'b')
			gpl.add_point(F, 'F', 'b')
			gpl.add_arc_from_center(E, F, V, 'magenta')

	return Blip.from_vector(E), Blip.from_vector(F), BEp, BFp, w


def turn_4pt(self, A, B, C, D) :

	## TODO: check implementation !

	line_AB = LineSegment(A, B)
	line_BC = LineSegment(B, C)
	line_CD = LineSegment(C, D)

	ABCa = line_AB.surface_angle(line_BC)
	BCDa = line_BC.surface_angle(line_CD)

	w1 = math.copysign(1.0, ABCa)
	w2 = math.copysign(1.0, BCDa)

	assert(0 < w1 * w2)

	ABCz = - (line_AB.Lz + line_BC.Lz).normalized()
	BCDz = - (line_BC.Lz + line_CD.Lz).normalized()

	ABCy = B @ ABCz
	BCDy = C @ BCDz

	# the center of the circle inscribed is V
	V = - (ABCy @ BCDy).normalized() * math.copysign(1.0, ABCa)

	E = line_AB.projection(V)
	F = line_BC.projection(V)
	G = line_CD.projection(V)

	VEa = V.angle_to(E)
	VFa = V.angle_to(F)
	VGa = V.angle_to(G)

	assert(
		math.isclose(VEa, VFa, rel_tol=1e-4) and
		math.isclose(VFa, VGa, rel_tol=1e-4) and
		math.isclose(VGa, VEa, rel_tol=1e-4)
	)

	AEp = A.angle_to(E) / line_AB.length
	BFp = B.angle_to(F) / line_BC.length
	CGp = C.angle_to(G) / line_CD.length

	return Blip.from_vector(E), Blip.from_vector(F), Blip.from_vector(G), w1 * VFa, AEp, BFp, CGp

if __name__ == '__main__' :
	

	A = Blip(0.0, 0.0)
	B = Blip(45.0, 5.0)
	C = Blip(0.0, 70.0)

	turn_3pt(A, B, C, 2000000.0, True)

