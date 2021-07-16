#!/usr/bin/env python3

import functools
import math
import sympy

import geometrik.threed as g3d

# import goto.globe.blip

class ArcTo() :
	def __init__(self, A: g3d.Vector, B: g3d.Vector, point_or_radius: [float, g3d.Vector]) :

		self.A = A.normalized()
		self.B = B.normalized()

		self.angle_ab = self.A.angle_to(self.B) # distance between A and B

		if isinstance(point_or_radius, float) :
			self.__init__from_radius(point_or_radius)
		elif isinstance(point_or_radius, g3d.Vector) :
			self.__init__from_point(point_or_radius)

		Az = (self.V @ self.A).normalized()
		Bz = (self.V @ self.B).normalized()

		self.length = Az.angle_to(Bz) * math.sin(self.radius)

	def __init__from_radius(self, radius: float) :
		radius_min = self.angle_ab / 2
		radius_max = math.pi / 2
		
		self.way = math.copysign(1.0, radius)

		self.radius = self.way * max(radius_min, min(abs(radius), radius_max))

		if radius != self.radius :
			print(f"radius was clamped to {self.radius}")

		I = (self.A + self.B).normalized() # the point between A and B
		Q = self.way * (self.B @ self.A).normalized()

		t = math.acos(math.cos(self.radius) / (self.A * I))
		self.V = I * math.cos(t) + Q * math.sin(t) # the center of the arc

	def __init__from_point(self, M: g3d.Vector) :
		M = M.normalized()

		Ix = (self.A + M).normalized()
		Jx = (M + self.B).normalized()

		Iz = (M @ self.A).normalized()
		Jz = (self.B @ M).normalized()

		Iy = Ix @ Iz
		Jy = Jx @ Jz

		self.way = math.copysign(1.0, M * (Jz @ Iz))

		self.V = self.way * (Jy @ Iy).normalized()

		self.radius = self.V.angle_to(M)

	def progress_frame(self, t: float) :
		""" frame local at the progress t, on the curve """

		Vx = self.V
		Vy = self.A
		Vz = (Vx @ Vy).normalized()

		Vm = Vy.deviate(Vz, t * self.length)

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

		# with g3d.UnitSpherePlot() as u :
		#     u.add_point(Vx, 'Vx', 'r')
		#     u.add_point(M, 'M', 'magenta')
		#     u.add_point(Vy, 'Vy', 'g')
		#     u.add_point(Vz, 'Vz', 'g')

		# P is M projected on the arc
		Px = Vx * math.cos(self.radius) + self.way * Vz * math.sin(self.radius)
		Py = self.way * Vy
		Pz = Px @ Py

		# print(f"Px = {Px}")

		Ax = self.V
		Ay = (self.A @ self.V).normalized()
		Az = Ax @ Ay

		Bx = self.V
		By = (self.B @ self.V).normalized()
		Bz = Bx @ By

		# with g3d.UnitSpherePlot() as u :
		# 	u.add_point(M, 'M', 'magenta')
		# 	u.add_point(Px, 'P', 'Vyan')

		# 	u.add_point(Vx, 'Vx', 'r')
		# 	u.add_point(Vy, 'Vy', 'r')
		# 	u.add_point(Vz, 'Vz', 'r')

		# 	u.add_point(Ax, 'Ax', 'g')
		# 	u.add_point(Ay, 'Ay', 'g')
		# 	u.add_point(Az, 'Az', 'g')

		# 	u.add_point(Bx, 'Bx', 'b')
		# 	u.add_point(By, 'By', 'b')
		# 	u.add_point(Bz, 'Bz', 'b')

		# 	u.add_circle_part(self.V, self.A, self.B)

		t = Vz.signed_angle_to(Az, self.way * Vx) / Az.angle_to(Bz)

		# frame, local to P, oriented to the north
		Nx = Px
		Ny, Nz = g3d.plane.Plane(Px).frame()

		# with g3d.UnitSpherePlot() as u :
		# 	u.add_point(M, 'M', 'magenta')
		# 	u.add_point(Px, 'P', 'Vyan')

		# 	u.add_point(Vx, 'Vx', 'r')
		# 	u.add_point(Vy, 'Vy', 'r')
		# 	u.add_point(Vz, 'Vz', 'r')

		# 	u.add_point(Px, 'Px', 'b')
		# 	u.add_point(Py, 'Py', 'b')
		# 	u.add_point(Pz, 'Pz', 'b')

		# 	u.add_point(Nx, 'Nx', 'g')
		# 	u.add_point(Ny, 'Ny', 'g')
		# 	u.add_point(Nz, 'Nz', 'g')

		# 	u.add_circle_part(self.V, self.A, self.B)

		h = math.degrees( Py.signed_angle_to(Nz, Px) )
		d = M.angle_to(Px)

		print(f"M = {M}")
		print(f"Px = {Px}")
		print(f"d = {d}")

		return Px, t, h, d

if __name__ == '__main__' :
	from goto.globe.blip import Blip

	A = Blip(0.0, 0.0).as_vector
	B = Blip(30.0, 0.0).as_vector
	C = Blip(35.0, 15.0).as_vector
	u = ArcTo(A, B, C)