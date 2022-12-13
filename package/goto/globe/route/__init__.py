#!/usr/bin/env python3

import collections
import enum
import math
import struct
import zlib

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

"""
définition du skeleton :

1. type of waypoint :
	START
	STOP
	__TURN_3PT__
	__TURN_4PT_1__
	__TURN_4PT_2__
	GOTO
2. latitude
3. longitude
4. altitude
	



"""

# earth_radius = 6371008.7714
earth_radius = 6371007.181
# openstreetmap earth radius = 6378137.0

def interpolate(x, a, b) :
	return a*(1.0 - x) + b*x

WskPt = collections.namedtuple('WskPt', ['verb', 'pos', 'radius', 'is_large_arc', 'alt', 'spd', 'width', 'attr'])

attr_enum = ['UNSPECIFIED', 'STOP', 'PARKING', 'TAXIWAY', 'GOAROUND', 'FLIGHT', 'DESCEND']


def read_wskpt(verb, lat, lon, radius, is_large_arc, alt, spd, width, attr) :
	return WskPt(verb, Blip(lat, lon).as_vector, radius, is_large_arc, alt, spd, width, attr)

def kt_to_ms(x) :
	return (1852.0 * (x) / 3600.0)

def ft_to_m(x) :
	return ((x) * 0.3048)

class RoutePrepare() :
	def __init__(self, lat_orig=0.0, lon_orig=0.0) :
		# load

		centerline_pth = Path("1_centerline.json")
		effective_pth = Path("2_effective.json")

		if Path("0_skeleton.json").is_file() :
			# if not Path("2_effective.json").is_file() :
			self.r_skeleton = Path("0_skeleton.json").load()
			for line in self.r_skeleton :
				line[1] += lat_orig
				line[2] += lon_orig
			self.plot_segment(self.r_skeleton, Path("0_skeleton.plot.json"))

			# apply first pass
			self.r_centerline = self.pass_1(self.r_skeleton)
			Path("1_centerline.json").save(self.r_centerline)
			self.plot_segment(self.r_centerline, Path("1_centerline.plot.json"))

			self.plot_corridor(Path("3_corridor.plot.json"))

			self.r_effective = self.pass_2(self.r_centerline)
			Path("2_effective.json").save(self.r_effective)
			# else :
			#	print("\x1b[31mcached !\x1b[0m")
			#	self.r_effective = Path("2_effective.json").load()

			self.plot_segment(self.r_effective, Path("2_effective.plot.json"))

			self.to_lang_c(self.r_effective)
			self.to_binary(self.r_effective)
			self.to_lua(self.r_effective)

			#self.plot_route(self.r_centerline, Path("1_route.txt"))

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
					print(p_curr.radius, p_curr.verb)
					if p_curr.radius == 0.0 or p_curr.verb not in ['GOTO', 'JOINT'] :
						s = LineCorridor(p_prev.pos, p_curr.pos, p_prev.width / earth_radius, p_curr.width / earth_radius)
					else :
						s = ArcCorridor(p_prev.pos, p_curr.pos, p_curr.radius / earth_radius, p_prev.width / earth_radius, p_curr.width / earth_radius)
					plt.add_segment(s)
				plt.add_point(p_curr.pos, f"{i}.{p_curr.verb}")
				p_prev = p_curr

		# route_pth.write_text(route_txt)

	def pass_1(self, r_prev) :
		r_next = list()
		a_lst = [ line[4] for line in r_prev ]

		for i, line in enumerate(r_prev) :
			print("pass_1 ::", line)
			verb, lat, lon, radius, is_large_arc, alt, spd, width, attr = line
			if verb == '__TURN_3PT__' :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				r = radius / earth_radius
				E, F, BEp, BFp, w = self.turn_3pt(A, B, C, r)
				# y a une erreur
				# r_next.append(["GOTO", E.lat, E.lon, 0, interpolate(BEp, a_lst[i-1], a_lst[i]), spd, width])
				# r_next.append(["GOTO", F.lat, F.lon, w*radius, interpolate(BFp, a_lst[i], a_lst[i+1]), spd, width])
				r_next.append(["GOTO", E.lat, E.lon, 0, False, alt, spd, width, attr])
				r_next.append(["GOTO", F.lat, F.lon, w*radius, is_large_arc, alt, spd, width, attr])
				print(r_next[-2:])
			elif verb == '__TURN_4PT_1__' :
				A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
				B = Blip(lat, lon).as_vector
				C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
				D = Blip(r_prev[i+2][1], r_prev[i+2][2]).as_vector
				E, F, G, VFa, AEp, BFp, CGp = self.turn_4pt(A, B, C, D)
				# r_next.append(["GOTO", E.lat, E.lon, 0.0, interpolate(AEp, a_lst[i-1], a_lst[i+1]), spd, width])
				# r_next.append(["GOTO", F.lat, F.lon, VFa * earth_radius, interpolate(BFp, a_lst[i], a_lst[i+1]), spd, width])
				# r_next.append(["GOTO", G.lat, G.lon, VFa * earth_radius, interpolate(CGp, a_lst[i+1], a_lst[i+2]), spd, width])
				r_next.append(["GOTO", E.lat, E.lon, 0.0, False, alt, spd, width, attr])
				r_next.append(["GOTO", F.lat, F.lon, VFa * earth_radius, False, alt, spd, width, attr])
				r_next.append(["GOTO", G.lat, G.lon, VFa * earth_radius, False, alt, spd, width, attr])
			elif verb == '__TURN_4PT_2__' :
				pass # this point was treated previously with __TURN_4PT_1__
			elif verb == '__LOOP__' :
				pass # we are looping, the last point is not used
			else :
				r_next.append(line)
		
		return r_next

	def pass_2(self, r_prev) :
		r_next = list()
		a_lst = [ line[4] for line in r_prev ]
		for i, line in enumerate(r_prev) :
			verb, lat, lon, radius, is_large_arc, alt, spd, width, attr = line
			# TODO: le joint automatique est fragile... dans le cas où les segments sont alignés, il plante
			# if verb == 'GOTO' and radius == 0.0 and r_prev[i+1][0] == 'GOTO' and r_prev[i+1][3] == 0.0 :
			# 	A = Blip(r_prev[i-1][1], r_prev[i-1][2]).as_vector
			# 	B = Blip(lat, lon).as_vector
			# 	C = Blip(r_prev[i+1][1], r_prev[i+1][2]).as_vector
			# 	E, F, VEa, AEp = self.joint(A, B, C, r_prev[i-1][6], r_prev[i][6], r_prev[i+1][6], 400.0)
			# 	if abs(VEa) < 0.5 :
			# 		# r_next.append(["GOTO", E.lat, E.lon, 0, interpolate(AEp, a_lst[i], a_lst[i+1]), spd, width])
			# 		# r_next.append(["JOINT", F.lat, F.lon, VEa * earth_radius, interpolate(AEp, a_lst[i], a_lst[i+1]), spd, width])
			# 		r_next.append(["GOTO", E.lat, E.lon, 0, False, alt, spd, width])
			# 		r_next.append(["JOINT", F.lat, F.lon, VEa * earth_radius, False, alt, spd, width])
			# 	else :
			# 		r_next.append(line)
			# else :
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

	def to_lang_c(self, r_lst) :
		
		w_lst = [
			'#include "fctext/routehandler_mod.h" TUTU',
			"",
			"#define kt_to_ms(x) (1852.0 * ((double)(x)) / 3600.0)",
			"#define ft_to_m(x) (((double)(x)) * 0.3048)",
			"",
			"rte_route_C rte_main = {",
			f"\t{len(r_lst)}, // length",
			"\ttrue, // is_circular",
			"\t0, // cursor",
			"\t0, // checksum",
			"\t{",
			"\t\t// (lat, lon), leg_radius, is_leg_large_arc, altitude, altitude_mode, speed, speed_mode, heading, heading_mode, corridor_width, corridor_height, ground_elevation, padding",
		]
		for verb, lat, lon, radius, is_large_arc, alt, spd, width, attr in r_lst :
			print(">>>", verb, lat, lon, radius, is_large_arc, alt, spd, width)
			w_lst.append(f"\t\t{{ {{{lat}, {lon}}}, {radius}, {is_large_arc}, ft_to_m({alt}), {1 if alt < 300 else 2}, kt_to_ms({spd}), {1 if spd < 45 else 2}, 0.0, 0, {width}, {width}, {37 if alt < 100 else 13}, -1 }},")
		w_lst.append("\t}\n};")
		w_txt = '\n'.join(w_lst)
		Path("route.c").write_text(w_txt)

	def to_binary(self, r_lst, total_len=256) :
		"""
			typedef struct {
				UpmvBlip_S point;
				float leg_radius;
				bool is_leg_large_arc;
				float altitude;
				UpmvRouteAltitude_E altitude_typ;
				float speed;
				UpmvRouteSpeed_E speed_typ;
				float heading;
				UpmvRouteHeading_E heading_typ;
				float corridor_width;
				float corridor_height;
				float terrain_elevation;
				float geoid_elevation;
				UpmvRouteAttr_E attr;
				bool stop_at;
			} UpmvRoutePiece_S;
		"""

		header_sti = struct.Struct('ibiI')
		waypoint_sti = struct.Struct('ddfbfifififfffii')


		b_lst = list()
		for verb, lat, lon, radius, is_large_arc, alt, spd, width, attr in r_lst :
			b_lst.append(waypoint_sti.pack(
				lat,
				lon,
				radius,
				is_large_arc,
				ft_to_m(alt),
				1 if alt < 300 else 2,
				kt_to_ms(spd),
				1 if spd < 45 else 2,
				0.0, 0, width, width, 13.0, 17.0,
				attr_enum.index(attr), spd == 0.0
			))
		for i in range(len(r_lst), total_len) :
			b_lst.append(waypoint_sti.pack(* ([0,] * 16)))
		
		b_data = b''.join(b_lst)

		print(waypoint_sti.size)

		Path("route.bin").write_bytes( header_sti.pack(len(r_lst), False, 0, zlib.crc32(b_data) & 0xffffffff)  + b_data)
	
	def to_lua(self, r_lst) :
		p_lst = list()
		for i, line in enumerate(r_lst) :
			p_lst.append( f"		{{{i+3}}}," )
		p_txt = '\n'.join(p_lst)
		w_lst = list()
		for i, line in enumerate(r_lst) :
			verb, lat, lon, radius, is_large_arc, alt, spd, width, attr = line
			w_lst.append(f"""	-- Table: {{{i}}}
	{{
		["alt"]={alt},
		["lat"]={lat},
		["lon"]={lon},
		["corridor_radius"]={width},
		["leg_radius"]={radius},
		["large_arc"]={1 if is_large_arc else 0},
		["name"]="{i}",
		["speed"]={spd},
	}},""")
		w_txt = '\n'.join(w_lst)

		route_txt = f"""return {{
	-- Table: {{1}}
	{{
		{{2}},
	}},
	-- Table: {{2}}
	{{
{p_txt}
	}},
{w_txt}
}}
"""
		Path("route.lua").save('\n'.join(w_lst))
