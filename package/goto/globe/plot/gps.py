#!/usr/bin/env python3

import math

import numpy as np

from cc_pathlib import Path

import geometrik.threed as g3d
from goto.globe import Blip

from .base import GlobePlot__base__

class GlobePlotGps(GlobePlot__base__) :

	def __init__(self, pth) :
		self.pth = pth

		self.line_lst = list()
		self.point_map = dict()
		self.polygon_lst = list()

	def __enter__(self) :
		return self

	def __exit__(self, exc_type, exc_value, traceback) :
		point_lst = list()
		for name, u in self.point_map.items() :
			b = Blip.from_vector(u)
			point_lst.append({
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [b.lon, b.lat]
				},
				"properties": {
					"name": name
				}
			})

		line_lst = list()
		for line in self.line_lst :
			p_lst = list()
			for p in line :
				u = Blip.from_vector(p)
				p_lst.append([u.lon, u.lat])
			line_lst.append({
				"type": "Feature",
				"geometry": {
					"type": "LineString",
					"coordinates": p_lst
				},
			})

		polygon_lst = list()
		for line in self.polygon_lst :
			p_lst = list()
			for p in line :
				u = Blip.from_vector(p)
				p_lst.append([u.lon, u.lat])
			polygon_lst.append({
				"type": "Feature",
				"geometry": {
					"type": "Polygon",
					"coordinates": [p_lst,]
				},
			})	

		self.pth.save({
			"type": "FeatureCollection",
			"features": point_lst + line_lst
		})

	def add_point(self, Ax, name, color=None) :
		self.point_map[name] = Ax

	def add_line(self, Ax, Bx) :
		self.line_lst.append( GlobePlot__base__.add_line(self, Ax, Bx) )

	def add_arc(self, Ax, Bx, radius=0.0) :
		self.line_lst.append( GlobePlot__base__.add_arc(self, Ax, Bx, radius) )

	def add_circle(self, Cx, Px) :
		self.line_lst.append( GlobePlot__base__.add_circle(self, Cx, Px) )

	def add_segment(self, u) :
		self.line_lst.append( GlobePlot__base__.add_segment(self, u) )

	def add_border(self, u) :
		self.line_lst.append( GlobePlot__base__.add_border(self, u) )
