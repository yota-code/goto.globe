#!/usr/bin/env python3

import ast
import struct
import zlib

from cc_pathlib import Path

import goto.globe
from goto.globe.blip import Blip

from goto.globe.route.common import *

import goto.globe.segment.turn

def parse_value(expr) :
	if isinstance(expr, str) :
		try :
			return ast.literal_eval(expr)
		except (SyntaxError, ValueError) :
			pass
	return expr

def complete_line(line, header) :
	if len(line) >= len(header) :
		return line[:len(header)]
	else :
		return line + ['',] * (len(header) - len(line))


header_lst = ["verb", "latitude", "longitude", "leg_radius", "is_large_arc", "altitude", "altitude_typ", "speed", "speed_typ", "heading", "heading_typ", "corridor_width", "corridor_height", "terrain_elevation", "geoid_elevation", "leg_attribute", "stop_at"]

'''
	on garde tout sous la forme de listes jusqu'à la dernière étape
	si la ligne commence par '+' on laisse les cases vides vides
	sinon on reporte
'''

class RoutePacker() :
	def __init__(self, cwd) :
		self.cwd = cwd

	def process(self) :
		w0 = self.load()
		w1 = self.unwrap_turn_3pt(w0)
		w2 = self.unwrap_turn_4pt(w1)

		self.w_lst = w2

		self.to_binary()
		self.to_lang_c()
		
	def to_binary(self) :
		header_stt = struct.Struct('ibiI')

		b_lst = list()
		for w_line in self.w_lst :
			print(w_line, type(w_line))
			b_lst.append(w_line.to_binary())

		b_data = b''.join(b_lst)

		(self.cwd / 'route.bin').write_bytes(
			header_stt.pack(len(self.w_lst), self.w_lst[-1].verb == 'LOOP', 0, zlib.crc32(b_data) & 0xffffffff)  + b_data
		)

	def to_lang_c(self) :
		s_lst = [
			'#include "fctext/routehandler_mod.h" TUTU',
			"",
			"#define kt_to_ms(x) (1852.0 * ((double)(x)) / 3600.0)",
			"#define ft_to_m(x) (((double)(x)) * 0.3048)",
			"",
			"rte_route_C rte_main = {",
			f"\t{len(self.w_lst)}, // length",
			f"\t{'true' if self.w_lst[-1].verb == 'LOOP' else 'false'}, // is_circular",
			"\t0, // cursor",
			"\t0, // checksum",
			"\t{",
			"\t\t// latitude, longitude, leg_radius, is_large_arc, altitude, altitude_typ, speed, speed_typ, heading, heading_typ, corridor_width, corridor_height, terrain_elevation, geoid_elevation, leg_attribute, stop_at",
		] + [i.to_lang_c() for i in self.w_lst] + ['\t}\n};',]
		(self.cwd / 'route.c').write_text('\n'.join(s_lst))

	def load(self) :
		w_input = (self.cwd / 'route.tsv').load()

		self.header = w_input.pop(0)

		w_output = list()

		w_prev = ['START', 0.0, 0.0, 0.0, False, 0.0, 'UNSPECIFIED', 0.0, 'UNSPECIFIED', 0.0, 'UNSPECIFIED', 5.0, 5.0, 0.0, 0.0, 'FLIGHT', False]
		while w_input :

			w_next = [parse_value(i) for i in complete_line(w_input.pop(0), header_lst)]

			if w_next[0] == '+' :
				w_piece = RoutePiece(* w_next)
			else :
				w_next = [p if n == '' else n for n, p in zip(w_next, w_prev)]
				w_prev = w_next

				w_piece = RoutePiece(* w_next)

				w_piece.altitude_typ = RouteAltitude[w_piece.altitude_typ]
				w_piece.speed_typ = RouteSpeed[w_piece.speed_typ]
				w_piece.heading_typ = RouteHeading[w_piece.heading_typ]
				w_piece.leg_attribute = RouteAttr[w_piece.leg_attribute]

			w_output.append(w_piece)

		(cwd / '1_loaded.tsv').write_text('\n'.join(['\t'.join(self.header),] + [piece.to_tsv() for piece in w_output]))

		return w_output

	def unwrap_turn_4pt(self, w_input) :

		return w_input[:]

	def unwrap_turn_3pt(self, w_input) :

		w_output = list()

		while w_input :
			w_curr = w_input.pop(0)

			if w_curr.verb == 'TURN_3PT' :
				A = Blip(w_output[-1].latitude, w_output[-1].longitude)
				B = Blip(w_curr.latitude, w_curr.longitude)
			
				w_extra = w_input.pop(0) if w_input[0].verb == '+' else None
				w_last = w_input.pop(0)

				C = Blip(w_last.latitude, w_last.longitude)

				E, F, BEp, BFp, w = goto.globe.segment.turn.turn_3pt(A, B, C, w_curr.leg_radius)

				w_curr.verb = 'GOTO'
				w_curr.latitude = E.lat
				w_curr.longitude = E.lon
				w_output.append(w_curr)

				w_last.latitude = F.lat
				w_last.longitude = F.lon
				
				if w_extra is not None :
					for k in self.header[1:] :
						print(k, w_extra[k])
						if w_extra[k] != '' :
							w_last[k] = w_extra[k]
				w_output.append(w_last)
			else :
				w_output.append(w_curr)

		(cwd / '2_turn_3pt.tsv').write_text('\n'.join(['\t'.join(self.header),] + [piece.to_tsv() for piece in w_output]))

		return w_output

if __name__ == '__main__' :

	cwd = Path('../../../../test/waystack/goaround').resolve()
	u = RoutePacker(cwd).process()
