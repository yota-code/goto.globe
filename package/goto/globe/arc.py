#!/usr/bin/env python3

import math
from re import S
import typing

import geometrik.threed as g3d

class ArcSegment() :

	def __init__(self, A: g3d.Vector, B: g3d.Vector, point_or_radius: typing.Union[float, g3d.Vector]) :

		self.Ax = A.normalized()
		self.Bx = B.normalized()

		self.angle_ab = self.Ax.angle_to(self.Bx) # distance between A and B

		if isinstance(point_or_radius, float) :
			self.__init__from_radius(point_or_radius)
		elif isinstance(point_or_radius, g3d.Vector) :
			self.__init__from_point(point_or_radius)

		self.Ay = self.way * (self.Ax @ self.Vx).normalized()
		self.Az = self.Ax @ self.Ay

		self.By = self.way * (self.Bx @ self.Vx).normalized()
		self.Bz = self.Bx @ self.By

		self.aperture_ab = self.Ay.angle_to(self.By) # angle covered by the arc
		self.length = self.aperture_ab * math.sin(self.radius) # geodesic distance

		# print(f"radius = {self.radius}")

		# compute the initial frame, direct only for right turns
		self.Vz = self.Ay
		self.Vy = -self.way * (self.Vz @ self.Vx)

	def __init__from_radius(self, radius: float) :
		radius_min = self.angle_ab / 2
		radius_max = math.pi / 2
		
		self.way = math.copysign(1.0, radius)
		self.radius = max(radius_min, min(abs(radius), radius_max))

		if radius != self.way * self.radius :
			print(f"radius was clamped to {self.way * self.radius}")

		Qx = (self.Ax + self.Bx).normalized() # the point between A and B
		Qy = self.way * (self.Bx @ self.Ax).normalized()

		r = math.cos(self.radius) / (self.Ax * Qx)
		s = max(-1.0, min(r, 1.0))
		t = math.acos(s)

		# print(f"Qx = {Qx}")
		# print(f"Qy = {Qy}")

		self.Vx = Qx * math.cos(t) + Qy * math.sin(t) # the center of the arc

	def __init__from_point(self, M: g3d.Vector) :
		""" better if M is a middle point in between A and B """
		M = M.normalized()

		Ix = (self.Ax + M).normalized()
		Jx = (M + self.Bx).normalized()

		Iz = (M @ self.Ax).normalized()
		Jz = (self.Bx @ M).normalized()

		Iy = Ix @ Iz
		Jy = Jx @ Jz

		self.way = math.copysign(1.0, M * (Jz @ Iz))

		self.Vx = self.way * (Jy @ Iy).normalized()

		self.radius = self.Vx.angle_to(M)
		if (math.pi / 2.0) <= self.radius :
			raise ValueError("Excessive radius")

	def progress_frame(self, t: float) :
		""" frame local at the progress t, on the curve """

		Px = self.progress_point(t)

		Py = self.way * (Px @ self.Vx).normalized()
		Pz = Py @ Px

		return Px, Py, Pz

	def progress_point(self, t: float) :

		Pm = self.Vy.deviate(self.Vz, t * self.aperture_ab)
		Px = self.Vx.deviate(Pm, self.radius)

		return Px

	def status(self, M: g3d.Vector) :
		# print(f"Vx = {self.Vx}")
		# print(f"Ax = {self.Ax}")

		# frame local to V, oriented with Uz toward M, and Uy in the way of displacement
		Ux = self.Vx
		Uy = self.way * (M @ Ux).normalized()
		Uz = self.way * (Ux @ Uy)

		self.Ux, self.Uy, self.Uz = Ux, Uy, Uz

		# print(f"Ux = {Ux}")
		# print(f"Uy = {Uy}")
		# print(f"M @ Ux = {M @ Ux}")
		# print(f"Uz = {Uz}")
		# print(f"radius = {self.radius}")

		# P is M projected on the arc
		# print(self.radius)
		Px = Ux * math.cos(self.radius) + Uz * math.sin(self.radius)
		Py = Uy
		Pz = Px @ Py
		# print(f"Px = {Px}")
		# print(f"Py = {Py}")
		# print(f"Pz = {Pz}")

		self.Px, self.Py, self.Pz = Px, Py, Pz
		# print(f"Ux = {Ux}")
		# print(f"Uy = {Uy}")
		# print(f"Uz = {Uz}")

		Ax = self.Vx
		Ay = (self.Ax @ self.Vx).normalized()
		Az = Ax @ Ay

		Bx = self.Vx
		By = (self.Bx @ self.Vx).normalized()
		Bz = Bx @ By

		t = self.way * Uz.angle_to(Az, Ux) / Az.angle_to(Bz)

		# frame, local to P, oriented to the north
		Nx = Px
		Ny, Nz = g3d.plane.Plane(Px).frame()

		h = math.degrees( Py.angle_to(Nz, Px) )
		d = Px.angle_to(M, Uy)

		#print(f"M = {M}")
		#print(f"Px = {Px}")
		#print(f"d = {d}")
		#print(f"h = {h}")

		# print(f"Px = {Px}")

		return Px, t, h, d

class ArcCorridor(ArcSegment) :
	def __init__(self, A: g3d.Vector, B: g3d.Vector, point_or_radius: typing.Union[float, g3d.Vector], a_width: float, b_width: float) :
		ArcSegment.__init__(self, A, B, point_or_radius)

		self.a_width = a_width
		self.b_width = b_width

	def border_point(self, t, s) :
		s = math.copysign(1.0, s)
		Px, Py, Pz = self.progress_frame(t)
		w = self.a_width * (1 - t) + self.b_width * t

		return Px.deviate(Pz, w * s)

	def _border_tip(self, t, d, s) :
		s = math.copysign(1.0, s)
		Px, Py, Pz = self.progress_frame(t)
		w = self.a_width * (1 - t) + self.b_width * t

		Pm = Pz.deviate(Py, d * math.pi * s)
		return Px.deviate(Pm, w)

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
