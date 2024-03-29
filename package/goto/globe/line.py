#!/usr/bin/env python3

import math
from os import P_WAIT
import sympy

from cc_pathlib import Path

import geometrik.threed as g3d

# import goto.globe.blip
# priorité à segment

class LineSegment() :

	""" plus de blip ici !!! que des vecteurs unitaires !!! """

	north = g3d.Vector(0.0, 0.0, 1.0, True)

	def __init__(self, A: g3d.Vector, B: g3d.Vector) :

		self.A = A.normalized()
		self.B = B.normalized()

		# frame, local to A, oriented along AB
		self.Lx = self.A
		self.Lz = (self.A @ self.B).normalized() # z is perpendicular to the the trajectory disk
		self.Ly = (self.Lz @ self.Lx) # y is perpendicular to z and x, along the line

		self.length = self.A.angle_to(self.B) # angle/distance between a and b

	@staticmethod
	def new_symbolic(a, b) :
		u = LineSegment( g3d.Vector(0.0, 0.0, 1.0, True), g3d.Vector(1.0, 0.0, 0.0, True) )
		
		u.A = g3d.Vector( * sympy.symbols(f'{a}_x {a}_y {a}_z') )
		u.B = g3d.Vector( * sympy.symbols(f'{a}_x {a}_y {a}_z') )

		u.Lx = g3d.Vector( * sympy.symbols(f'{a}{b}^Lx_x {a}{b}^Lx_y {a}{b}^Lx_z') )
		u.Ly = g3d.Vector( * sympy.symbols(f'{a}{b}^Ly_x {a}{b}^Ly_y {a}{b}^Ly_z') )
		u.Lz = g3d.Vector( * sympy.symbols(f'{a}{b}^Lz_x {a}{b}^Lz_y {a}{b}^Lz_z') )

		u.length = sympy.symbols(f'{a}{b}^d')

		return u

	def intersection(self, other) :
		return (self.Lz @ other.Lz).normalized()

	def side_point(self, t, d) :
		Px, Py, Pz = self.progress_frame(t)
		return Px.deviate(Pz, -d)

	def progress_point(self, t: float) :
		return self.Lx.deviate(self.Ly, t * self.length)

	def progress_frame(self, t: float) :
		Px = self.progress_point(t)
		Pz = self.Lz
		Py = Pz @ Px
		return Px, Py, Pz

	def projected_frame(self, Mx: g3d.Vector) :
		""" return Px, Py Pz where Px is the projection of Mx on the Line
		"""

		Pz = self.Lz
		Py = (Pz @ Mx).normalized()
		Px = (Py @ Pz) # the projection

		return Px, Py, Pz

	def projection(self, Mx: g3d.Vector) :
		""" return Px, Py Pz where Px is the projection of Mx on the Line
		"""

		Pz = self.Lz
		Py = (Pz @ Mx).normalized()
		Px = (Py @ Pz) # the projection

		return Px

	def surface_angle(self, other) :
		""" from one line to another, what is the angle """
		assert(self.B == other.A)
		return - self.Ly.angle_to(other.Ly, self.B)

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

		t = Lx.angle_to(Px, Lz) / self.length # the progress

		# frame, local to P, oriented to the north
		Nx = Px
		Ny = (g3d.v_north @ Nx).normalized()
		Nz = (Nx @ Ny)

		h = math.degrees( Py.angle_to(Nz, Px) )

		d = Mx.angle_to(Px)

		return Px, t, h, d

class LineCorridor(LineSegment) :

	def __init__(self, A: g3d.Vector, B: g3d.Vector, a_width: float, b_width: float) :

		LineSegment.__init__(self, A, B)

		self.a_width = a_width
		self.b_width = b_width
		
	def border_point(self, t, s) :
		s = math.copysign(1.0, s)
		Pq, Pr, Ps = self.progress_frame(t)
		w = self.a_width * (1 - t) + self.b_width * t

		return Pq.deviate(Ps, w * s)

	def _border_tip(self, t, d, s) :
		s = math.copysign(1.0, s)
		Pq, Pr, Ps = self.progress_frame(t)
		w = self.a_width * (1 - t) + self.b_width * t

		Pm = Ps.deviate(Pr, d * math.pi * s)
		return Pq.deviate(Pm, w)

	def make_joint(self, other) :
		""" for 3 points A, B, C in this order, self and other should two consecutive corridors A->B et B->C """
		from goto.globe.plot import GlobePlotMpl, GlobePlotGps

		assert(self.B == other.A)

		A, B, C = self.A, self.B, other.B

		q = self.surface_angle(other)
		w = math.copysign(1.0, q)
		print(w)

		Q = -w * (self.Lz + other.Lz).normalized()

		point_ab = self.side_point(0.0, w * self.a_width)
		point_ba = self.side_point(1.0, w * self.b_width)
		point_bc = other.side_point(0.0, w * other.a_width)
		point_cb = other.side_point(1.0, w * other.b_width)

		side_ab = LineSegment(point_ab, point_ba)
		side_bc = LineSegment(point_bc, point_cb)

		I = -w * side_ab.intersection(side_bc)

		# Px, Py, Pz = self.progress_frame(0.0)

		# with GlobePlotMpl() as plt :
		# 	plt.add_point(A, 'A', 'r')
		# 	plt.add_point(B, 'B', 'g')
		# 	plt.add_point(C, 'C', 'b')
		# 	# plt.add_point(Px, 'Px', 'purple')
		# 	# plt.add_point(Py, 'Py', 'purple')
		# 	# plt.add_point(Pz, 'Pz', 'purple')
		# 	# plt.add_point(point_ab, 'Pab', 'orange')
		# 	plt.add_line(point_ab, point_ba)
		# 	plt.add_line(point_bc, point_cb)
		# 	plt.add_point(I, 'I', 'orange')
		# 	plt.add_point(Q, 'Q', "magenta")

		P1 = I * Q
		P2 = I * B
		R = -(A * Q)**2 / (
		    A.y**2*(-1+B.y**2) +
		    2*A.x*A.z*B.x*B.z +
		    2*A.y*B.y*(A.x*B.x+A.z*B.z) +
		    A.z**2*(-1+B.z**2) -
		    A.x**2*(B.y**2+B.z**2)
		)

		t = math.acos(math.sqrt( (P1**2 - R)**2 / (
		    P1**4 + P1**2*(1 + P2**2 - 2*R) +
		    R*(-1 + P2**2 + R) +
		    2*math.sqrt(P1**2*P2**2*(P1**2 + (-1 + P2**2)*R))
		)))

		V = B*math.cos(t) + Q*math.sin(t)

		# with GlobePlotMpl() as plt :
		with GlobePlotGps(Path("tmp.plot.json")) as plt :
			plt.add_point(A, 'A')
			plt.add_point(B, 'B')
			plt.add_point(C, 'C')
			# plt.add_point(point_ab, 'Pab')
			plt.add_line(point_ab, point_ba)
			plt.add_line(point_bc, point_cb)
			plt.add_point(Q, 'Q', 'g')
			# plt.add_point(self.Ly, 'Sy', 'r')
			# plt.add_point(other.Ly, 'Oy', 'r')
			plt.add_line(point_ab, point_ba)
			plt.add_line(point_bc, point_cb)
			plt.add_point(I, 'I')
			plt.add_point(V, 'V', 'magenta')

		E = self.projection(V)
		F = other.projection(V)

		VEa = E.angle_to(V)
		VFa = F.angle_to(V)

		assert( math.isclose(VEa, VFa, rel_tol=1e-4) )

		AEp = A.angle_to(E) / self.length
		BFp = B.angle_to(F) / other.length

		return E, F, V, w*VEa, AEp, BFp

if __name__ == '__main__' :
	from goto.globe.blip import Blip

	A = Blip(-30.0, 0.0).as_vector
	B = Blip(0.0, 0.0).as_vector
	C = Blip(15.0, 15.0).as_vector
	#L = Blip(0.0, -30.0).as_vector

	line_AB = LineCorridor(A, B, 0.05, 0.05)
	line_BC = LineCorridor(B, C, 0.05, 0.05)

	# print(
	# 	line_AB.make_joint(line_BR)
	# )

	#line_BL = LineCorridor(B, L, 0.05, 0.05)

	print(
		line_AB.make_joint(line_BC)
	)
