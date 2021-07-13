#!/usr/bin/env python3

import math

from goto.globe.blip import Blip

from goto.globe.lineto import LineTo
from goto.globe.arcto import ArcTo

DISABLED !!

def turn_on_4pt(self, A, B, C, D) :

	line_AB = LineTo(A, B)
	line_BC = LineTo(B, C)
	line_CD = LineTo(C, D)

	ABCa = line_AB.surface_angle(line_BC)
	BCDa = line_BC.surface_angle(line_CD)

	assert(0 < ABCa * BCDa)

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
		math.isclose(VEa, VFa) and
		math.isclose(VFa, VGa) and
		math.isclose(VGa, VEa)
	)

	return [
		LineTo(A, E),
		ArcTo(E, F, VEa),
		ArcTo(F, G, VEa),
		LineTo(G, D)
	]

def turn_3pt(self, A, B, C, radius) :

	line_AB = LineTo(A, B)
	line_BC = LineTo(B, C)

	ABCa = line_AB.surfacea(line_BC)

	ABCz = - (line_AB.Lz + line_BC.Lz).normalized()

	V = B.deviate(ABCz, radius)

	E = line_AB.projection(V)
	F = line_BC.projection(V)

	VEa = V.angle_to(E)
	VFa = V.angle_to(F)

	BEp = B.angle(E) / line_AB.angle_ab
	BFp = B.angle(F) / line_EF

	assert(	math.isclose(VEa, VFa) )

	return Blip.from_vector(E), Blip.from_vector(F), VEa
