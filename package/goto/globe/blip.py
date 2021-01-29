#!/usr/bin/env python3

import math

import geometrik.threed as g3d

class Blip() :
	""" a blip is a point on the unit sphere (no orientation, no altitude, no earth radius, just a dot on the map) """

	def __init__(self, lat, lon) :
		# lat and lon are in degrees
		self.lat, self.lon = lat, lon

	def __repr__(self) :
		return f'Blip({self.lat}, {self.lon}) / {self.to_vector}'

	@staticmethod
	def from_vector(v) :
		if not v._is_unit :
			v = v.normalized()
			
		theta = math.acos(v.z)
		phi = math.atan2(v.y, v.x)

		lat = math.degrees( math.pi/2 - theta )
		lon = math.degrees( phi )
		
		return Blip(lat, lon)

	def to_vector(self) :
		theta =  (math.pi / 2) - math.radians( self.lat )
		phi = math.radians( self.lon )

		sin_theta, cos_theta = math.sin(theta), math.cos(theta)
		sin_phi, cos_phi = math.sin(phi), math.cos(phi)

		v = g3d.Vector(
			sin_theta * cos_phi,
			sin_theta * sin_phi,
			cos_theta, True
		)

		# the vector must be on the unit sphere
		assert( math.isclose(v.norm, 1.0) )

		return v
