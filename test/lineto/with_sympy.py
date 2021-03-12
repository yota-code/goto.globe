#!/usr/bin/env python3

import collections
import math
import sys

import sympy

from cc_pathlib import Path

import geometrik.threed as g3d

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

circle_lst = list()
def add_circle(center, radius, name, resolution=256) :
	# center is a unitary vector pointing to the center of the circle
	# radius is a unitary vector pointing to a place on the circle

	# perpendicular to both the center and the radius
	perp = ( radius @ center ).normalized()
	coli = ( center @ perp )

	angl = center.angle_to(radius)
	print(angl)

	point_lst = list()
	for i in range(resolution) :
		t = i * math.tau / resolution
		side = coli * math.cos(t) + perp * math.sin(t)
		radi = center * math.cos( angl ) + side * math.sin( angl )
		u = goto.globe.blip.Blip.from_vector( radi )
		point_lst.append([u.lon, u.lat])
	point_lst.append(point_lst[0])

	circle_lst.append( {
		"type": "Feature",
		"geometry": {
			"type": "LineString",
			"coordinates": point_lst
		},
		"properties": {
			"name": name,
		}
	} )

route_map = collections.defaultdict(list)
def add_to_route(point, point_name, route_name) :
	u = goto.globe.blip.Blip.from_vector(point)
	add_point(point, point_name)
	route_map[route_name].append([u.lon, u.lat])


# numeric part

BOD = goto.globe.blip.Blip(44.828333, -0.715556).as_vector
MXP = goto.globe.blip.Blip(45.63, 8.723056).as_vector
MRS = goto.globe.blip.Blip(43.436667, 5.215).as_vector
LHR = goto.globe.blip.Blip(51.4775, -0.461389).as_vector
LIS = goto.globe.blip.Blip(38.774167, -9.134167).as_vector
RKV = goto.globe.blip.Blip(64.13, -21.940556).as_vector

A, B, C = LIS, LHR, MRS

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
Q = math.copysign(1.0, q) * (lineto_BC.Lz - lineto_BA.Lz ).normalized()
# add_point(Q, "Q")
t = 0.0475942
V = B * math.cos(t) + Q * math.sin(t)
add_point(V, "V")

v12, null, null, a12 = lineto_AB.status(V)
add_point(v12, "v12")
add_circle(V, v12, 'v12')

v23, null, null, a23 = lineto_BC.status(V)
add_point(v23, "v23")
add_circle(V, v23, 'v23')

if q < 0.0 :
	line_12 = goto.globe.lineto.LineTo(r12, r21)
	line_32 = goto.globe.lineto.LineTo(r32, r23)
elif 0.0 < q :
	line_12 = goto.globe.lineto.LineTo(l21, l12)
	line_32 = goto.globe.lineto.LineTo(l32, l23)
else :
	raise ValueError
I = line_12.intersection(line_32)

add_point(I, "I")
print(goto.globe.blip.Blip.from_vector(I))

add_to_route(B, "B", "bissect")
add_to_route(V, "V", "bissect")

add_circle(V, I, 'test')

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
	} for k in route_map ] + circle_lst
}

Path("point.json").save(geo_json)



sys.exit(0)

val = {
	'A_x': A.x, 'A_y': A.y, 'A_z': A.z,
	'B_x': B.x, 'B_y': B.y, 'B_z': B.z,
	'I_x': I.x, 'I_y': I.y, 'I_z': I.z,
	'Q_x': Q.x, 'Q_y': Q.y, 'Q_z': Q.z,
}

# symbolic part

t = sympy.symbols('t')

A = g3d.Vector( * sympy.symbols('A_x A_y A_z'), True )
B = g3d.Vector( * sympy.symbols('B_x B_y B_z'), True )
C = g3d.Vector( * sympy.symbols('C_x C_y C_z'), True )

I = g3d.Vector( * sympy.symbols('I_x I_y I_z'), True )
Q = g3d.Vector( * sympy.symbols('Q_x Q_y Q_z'), True )

V = B * sympy.cos(t) + Q * sympy.sin(t)

Pab_Z = g3d.Vector( * sympy.symbols('PabZx PabZy PabZz'), True )
Pab_Y = (Pab_Z @ V).normalized()
Pab_X = (Pab_Y @ Pab_Z)

left_angle = (Pab_X * V)
center_angle = (I * V)

