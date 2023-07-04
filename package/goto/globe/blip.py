#!/usr/bin/env python3

import math
import numbers
import sympy

import geometrik.threed as g3d

class Blip() :
	""" a blip is a point on the unit sphere (no orientation, no altitude, no earth radius, just a dot on the map) """

	def __init__(self, lat, lon, is_symbolic=False) :
		# lat and lon are in degrees
		self.lat, self.lon = lat, lon

		self._is_symbolic = self.is_symbolic
		self.m = sympy if is_symbolic else math

	@property
	def is_symbolic(self) :
		return not all(isinstance(i, numbers.Number) for i in self.as_tuple)

	@property
	def as_tuple(self) :
		return self.lat, self.lon


	def __repr__(self) :
		return f'Blip({self.lat}, {self.lon})'

	def __str__(self) :
		return f'Blip({self.lat}, {self.lon}) / {self.as_vector}'

	@staticmethod
	def from_vector(v) :

		if not v._is_unit :
			v = v.normalized()
			
		theta = math.acos(v.z)
		phi = math.atan2(v.y, v.x)

		lat = math.degrees( math.pi/2 - theta )
		lon = math.degrees( phi )
		
		return Blip(lat, lon)

	@property
	def as_vector(self) :

		theta =  (self.m.pi / 2) - (self.m.pi * self.lat / 180)
		phi = (self.m.pi * self.lon / 180)

		sin_theta, cos_theta = self.m.sin(theta), self.m.cos(theta)
		sin_phi, cos_phi = self.m.sin(phi), self.m.cos(phi)

		v = g3d.Vector(
			sin_theta * cos_phi,
			sin_theta * sin_phi,
			cos_theta, True
		)

		# the vector must be on the unit sphere
		if not math.isclose(v.norm, 1.0) :
			print(f"WARNING: norm={v.norm} ({theta} {phi})")
		# assert( math.isclose(v.norm, 1.0) )

		return v

	@property
	def as_mercator(self) :
		# https://en.wikipedia.org/wiki/Mercator_projection
		x = math.radians( self.lon )
		y = math.log(math.tan(math.pi/4 + math.radians(self.lat)/2))
		return x, y

	@property
	def as_openstreetmap(self, zoom) :
		# https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg
		
		lat_rad = math.radians(self.lat)
		n = 2**zoom
		x = int(n * (self.lon + 180.0) / 360.0)
		y = int(n * (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0)

		return x, y

	def p_gnomic(self, zero, pos) :

		n = g3d.v_north
		z = Blip(lat_zero, lon_zero).as_vector
		x = (n @ z).normalized()
		y = (z @ x)

		d = 0

if __name__ == '__main__' :
	u = Blip(0.0, 0.0)
	print(u)