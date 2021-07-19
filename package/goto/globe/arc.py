#!/usr/bin/env python3

import functools
import math
import sympy
import typing

import geometrik.threed as g3d


class ArcSegment() :
	def __init__(self, A: g3d.Vector, B: g3d.Vector, point_or_radius: typing.Union[float, g3d.Vector]) :

		self.A = A.normalized()
		self.B = B.normalized()

		self.angle_ab = self.A.angle_to(self.B) # distance between A and B

		if isinstance(point_or_radius, float) :
			self.__init__from_radius(point_or_radius)
		elif isinstance(point_or_radius, g3d.Vector) :
			self.__init__from_point(point_or_radius)

		Az = (self.Vx @ self.A).normalized()
		Bz = (self.Vx @ self.B).normalized()

		self.sector_ab = Az.angle_to(Bz) # angle covered by the arc
		self.length = self.sector_ab * math.sin(self.radius) # geodesic distance

		# compute the initial frame, direct only for right turns
		self.Vy = - self.way * Az
		self.Vz = self.way * (self.Vx @ self.Vy)

	def __init__from_radius(self, radius: float) :
		radius_min = self.angle_ab / 2
		radius_max = math.pi / 2
		
		self.way = math.copysign(1.0, radius)
		self.radius = max(radius_min, min(abs(radius), radius_max))

		if radius != self.way * self.radius :
			print(f"radius was clamped to {self.way * self.radius}")

		I = (self.A + self.B).normalized() # the point between A and B
		Q = self.way * (self.B @ self.A).normalized()

		t = math.acos(math.cos(self.radius) / (self.A * I))
		self.Vx = I * math.cos(t) + Q * math.sin(t) # the center of the arc

	def __init__from_point(self, M: g3d.Vector) :
		""" better if M is a middle point in between A and B """
		M = M.normalized()

		Ix = (self.A + M).normalized()
		Jx = (M + self.B).normalized()

		Iz = (M @ self.A).normalized()
		Jz = (self.B @ M).normalized()

		Iy = Ix @ Iz
		Jy = Jx @ Jz

		self.way = math.copysign(1.0, M * (Jz @ Iz))

		self.Vx = self.way * (Jy @ Iy).normalized()

		self.radius = self.Vx.angle_to(M)
		if (math.pi / 2.0) <= self.radius :
			raise ValueError("Excessive radius")

	def progress_frame(self, t: float) :
		""" frame local at the progress t, on the curve """

		Pq = self.progress_point(t)

		Pr = self.way * (Pq @ self.Vx).normalized()
		Ps = Pr @ Pq

		return Pq, Pr, Ps

	def progress_point(self, t: float) :

		Pm = self.Vz.deviate(self.Vy, t * self.sector_ab)
		Pq = self.Vx.deviate(Pm, self.radius)

		return Pq

	# def plot_line(self, n=64) :
	# 	p_lst = list()
	# 	for i in range(n) :
	# 		t = i / (n - 1)
	# 		p_lst.append( self.progress_point(t) )
	# 	return p_lst

	def status(self, M: g3d.Vector) :

		# frame local to C, oriented with Vz toward M
		Vx = self.V
		Vy = (M @ Vx).normalized()
		Vz = Vx @ Vy

		print(f"Vx = {Vx}")
		print(f"Vy = {Vy}")
		print(f"M @ Vx = {M @ Vx}")
		print(f"Vz = {Vz}")
		print(f"radius = {self.radius}")

		# P is M projected on the arc
		Px = Vx * math.cos(self.radius) + self.way * Vz * math.sin(self.radius)
		Py = self.way * Vy
		Pz = Px @ Py

		Ax = self.V
		Ay = (self.A @ self.V).normalized()
		Az = Ax @ Ay

		Bx = self.V
		By = (self.B @ self.V).normalized()
		Bz = Bx @ By

		t = Vz.signed_angle_to(Az, self.way * Vx) / Az.angle_to(Bz)

		# frame, local to P, oriented to the north
		Nx = Px
		Ny, Nz = g3d.plane.Plane(Px).frame()

		h = math.degrees( Py.signed_angle_to(Nz, Px) )
		d = M.angle_to(Px)

		print(f"M = {M}")
		print(f"Px = {Px}")
		print(f"d = {d}")

		return Px, t, h, d

class ArcCorridor(ArcSegment) :
	def __init__(self, A: g3d.Vector, B: g3d.Vector, point_or_radius: typing.Union[float, g3d.Vector], a_width: float, b_width: float) :
		ArcSegment.__init__(self, A, B, point_or_radius)

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

if __name__ == '__main__' :

	from cc_pathlib import Path

	from goto.globe.blip import Blip
	from goto.globe.plot import GlobePlotMpl, GlobePlotGps

	A = Blip(-30.0, 0.0).as_vector
	B = Blip(30.0, 0.0).as_vector
	C = Blip(0.0, 15.0).as_vector

	u = ArcCorridor(A, B, C, 0.04, 0.06)

	# with GlobePlotMpl() as plt :
	# 	plt.add_point(A, 'A', 'r')
	# 	plt.add_point(B, 'B', 'g')
	# 	plt.add_point(C, 'C', 'b')
	# 	plt.add_point(u.Vx, 'V', 'k')
	# 	plt.add_segment(u)
	# 	plt.add_border(u, "orange")

	with GlobePlotGps(Path("test.plot.json")) as plt :
		plt.add_point(A, 'A')
		plt.add_point(B, 'B')
		plt.add_segment(u)
		plt.add_border(u)
