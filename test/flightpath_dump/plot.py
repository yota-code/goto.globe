#!/usr/bin/env python3

import enum
import sys

from cc_pathlib import Path

pth = Path(sys.argv[1]).resolve()

assert pth.is_file() and pth.suffix == '.json'

obj = pth.load()

import goto.globe
import goto.globe.segment
from goto.globe.plot import GlobePlotGps

class line_type(enum.IntEnum) :
    UNKNOWN  = 0,
    GEODESIC = 1,
    ARC      = 2,
    COURSE   = 3,
    GAP      = 4,



"""
typedef enum {
    FLIGHT_PATH_LINE_UNKNOWN  = 0,
    FLIGHT_PATH_LINE_GEODESIC = 1,
    FLIGHT_PATH_LINE_ARC      = 2,
    FLIGHT_PATH_LINE_COURSE   = 3,
    FLIGHT_PATH_LINE_GAP      = 4,
} RcmFlightPathLineType_e;

"""

with GlobePlotGps(pth.with_suffix('.map.json')) as plt :
	A = None
	for n, wpt in enumerate(obj["data"]["route"]) :
		if obj["data"]["point_nb"] - 1 == n :
			break
		B = goto.globe.Blip(wpt["waypoint_lat"], wpt["waypoint_lon"])
		altitude = ""
		if wpt["altitude_ceil"] is not None and wpt["altitude_floor"] is not None and wpt["altitude_floor"] == wpt["altitude_ceil"] :
			altitude = f" ({wpt["altitude_floor"]}m)"
		plt.add_point(B, prop={"name": str(n) + altitude})
		if A is not None :
			try :
				s = goto.globe.segment.SegmentLine(A, B)
			except :
				print(f"points confondus en {n}")
				s = None

			p = None
			if wpt["line_type"] == line_type.ARC :
				C = goto.globe.Blip(wpt["arc_lat"], wpt["arc_lon"])
				s = goto.globe.segment.SegmentArc(A, B, center=C)
				p = {'stroke': "#9933FF"}
			elif wpt["line_type"] == line_type.COURSE :
				p = {'stroke': "#FF0000"}
			elif wpt["line_type"] == line_type.GAP :
				p = {'stroke': "#FF9900"}
			elif wpt["line_type"] == line_type.GEODESIC :
				p = {'stroke': "#0000FF"}
			elif wpt["line_type"] == line_type.UNKNOWN :
				p = {'stroke': "#99FFBB"}
			else :
				raise ValueError(f"unknown line_type = {wpt["line_type"]}")
			if s is not None :
				plt.add_segment(s, prop=p)
		A = B
