#!/usr/bin/env python3

import math

import numpy as np

from cc_pathlib import Path

from geometrik.threed import Vector
from goto.globe import Blip

from .base import GlobePlot__base__

class GeoJSON_Point() :
	prop_check = {
		"name": str,
		"marker-color": lambda x: re.compile(r'#[0-9A-Fa-f]{6}').match(x).group(0),
		"marker-size": lambda x: re.compile(r'(small|medium|large)').match(x).group(0),
	}

	def __init__(self, p, name=None, prop=None) :
		self.prop = prop if prop is not None else dict()
		if name is not None :
			self.prop['name'] = name
		self.p = Blip.from_gpoint(p)

	def to_json(self) :
		m = {
			"type": "Feature",
			"geometry" : {
				"type": "Point",
				"coordinates": [self.p.lon, self.p.lat]
			}
		}
		if self.prop :
			m['properties'] = self.prop
		return m

class GeoJSON_LineString() :
	prop_check = {
		"stroke": lambda x: re.compile(r'#[0-9A-Fa-f]{6}').match(x).group(0),
		"stroke-width": lambda x: re.compile(r'#[0-9A-Fa-f]{6}').match(x).group(0),
		"stroke-opacity": float,
	}

	def __init__(self, p_lst, name=None, prop=None) :
		self.prop = prop if prop is not None else dict()
		if name is not None :
			self.prop['name'] = name
		self.p_lst = [Blip.from_gpoint(p) for p in p_lst]

	def to_json(self) :
		m = {
			"type": "Feature",
			"geometry" : {
				"type": "LineString",
				"coordinates": [
					[p.lon, p.lat] for p in self.p_lst
				]
			}
		}
		if self.prop :
			m['properties'] = self.prop
		return m

class GlobePlotGps(GlobePlot__base__) :
	""" this class is meant to help producing a GeoJSON file, as specified in https://datatracker.ietf.org/doc/html/rfc7946
	this GeoJSON can be loaded in visualisation tools like GPXSee.
	"""

	def __init__(self, pth) :
		self.pth = pth

		# self.line_lst = list()
		# self.prop_lst = list()

		# self.point_lst = list()


		# self.point_map = dict()
		# self.polygon_lst = list()

		self.feature_lst = list()

	def __enter__(self) :
		return self

	def __exit__(self, exc_type, exc_value, traceback) :
		self.flush()

	def flush(self) :
		self.pth.save({
			"type": "FeatureCollection",
			"features": [
				f.to_json() for f in self.feature_lst
			]
		}, verbose=True)

		return
		point_lst = list()
		for point, prop in self.point_lst :
			if isinstance(point, g3d.Vector) :
				point = Blip.from_vector(point)
			point_lst.append({
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [point.lon, point.lat]
				},
			})
			if prop :
				point_lst[-1]["properties"] = prop

		line_lst = list()
		for line, prop in self.line_lst :
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
			if prop :
				line_lst[-1]["properties"] = prop

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
		}, verbose=True)

	def add_point(self, Ax, name=None, prop=None) :
		# self.point_map[name] = Ax
		self.feature_lst.append(GeoJSON_Point(Ax, name, prop))

	def add_line(self, A, B, color=None) :
		self.line_lst.append( GlobePlot__base__.add_line(self, A, B) )

	def add_polyline(self, W_lst, p_map=None, close=True) :
		p_lst = [
			W.as_vector for W in W_lst
		]
		if close :
			p_lst.append(p_lst[0])
		self.line_lst.append((p_lst, p_map))

	def add_arc(self, A, B, radius=0.0) :
		self.line_lst.append( GlobePlot__base__.add_arc(self, A, B, radius) )

	def add_circle(self, Cx, Px) :
		self.line_lst.append( GlobePlot__base__.add_circle(self, Cx, Px) )

	def add_segment(self, obj, color=None) :
		self.line_lst.append( GlobePlot__base__.add_segment(self, obj, 2 if obj.radius == 0.0 else 128) )

	def add_border(self, u) :
		self.line_lst.append( GlobePlot__base__.add_border(self, u) )

