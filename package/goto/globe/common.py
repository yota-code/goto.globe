#!/usr/bin/env python3

earth_radius = 6371008.7714
# earth_radius = 1852 * 60 * 360 / math.tau
earth_gravity = 9.80665

from geometrik.threed.vector import Vector

v_null = Vector(0.0, 0.0, 0.0, True)
v_north = Vector(0.0, 0.0, 1.0, True)
v_east = Vector(0.0, 1.0, 0.0, True)
v_down = v_north @ v_east
v_up = v_east @ v_north
