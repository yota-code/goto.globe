#!/usr/bin/env python3

import math

import goto.globe

from goto.globe.plot import GlobePlotMpl


p_lst = [
	(0.0, 0.0),
	(10.0, 10.0),
	(100.0, 10.0),
	(100.0, -10.0),
	(10.0, -10.0),
	(0.0, 0.0),
]

helico_pos = goto.globe.Blip(44.0, 5.0)
helico_dir = math.radians(27.0)

Hz = helico_pos.as_vector
Hx, Hy = Hz.oriented_frame(helico_dir)

Gzx = Hz.deflect(Hx, 3_000_000.0 / goto.globe.earth_radius)

# with GlobePlotMpl("test_grid") as plt :
with GlobePloGps("tutu.json") as plt :
	plt.add_point(Hx, "Hx")
	plt.add_point(Hy, "Hy")
	plt.add_point(Hz, "Hz")
	plt.add_point(Gzx, "Gzx", 'r')
	plt.add_line(Hz, Gzx)
