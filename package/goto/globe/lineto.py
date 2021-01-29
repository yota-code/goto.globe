#!/usr/bin/env python3

import geometrik.threed as g3d

import goto.globe.blip

class LineTo() :

	north = g3d.Vector(0.0, 0.0, 1.0, True)

	def __init__(self, goto.globe.blip.Blip: blip_a, goto.globe.blip.Blip: blip_b) :
		self.blip_a = blip_a # start blip
		self.blip_b = blip_b # end blip

		a = blip_a.to_vector()
		b = blip_b.to_vector()

		# frame, local to A, oriented along AB
		self.x = a
		self.z = (a @ b).normalized() # z is perpendicular to the the trajectory disk
		self.y = (self.z @ self.x).normalized() # y is perpendicular to z and x

		self.angle_ab = a.angle_to(b) # angle between a and b

	def __len__(self) :
		return self.angle_ab

	def progress(self, float: t) :
		v = (
			self.x * math.cos(t * self.angle_ab) +
			self.y * math.sin(t * self.angle_ab)
		)

		return Blip.from_vector(v)

	def status(self, goto.globe.blip.Blip: blip_m) :
		""" blip_m is the real position of the aircraft, maybe not exactly on the the line
		this function returns:
			* p, the blip of the aircraft as projected orthogonally onto the line
			* t, the relative position of p on the line ab (between 0.0 and 1.0)
			* h, the true heading to follow at p in order to stay on the line
			* q, the distance between m and p

		"""

		m = blip_m.to_vector

		# frame, local to P, oriented along AB
		pz = self.z
		py = (pz @ m) # not normalized
		px = (py @ pz) # the projection, not normalized

		p = Blip.from_vector(px)

		t = self.x.signed_angle_to(px, self.z) / self.angle_ab # the progress

		# frame, local to P, oriented to the north
		nx = px
		ny = (nx @ self.north)
		nz = (ny @ nx)

		h = math.degrees( nz.signed_angle_to(py, -1.0 * p) )

		d = m.angle_to(p)

		return p, t, h, d
