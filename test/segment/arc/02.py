#!/usr/bin/env python3

import sys

import numpy as np
import matplotlib.pyplot as plt

from goto.globe.blip import Blip
from goto.globe.segment.arc import SegmentArc
from goto.globe.plot import GlobePlotGps

from cc_pathlib import Path

u = SegmentArc(Blip(0.0, 0.0), Blip(30.0, 0.0), radius=-3.0e6, is_large_arc=True, debug=True)

with GlobePlotGps(Path("02.json")) as gpl :
	gpl.point_map["A"] = u.Ax
	gpl.point_map["B"] = u.Bx
	for i in [0.3, 0.6, 0.9] :
		gpl.point_map[f"P{i}"] = u.position_at(i)
	gpl.add_segment(u)



