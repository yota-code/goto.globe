#!/usr/bin/env python3

import collections

from cc_pathlib import Path

from goto.globe.blip import Blip

WskPt = collections.namedtuple('WskPt', ['verb', 'pos', 'radius', 'alt', 'spd', 'width'])

w_lst = list()
for p in Path("source.json").load() :
	w = WskPt(("GOTO" if len(w_lst) else "START"), Blip(p['lat'], p['lon']), p['leg_radius'], p['alt'], p['speed'], p['corridor_radius'])
	w_lst.append([w.verb, w.pos.lat, w.pos.lon, -w.radius, w.alt, w.spd, w.width])

Path("2_effective.json").save(w_lst, filter_opt={'verbose':True})