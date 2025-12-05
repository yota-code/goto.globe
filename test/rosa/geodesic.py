#!/usr/bin/env python3

import goto.globe

import goto.globe.plot

def bam2deg(i) :
	return i  * 360.0 / 4294967296.0

P1 = goto.globe.Blip(43.603664, 5.141878).as_vector
P2 = goto.globe.Blip(44.413333, 8.837500).as_vector

# P1 = goto.globe.Blip(45.0, 0.0).as_vector
# P2 = goto.globe.Blip(45.0, 75.0).as_vector

P3 = (P1 @ P2).normalized()

H = goto.globe.Blip(bam2deg(521878637), bam2deg(68971426)).as_vector

# H = goto.globe.Blip(20.0, 45.0).as_vector
M = H.project_normal(P3).normalized()

dist = M.angle_to(H) * goto.globe.earth_radius

print(dist)

with goto.globe.plot.GlobePlotMpl() as plt :
	plt.add_point(P1, "P1")
	plt.add_point(P2, "P2")
	plt.add_point(H, "H", "b")
	plt.add_point(P3, "P3")
	plt.add_point(M, "M")
	plt.add_line(P1, P2, 'r')

