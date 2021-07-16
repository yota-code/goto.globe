#!/usr/bin/env python3

import math

from cc_pathlib import Path

from goto.globe.blip import Blip

from goto.globe.line import LineTo, LineCorridor
from goto.globe.arc import ArcTo

from goto.globe.plot import GlobePlotGps


"""
skeleton: first version of the route, contains GOTO instructions, as well as 3 and 4 points turns. It can be seen as control points of the trajectory
centerline: second version of the route, contains only lines and arcs. It shapes the corridor itself
effective: the last version of the route, with added JOINT, used to compute maximal admissible speeds
"""

earth_radius = 6371008.7714
# openstreetmap earth radius = 6378137.0

def interpolate(x, a, b) :
	return a*(1.0 - x) + b*x

class RouteCut() :
	def __init__(self) :
		# load
		self.r_skeleton = Path("0_skeleton.json").load()
		self.plot(self.r_skeleton, Path("0_skeleton.plot.json"))

		# apply first pass
		self.r_centerline = self.pass_1(self.r_skeleton)
		Path("1_centerline.json").save(self.r_centerline)
		self.plot(self.r_centerline, Path("1_centerline.plot.json"))

		self.r_effective = self.pass_2(self.r_centerline)
		Path("2_effective.json").save(self.r_centerline)
		self.plot(self.r_effective, Path("2_effective.plot.json"))

		self.plot_corridor( Path("3_corridor.plot.json") )

	def plot_corridor(self, route_pth) :
		p_prev = None
		r_lst = self.r_centerline
		with GlobePlotGps(route_pth) as plt :
			for i, line in enumerate(r_lst) :
				verb, lat, lon, radius, alt, spd, width = line
				p_curr = Blip(lat, lon).as_vector
				plt.add_circle(p_curr, width / earth_radius)
				if p_prev != None :
					if radius == 0.0 :
						line_AB = LineCorridor(p_prev, p_curr, r_lst[i-1][6] / earth_radius, width / earth_radius)
						plt.add_line(line_AB.side_point(0.0, -1), line_AB.side_point(1.0, -1))
						plt.add_line(line_AB.side_point(0.0, 1), line_AB.side_point(1.0, 1))
					else :
						plt.add_arc(p_prev, p_curr, radius / earth_radius)

				plt.add_point(p_curr, f"{i}.{verb}")
				p_prev = p_curr

	def plot(self, r_lst, route_pth) :
		p_prev = None
		with GlobePlotGps(route_pth) as plt :
			for i, line in enumerate(r_lst) :
				verb, lat, lon, radius, alt, spd, width = line
				p_curr = Blip(lat, lon).as_vector
				# plt.add_circle(p_curr, width / earth_radius)
				if p_prev != None :
					# if radius == 0.0 :
					# 	line_AB = LineCorridor(p_prev, p_curr, r_lst[i-1][6] / earth_radius, width / earth_radius)
					# 	p_lst = [
					# 		line_AB.side_point(0.0, -1), line_AB.side_point(1.0, -1),
					# 		line_AB.side_point(1.0, 1), line_AB.side_point(0.0, 1),
					# 	]
					# 	plt.add_line(line_AB.side_point(0.0, -1), line_AB.side_point(1.0, -1))
					# 	plt.add_line(line_AB.side_point(0.0, 1), line_AB.side_point(1.0, 1))
					if radius == 0.0 :
						plt.add_line(p_prev, p_curr)
					else :
						plt.add_arc(p_prev, p_curr, radius / earth_radius)

				plt.add_point(p_curr, f"{i}.{verb}")
				# print(i, p_prev, type(p_prev))
				# print(i, p_curr, type(p_curr))
				# try :
				p_prev = p_curr
				# except :
				# 	pass
				# print(i, p_prev, type(p_prev))
				# print(i, p_curr, type(p_curr))

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
			verb, lat, lon, radius, alt, spd, width = line
			if verb == 'GOTO' and radius == 0.0 and r_prev[i+1][0] == 'GOTO' and r_prev[i+1][3] == 0.0 :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				E, F, VEa, AEp = self.joint(A, B, C, r_prev[i-1][6], r_prev[i][6], r_prev[i+1][6], 400.0)
				r_next.append(["GOTO", E.lat, E.lon, 0, interpolate(AEp, a_lst[i], a_lst[i+1]), spd, width])
				r_next.append(["JOINT", F.lat, F.lon, VEa * earth_radius, interpolate(AEp, a_lst[i], a_lst[i+1]), spd, width])
			else :
				r_next.append(line)
		return r_next

	def turn_3pt(self, A, B, C, d) :
		line_AB = LineTo(A, B)
		line_BC = LineTo(B, C)

		q = line_AB.Ly.angle_to(line_BC.Ly, B)
		Q = (line_AB.Ly + line_BC.Ly).normalized()

		w = math.copysign(1.0, q)

		R1 = - (A * Q)**2 / (
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

		line_AB = LineCorridor(A, B, wa / earth_radius, wb / earth_radius)
		line_BC = LineCorridor(B, C, wb / earth_radius, wc / earth_radius)

		E, F, V, VEa, AEp, BFp = line_AB.make_joint(line_BC)

		return Blip.from_vector(E), Blip.from_vector(F), VEa, AEp

if __name__ == "__main__" :
	u = RouteCut()