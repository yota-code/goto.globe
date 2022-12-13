#!/usr/bin/env python3

import ast

from cc_pathlib import Path

import goto.globe
from goto.globe.blip import Blip

from goto.globe.route.common import *

import goto.globe.segment.turn

def load_value(expr) :
	if isinstance(expr, str) :
		try :
			return ast.literal_eval(expr)
		except (SyntaxError, ValueError) :
			pass
	return expr

cwd = Path('../../../../test/waystack/goaround').resolve()

header = ["verb", "latitude", "longitude", "leg_radius", "is_large_arc", "altitude", "altitude_typ", "speed", "speed_typ", "heading", "heading_typ", "corridor_width", "corridor_height", "terrain_elevation", "geoid_elevation", "leg_attribute", "stop_at"]


def load() :

	w_lst = list()

	w_prev = ['START', 0.0, 0.0, 0.0, False, 0.0, 'UNSPECIFIED', 0.0, 'UNSPECIFIED', 0.0, 'UNSPECIFIED', 5.0, 5.0, 0.0, 0.0, 'FLIGHT', False]
	for w_line in (cwd / '0_skeleton.tsv').load()[1:] :
		w_next = list()
		for i, w in enumerate(w_prev) :
			try :
				m = w_line[i].strip()
			except IndexError :
				m = '*'
			if m == '*' or m == '' :
				m = w
			w_next.append(load_value(m))

		m_line = w_next[:]

		print(m_line)

		m_line[6] = getattr(RouteAltitude, m_line[6])
		m_line[8] = getattr(RouteSpeed, m_line[8])
		m_line[10] = getattr(RouteHeading, m_line[10])
		m_line[15] = getattr(RouteAttr, m_line[15])

		w_lst.append(RoutePiece(* m_line))
		w_prev = w_next

	(cwd / '1_loaded.tsv').write_text('\n'.join(w.to_tsv() for w in w_lst))

	return w_lst

def pass_turn_3(w_prev) :

	print("pass_turn3")
	print(w_prev)

	w_next = list()

	while w_prev :
		w_curr = w_prev.pop(0)
		print(w_curr)
		if w_curr.verb == 'TURN_3PT' :
			A = Blip(w_next[-1].latitude, w_prev[-1].longitude)
			B = Blip(w_curr.latitude, w_curr.longitude)
		
			w_extra = w_prev.pop(0) if w_prev[0].verb == '+' else None	
			w_last = w_prev.pop(0)

			C = Blip(w_last.latitude, w_last.longitude)

			E, F, BEp, BFp, w = goto.globe.segment.turn.turn_3pt(A, B, C, w_curr.leg_radius)

			w_curr.latitude = E.lat
			w_curr.longitude = E.lon
			w_next.append(w_curr)

			w_last.latitude = F.lat
			w_last.longitude = F.lon
			if w_extra is not None :
				w_last
			w_next.append(w_last)
		else :
			w_next.append(w_curr)

	(cwd / '2_turn_3pt.tsv').write_text('\n'.join(w.to_tsv() for w in w_next))

	return w_next

if __name__ == '__main__' :
	w1 = load()
	w2 = pass_turn_3(w1)