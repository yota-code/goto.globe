#!/usr/bin/env python3

import math
import collections
from os import wait4

from cc_pathlib import Path

from goto.globe.blip import Blip

from goto.globe.line import LineSegment, LineCorridor
from goto.globe.arc import ArcSegment, ArcCorridor

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

WskPt = collections.namedtuple('WskPt', ['verb', 'pos', 'radius', 'alt', 'spd', 'width'])

def read_wskpt(verb, lat, lon, radius, alt, spd, width) :
	return WskPt(verb, Blip(lat, lon).as_vector, radius, alt, spd, width)

class RouteCut() :
	def __init__(self, lat_orig=0.0, lon_orig=0.0) :
		# load

		centerline_pth = Path("1_centerline.json")
		effective_pth = Path("2_effective.json")

		if Path("0_skeleton.json").is_file() :
			self.r_skeleton = Path("0_skeleton.json").load()
			for line in self.r_skeleton :
				line[1] += lat_orig
				line[2] += lon_orig
			self.plot_segment(self.r_skeleton, Path("0_skeleton.plot.json"))

			# apply first pass
			self.r_centerline = self.pass_1(self.r_skeleton)
			Path("1_centerline.json").save(self.r_centerline)
			self.plot_segment(self.r_centerline, Path("1_centerline.plot.json"))

			self.plot_corridor( Path("3_corridor.plot.json") )

		if centerline_pth.is_file() :
			self.r_effective = self.pass_2(self.r_centerline)
			Path("2_effective.json").save(self.r_centerline)
		else :
			self.r_effective = effective_pth.load()
		self.plot_segment(self.r_effective, Path("2_effective.plot.json"))

		self.to_wsk_qnd_point(self.r_effective)

	def plot_corridor(self, route_pth) :
		p_prev = None
		with GlobePlotGps(route_pth) as plt :
			for i, line in enumerate(self.r_centerline) :
				p_curr = read_wskpt(* line)
				if p_prev != None :
					if p_curr.radius == 0.0 :
						s = LineCorridor(p_prev.pos, p_curr.pos, p_prev.width / earth_radius, p_curr.width / earth_radius)
					else :
						s = ArcCorridor(p_prev.pos, p_curr.pos, p_curr.radius / earth_radius, p_prev.width / earth_radius, p_curr.width / earth_radius)
					plt.add_border(s)
				plt.add_point(p_curr.pos, f"{i}.{p_curr.verb}")
				p_prev = p_curr

	def plot_segment(self, r_lst, route_pth) :
		p_prev = None
		with GlobePlotGps(route_pth) as plt :
			for i, line in enumerate(r_lst) :
				p_curr = read_wskpt(* line)
				if p_prev != None :
					if p_curr.radius == 0.0 or p_curr.verb not in ['GOTO', 'JOINT'] :
						s = LineCorridor(p_prev.pos, p_curr.pos, p_prev.width / earth_radius, p_curr.width / earth_radius)
					else :
						s = ArcCorridor(p_prev.pos, p_curr.pos, p_curr.radius / earth_radius, p_prev.width / earth_radius, p_curr.width / earth_radius)
					plt.add_segment(s)
				plt.add_point(p_curr.pos, f"{i}.{p_curr.verb}")
				p_prev = p_curr

	def pass_1(self, r_prev) :
		r_next = list()
		a_lst = [ line[4] for line in r_prev ]

		for i, line in enumerate(r_prev) :
			print("pass_1 ::", line)
			verb, lat, lon, radius, alt, spd, width = line
			if verb == '__TURN_3PT__' :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				r = radius / earth_radius
				E, F, BEp, BFp, w = self.turn_3pt(A, B, C, r)
				r_next.append(["GOTO", E.lat, E.lon, 0, interpolate(BEp, a_lst[i-1], a_lst[i]), spd, width])
				r_next.append(["GOTO", F.lat, F.lon, w*radius, interpolate(BFp, a_lst[i], a_lst[i+1]), spd, width])
				print(r_next[-2:])
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
				pass # this point was treated previously with __TURN_4PT_1__
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

		print("d =", d)
		line_BA = LineSegment(B, A)
		line_BC = LineSegment(B, C)

		q = line_BA.Ly.angle_to(line_BC.Ly, B)
		Q = (line_BA.Ly + line_BC.Ly).normalized()

		w = math.copysign(1.0, q)
		print("q = ", q)
		print("w = ", w)

		R1 = - (A * Q)**2 / (
		    A.y**2*(-1+B.y**2) +
		    2*A.x*A.z*B.x*B.z +
		    2*A.y*B.y*(A.x*B.x+A.z*B.z) +
		    A.z**2*(-1+B.z**2) -
		    A.x**2*(B.y**2+B.z**2)
		)

		t = math.acos(math.sqrt(math.cos(d)**2 - R1) / math.sqrt(1 - R1))

		V = B.deviate(Q, t)

		E = line_BA.projection(V)
		F = line_BC.projection(V)

		VEa = V.angle_to(E)
		VFa = V.angle_to(F)

		try :
			assert(	math.isclose(VEa, VFa, rel_tol=1e-4) )
			assert(	math.isclose(VEa, d, rel_tol=1e-4) )
		except AssertionError :
			print(VEa, VFa, d)
			raise

		BEp = B.angle_to(E) / line_BA.length
		BFp = B.angle_to(F) / line_BC.length

		return Blip.from_vector(E), Blip.from_vector(F), BEp, BFp, w

	def turn_4pt(self, A, B, C, D) :

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

	def joint(self, A, B, C, wa, wb, wc, radius_max) :

		line_AB = LineCorridor(A, B, wa / earth_radius, wb / earth_radius)
		line_BC = LineCorridor(B, C, wb / earth_radius, wc / earth_radius)

		E, F, V, VEa, AEp, BFp = line_AB.make_joint(line_BC)

		return Blip.from_vector(E), Blip.from_vector(F), VEa, AEp

	def to_wsk_qnd_point(self, r_lst) :
		w_lst = [
			"wsk_qnd_point_T wsk_qnd_line_arr[wsk_qnd_line_LEN] = {",
		]
		for verb, lat, lon, radius, alt, spd, width in r_lst :
			print(verb, lat, lon, radius, alt, spd, width)
			verb_id = 0 if radius == 0.0 else 1
			w_lst.append('\t' + str([verb_id, [lat, lon], radius, alt, spd]).replace('[', '{').replace(']', '}') + ',')
		w_lst.append("};")
		w_txt = '\n'.join(w_lst)
		Path("4_wsk_qnd.c").write_text(w_txt)

if __name__ == "__main__" :
	u = RouteCut(43.436667, 5.215)