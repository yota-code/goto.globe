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

	def projection(self, Mx: g3d.Vector) :
		""" return Px, Py Pz where Px is the projection of Mx on the Line
		"""

		Pz = self.Lz
		Py = (Pz @ Mx).normalized()
		Px = (Py @ Pz) # the projection, not normalized

		return Px, Py, Pz


	def status(self, Mx : g3d.Vector) :
		""" blip_m is the real position of the aircraft, maybe not exactly on the the line
		this function returns:
			* p, the blip of the aircraft as projected orthogonally onto the line
			* t, the relative position of p on the line ab (between 0.0 and 1.0)
			* h, the true heading to follow at p in order to stay on the line
			* q, the distance between m and p
		"""

		Lx, Ly, Lz = self.Lx, self.Ly, self.Lz

		print(f"Lx = {Lx}")
		print(f"Ly = {Ly}")
		print(f"Lz = {Lz}")

		# frame, local to P, oriented along AB

		Pz = Lz
		Py = (Pz @ Mx).normalized()
		Px = (Py @ Pz) # the projection, not normalized

		print(f"Px = {Px}")
		print(f"Py = {Py}")
		print(f"Pz = {Pz}")

		t = Lx.signed_angle_to(Px, Lz) / self.angle_ab # the progress

		# frame, local to P, oriented to the north
		Nx = Px
		Ny = (self.north @ Nx).normalized()
		Nz = (Nx @ Ny)

		h = math.degrees( Py.signed_angle_to(Nz, Px) )

		d = Mx.angle_to(Px)

		return Px, t, h, d


class LineCorridor(LineTo) :

	def __init__(self, a : g3d.Vector, b : g3d.Vector, a_width: float, b_width: float) :

		self.La = a.normalized()
		self.Lb = b.normalized()

		# frame, local to A, oriented along AB
		self.Lx = self.La
		self.Lz = (self.La @ self.Lb).normalized() # z is perpendicular to the the trajectory disk
		self.Ly = (self.Lz @ self.Lx) # y is perpendicular to z and x

		self.angle_ab = a.angle_to(b) # angle/distance between a and b

		self.a_width = a_width
		self.b_width = b_width
		
	def side_point(self, t, w) :
		
		t = max(0.0, min(1.0, t))
		d = (self.b_width - self.a_width) * t + self.a_width
		return self.progress(t) * math.cos(d) + w * self.Lz * math.sin(d)

	def make_joint(self, other) :
		""" B->A et B->C """

		A, B = self.Lb, self.La

		q = self.Ly.signed_angle_to(other.Ly, B)
		Q = (self.Ly + other.Ly).normalized()

		w = math.copysign(1.0, q)

		point_ba = self.side_point(0.0, w)
		point_ab = self.side_point(1.0, w)
		point_bc = other.side_point(1.0, -w)
		point_cb = other.side_point(0.0, -w)

		side_ab = LineTo(point_ab, point_ba)
		side_bc = LineTo(point_bc, point_cb)

		I = side_ab.intersection(side_bc)

		P1 = I * Q
		P2 = I * B
		R1 = -(A * Q)**2 / (
		    A.y**2*(-1+B.y**2) +
		    2*A.x*A.z*B.x*B.z +
		    2*A.y*B.y*(A.x*B.x+A.z*B.z) +
		    A.z**2*(-1+B.z**2) -
		    A.x**2*(B.y**2+B.z**2)
		)

		t = math.acos(math.sqrt( (P1**2 - R1)**2 / (
		    P1**4 + P1**2*(1 + P2**2 - 2*R1) +
		    R1*(-1 + P2**2 + R1) +
		    2*math.sqrt(P1**2*P2**2*(P1**2 + (-1 + P2**2)*R1))
		)))

		V = B * math.cos(t) + Q * math.sin(t)

		E, null, null = self.projection(V)
		F, null, null = other.projection(V)

		return E, F, V
