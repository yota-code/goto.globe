#!/usr/bin/env python3

import math

from cc_pathlib import Path

from goto.globe.blip import Blip

from goto.globe.line import LineTo, LineCorridor
from goto.globe.arc import ArcTo

from goto.globe.plot import GlobePlotGps

earth_radius = 6371008.7714
# openstreetmap earth radius = 6378137.0

def interpolate(x, a, b) :
	return a*(1.0 - x) + b*x

class RouteCut() :
	def __init__(self) :
		# load
		self.route_0 = Path("route_0.json").load()
		self.plot_centerline(self.route_0, Path("route_0.plot.json"))

		# apply first pass
		self.route_1 = self.pass_1(self.route_0)
		Path("route_1.json").save(self.route_1)
		self.plot_centerline(self.route_1, Path("route_1.plot.json"))

	def plot_centerline(self, route_lst, route_pth) :
		p_prev = None
		with GlobePlotGps(route_pth) as plt :
			for i, line in enumerate(route_lst) :
				verb, lat, lon, radius, alt, width = line
				p_curr = Blip(lat, lon).as_vector
				if p_prev != None :
					if radius == 0.0 or verb != "GOTO" :
						plt.add_line(p_prev, p_curr)
					else :
						plt.add_arc(p_prev, p_curr, radius / earth_radius)

				plt.add_point(p_curr, f"{i}.{verb}")

				p_prev = p_curr		

	def pass_1(self, r_prev) :
		r_next = list()
		a_lst = [ line[4] for line in r_prev ]

		for i, line in enumerate(r_prev) :
			verb, lat, lon, radius, alt, spd, width = line
			if verb == '__TURN_3PT__' :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				r = radius / earth_radius
				E, F, VEa, AEp, BFp = self.turn_3pt(A, B, C, r)
				r_next.append(["GOTO", E.lat, E.lon, 0, interpolate(AEp, a_lst[i], a_lst[i+1]), spd, width])
				r_next.append(["GOTO", F.lat, F.lon, VEa * earth_radius, interpolate(BFp, a_lst[i], a_lst[i+1]), spd, width])
			elif verb == '__TURN_4PT_1__' :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				D = Blip(r_prev[i+2][1], r_prev[i+2][2]).as_vector
				E, F, G, VFa, AEp, BFp, CGp = self.turn_4pt(A, B, C, D)
				r_next.append(["GOTO", E.lat, E.lon, 0.0, interpolate(AEp, a_lst[i-1], a_lst[i+1]), spd, width])
				r_next.append(["GOTO", F.lat, F.lon, VFa * earth_radius, interpolate(BFp, a_lst[i], a_lst[i+1]), spd, width])
				r_next.append(["GOTO", G.lat, G.lon, VFa * earth_radius, interpolate(CGp, a_lst[i+1], a_lst[i+2]), spd, width])
			elif verb == '__TURN_4PT_2__' :
				pass
			else :
				r_next.append(line)
		
		return r_next

	def pass_2(self, r_prev) :
		r_next = list()
		a_lst = [ line[4] for line in r_prev ]
		for i, line in enumerate(r_prev) :
			verb, lat, lon, radius, alt, width = line
			if verb == 'GOTO' and radius == 0.0 and line[i-1][0] == 'GOTO' and line[i-1][3] == 0.0 :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				r = radius / earth_radius

	def turn_3pt(self, A, B, C, d) :
		line_AB = LineTo(A, B)
		line_BC = LineTo(B, C)

		q = line_AB.Ly.signed_angle_to(line_BC.Ly, B)
		Q = (line_AB.Ly + line_BC.Ly).normalized()

		w = math.copysign(1.0, q)

		R1 = -(A * Q)**2 / (
		    A.y**2*(-1+B.y**2) +
		    2*A.x*A.z*B.x*B.z +
		    2*A.y*B.y*(A.x*B.x+A.z*B.z) +
		    A.z**2*(-1+B.z**2) -
		    A.x**2*(B.y**2+B.z**2)
		)

		t = math.acos(math.sqrt(math.cos(d)**2 - R1)/math.sqrt(1 - R1))

		ABCz = w * (line_AB.Lz + line_BC.Lz).normalized()

		V = B.deviate(ABCz, t)

		E = line_AB.projection(V)
		F = line_BC.projection(V)

		VEa = V.angle_to(E)
		VFa = V.angle_to(F)

		assert(	math.isclose(VEa, VFa, rel_tol=1e-4) )

		BEp = B.angle_to(E) / line_AB.length
		BFp = B.angle_to(F) / line_BC.length

		return Blip.from_vector(E), Blip.from_vector(F), VEa, BEp, BFp

	def turn_4pt(self, A, B, C, D) :

		line_AB = LineTo(A, B)
		line_BC = LineTo(B, C)
		line_CD = LineTo(C, D)

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

	def joint(self, A, B, C, wa, wb, wc, radius_max) :
		line_AB = LineCorridor(B, A, wb, wa)
		line_BC = LineCorridor(B, C, wb, wc)

		E, F, V, VEa, AEp, BFp = line_AB.make_joint(line_BC)





if __name__ == "__main__" :
	u = RouteCut()