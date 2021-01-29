#!/usr/bin/env python3

import math

from cc_pathlib import Path

import goto.globe.aircraft
import goto.globe.common

goto.globe.common.earth_radius = 1000.0 / math.pi

u = goto.globe.aircraft.Aircraft(0.0, 0.0, 0.0, math.radians(90.0), 1.0, 0.0)

for i in range(100) :
	u.step()
	u.dump(Path("go_east.tsv"))
