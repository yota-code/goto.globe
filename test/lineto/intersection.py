#!/usr/bin/env python3

import collections
import math

from cc_pathlib import Path

import goto.globe.blip
import goto.globe.lineto

point_set = set()
point_lst = list()
def add_point(point, name) :
	if name not in point_set  :
		u = goto.globe.blip.Blip.from_vector(point)
		point_lst.append({
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [u.lon, u.lat]
			},
			"properties": {
				"name": name
			}
		})
		point_set.add(name)

route_map = collections.defaultdict(list)
def add_to_route(point, point_name, route_name) :
	u = goto.globe.blip.Blip.from_vector(point)
	add_point(point, point_name)
	route_map[route_name].append([u.lon, u.lat])

BOD = goto.globe.blip.Blip(44.828333, -0.715556).as_vector
MXP = goto.globe.blip.Blip(45.63, 8.723056).as_vector
MRS = goto.globe.blip.Blip(43.436667, 5.215).as_vector
LHR = goto.globe.blip.Blip(51.4775, -0.461389).as_vector
LIS = goto.globe.blip.Blip(38.774167, -9.134167).as_vector
RKV = goto.globe.blip.Blip(64.13, -21.940556).as_vector

A = LIS
B = LHR
C = MRS

add_to_route(A, "A", "center")
add_to_route(B, "B", "center")
add_to_route(C, "C", "center")

lineto_AB = goto.globe.lineto.LineTo(A, B)
lineto_BC = goto.globe.lineto.LineTo(B, C)

u = lineto_AB.intersection(lineto_BC)

l12 = lineto_AB.side_point(0.0, 0.02, 1.0)
r12 = lineto_AB.side_point(0.0, 0.02, -1.0)

l21 = lineto_AB.side_point(1.0, 0.01, 1.0)
r21 = lineto_AB.side_point(1.0, 0.01, -1.0)

l23 = lineto_BC.side_point(0.0, 0.01, 1.0)
r23 = lineto_BC.side_point(0.0, 0.01, -1.0)
l32 = lineto_BC.side_point(1.0, 0.03, 1.0)
r32 = lineto_BC.side_point(1.0, 0.03, -1.0)

add_to_route(r12, "R12", "right")
add_to_route(r21, "R21", "right")
add_to_route(r23, "R23", "right")
add_to_route(r32, "R32", "right")

add_to_route(l12, "L12", "left")
add_to_route(l21, "L21", "left")
add_to_route(l23, "L23", "left")
add_to_route(l32, "L32", "left")

lineto_BA = goto.globe.lineto.LineTo(B, A)
q = lineto_BA.Lz.signed_angle_to(lineto_BC.Ly, B)
print(q)
Q = math.copysign(1.0, q) * (lineto_BC.Lz - lineto_BA.Lz ).normalized()

V = B * math.cos(0.2) + Q * math.sin(0.2)
add_point(V, "V")

if q < 0.0 :
	line_12 = goto.globe.lineto.LineTo(r12, r21)
	line_32 = goto.globe.lineto.LineTo(r32, r23)

elif 0.0 < q :
	line_12 = goto.globe.lineto.LineTo(l21, l12)
	line_32 = goto.globe.lineto.LineTo(l32, l23)

I = line_12.intersection(line_32)

add_point(I, "I")
print(goto.globe.blip.Blip.from_vector(I))

add_to_route(B, "B", "bissect")
add_to_route(V, "V", "bissect")

geo_json = {
	"type": "FeatureCollection",
	"features": point_lst + [ {
		"type": "Feature",
		"geometry": {
			"type": "LineString",
			"coordinates": route_map[k]
		},
		"properties": {
			"name": k,
		}
	} for k in route_map ]
}

Path("point.json").save(geo_json)
