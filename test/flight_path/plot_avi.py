#!/usr/bin/env python3

import enum
import re
import sys

from cc_pathlib import Path

avi_rec = re.compile(r'Leg\s+(?P<index>\d+)\s*-\s*(?P<legtype>Gap|Great Circle|Arc|Course)\s*,\s*(?P<is_active>Inactive|Active)\s*,\s*fix\s*(?P<fixname>\w+)\s*(?P<wptlat>[-+]?\d+(\.\d+)?)\s*,\s*(?P<wptlon>[-+]?\d+(\.\d+)?)\s*(((?P<turnway>left|right) arc)\s*,\s*(?P<cntlat>[-+]?\d+(\.\d+)?)\s*,\s*(?P<cntlon>[-+]?\d+(\.\d+)?))?')

pth = Path(sys.argv[1])

turnway_map = {
	"left" : -1,
	"right" : 1
}

active_map = {
	"inactive" : False,
	"active" : True
}

class LegType(enum.Enum) :
	Gap = 0
	Line = 1
	Arc = 2
	Course = 3

legtype_map = {
	"gap" : LegType.Gap,
	"great circle" : LegType.Line,
	"arc" : LegType.Arc,
	"course" : LegType.Course,
}

u_lst = list()
for line in pth.read_text().splitlines() :
	res = avi_rec.match(line)
	if res is None :
		print("ERROR :", line)
		continue
	else :
		index = int(res.group('index'))
		legtype = legtype_map[res.group('legtype').lower()]
		is_active = active_map[res.group('is_active').lower()]
		fixname = res.group('fixname')
		wpt = float(res.group('wptlat')), float(res.group('wptlon'))
		if res.group('turnway') is not None :
			cnt = float(res.group('cntlat')), float(res.group('cntlon'))
			turnway = turnway_map[res.group('turnway').lower()]
		else :
			cnt, turnway = None, None
		u_lst.append([index, legtype, is_active, fixname, wpt, turnway, cnt])

Path("parsed_route.tsv").save(u_lst)

import goto.globe

from goto.globe.plot import GlobePlotGps
from goto.globe.blip import Blip

from goto.globe.segment import *

with GlobePlotGps(Path("gps_plot.json")) as gpl :
	Ax = None
	for index, legtype, is_active, fixname, wpt, turnway, cnt in u_lst :
		Bx = Blip(* wpt)
		gpl.point_map[f"P{index}"] = Bx
		if Ax is not None :
			try :
				if cnt is None :
					obj = SegmentLine(Ax, Bx)
				else :
					Cx = Blip(* cnt)
					gpl.point_map[f"C{index}"] = Cx
					obj = SegmentArc(Ax, Bx, center=Cx, turnway=turnway)
				gpl.add_segment(obj)
			except AssertionError :
				print(index, Ax, Bx)
		Ax = Bx
