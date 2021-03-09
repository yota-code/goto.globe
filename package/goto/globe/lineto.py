#!/usr/bin/env python3

import math
import sympy

import geometrik.threed as g3d

# import goto.globe.blip

class LineTo() :

	""" plus de blip ici !!! que des vecteurs unitaires !!! """

	north = g3d.Vector(0.0, 0.0, 1.0, True)

	def __init__(self, a : g3d.Vector, b : g3d.Vector) :

		self.La = a.normalized()
		self.Lb = b.normalized()

		# frame, local to A, oriented along AB
		self.Lx = self.La
		self.Lz = (self.La @ self.Lb).normalized() # z is perpendicular to the the trajectory disk
		self.Ly = (self.Lz @ self.Lx) # y is perpendicular to z and x

		self.angle_ab = a.angle_to(b) # angle/distance between a and b

	@staticmethod
	def new_symbolic(a, b) :
		u = LineTo( g3d.Vector(0.0, 0.0, 1.0, True), g3d.Vector(1.0, 0.0, 0.0, True) )
		
		u.La = g3d.Vector( * sympy.symbols(f'{a}_x {a}_y {a}_z') )
		u.Lb = g3d.Vector( * sympy.symbols(f'{a}_x {a}_y {a}_z') )

		u.Lx = g3d.Vector( * sympy.symbols(f'{a}{b}^Lx_x {a}{b}^Lx_y {a}{b}^Lx_z') )
		u.Ly = g3d.Vector( * sympy.symbols(f'{a}{b}^Ly_x {a}{b}^Ly_y {a}{b}^Ly_z') )
		u.Lz = g3d.Vector( * sympy.symbols(f'{a}{b}^Lz_x {a}{b}^Lz_y {a}{b}^Lz_z') )

		u.angle_ab = sympy.symbols(f'{a}{b}^d')

		return u

	def __len__(self) :
		return self.angle_ab

	def intersection(self, other) :
		return (self.Lz @ other.Lz).normalized()

	def side_point(self, t, d, w) :
		return self.progress(t) * math.cos( d ) + w * self.Lz * math.sin( d )

	def progress(self, t : float) :
		return (
			self.Lx * math.cos(t * self.angle_ab) +
			self.Ly * math.sin(t * self.angle_ab)
		)

	def status(self, m : g3d.Vector) :
		""" blip_m is the real position of the aircraft, maybe not exactly on the the line
		this function returns:
			* p, the blip of the aircraft as projected orthogonally onto the line
			* t, the relative position of p on the line ab (between 0.0 and 1.0)
			* h, the true heading to follow at p in order to stay on the line
			* q, the distance between m and p
		"""

		Lx, Ly, Lz = self.Lx, self.Ly, self.Lz

		# frame, local to P, oriented along AB
		Pz = Lz
		Py = (Pz @ m).normalized()
		Px = (Py @ Pz) # the projection, not normalized

		t = Lx.signed_angle_to(Px, Lz) / self.angle_ab # the progress

		# frame, local to P, oriented to the north
		Nx = Px
		Ny = (self.north @ Nx).normalized()
		Nz = (Nx @ Ny)

		h = math.degrees( Py.signed_angle_to(Nz, Px) )

		d = m.angle_to(Px)

		return Px, t, h, d
