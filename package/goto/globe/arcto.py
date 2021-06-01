#!/usr/bin/env python3

import math
import sympy

import geometrik.threed as g3d

# import goto.globe.blip

class ArcTo() :

	""" plus de blip ici !!! que des vecteurs unitaires !!! """

	def __init__(self, A: g3d.Vector, B: g3d.Vector, radius: float) :

		self.A = A.normalized()
		self.B = B.normalized()

		# print(f"A = {self.A}")
		# print(f"B = {self.B}")

		self.angle_ab = self.A.angle_to(self.B) # angle/distance between A and B			

		radius_mini = self.angle_ab / 2
		self.way = math.copysign(1.0, radius)
		self.radius = self.way * max(radius_mini, min(abs(radius), math.pi / 2))
		if self.radius != radius :
			print(f"radius was clamped to {self.radius}")

		I = (self.A + self.B).normalized() # the point between A and B
		Q = self.way * (self.B @ self.A).normalized()

		# print(f"radius = {self.radius}")
		# print(f"I = {I}")
		# print(f"Q = {Q}")

		t = math.acos(math.cos(self.radius) / (self.A * I))
		self.C = I * math.cos(t) + Q * math.sin(t) # the center of the arc

		# print(f"t = {t}")
		# print(f"C = {self.C}")

	def status(self, M: g3d.Vector) :

		# frame local to C, oriented with Cz toward M
		Cx = self.C
		Cy = (M @ self.C).normalized()
		Cz = Cx @ Cy

		# print(f"Cx = {Cx}")
		# print(f"Cy = {Cy}")
		# print(f"Cz = {Cz}")


		# with g3d.UnitSpherePlot() as u :
		#     u.add_point(Cx, 'Cx', 'r')
		#     u.add_point(M, 'M', 'magenta')
		#     u.add_point(Cy, 'Cy', 'g')
		#     u.add_point(Cz, 'Cz', 'g')

		# P is M projected on the arc
		Px = Cx * math.cos(self.radius) + self.way * Cz * math.sin(self.radius)
		Py = self.way * Cy
		Pz = Px @ Py

		# print(f"Px = {Px}")

		Ax = self.C
		Ay = (self.A @ self.C).normalized()
		Az = Ax @ Ay

		Bx = self.C
		By = (self.B @ self.C).normalized()
		Bz = Bx @ By

		# with g3d.UnitSpherePlot() as u :
		# 	u.add_point(M, 'M', 'magenta')
		# 	u.add_point(Px, 'P', 'cyan')

		# 	u.add_point(Cx, 'Cx', 'r')
		# 	u.add_point(Cy, 'Cy', 'r')
		# 	u.add_point(Cz, 'Cz', 'r')

		# 	u.add_point(Ax, 'Ax', 'g')
		# 	u.add_point(Ay, 'Ay', 'g')
		# 	u.add_point(Az, 'Az', 'g')

		# 	u.add_point(Bx, 'Bx', 'b')
		# 	u.add_point(By, 'By', 'b')
		# 	u.add_point(Bz, 'Bz', 'b')

		# 	u.add_circle_part(self.C, self.A, self.B)

		t = Cz.signed_angle_to(Az, self.way * Cx) / Az.angle_to(Bz)

		# frame, local to P, oriented to the north
		Nx = Px
		Ny, Nz = g3d.plane.Plane(Px).frame()

		# with g3d.UnitSpherePlot() as u :
		# 	u.add_point(M, 'M', 'magenta')
		# 	u.add_point(Px, 'P', 'cyan')

		# 	u.add_point(Cx, 'Cx', 'r')
		# 	u.add_point(Cy, 'Cy', 'r')
		# 	u.add_point(Cz, 'Cz', 'r')

		# 	u.add_point(Px, 'Px', 'b')
		# 	u.add_point(Py, 'Py', 'b')
		# 	u.add_point(Pz, 'Pz', 'b')

		# 	u.add_point(Nx, 'Nx', 'g')
		# 	u.add_point(Ny, 'Ny', 'g')
		# 	u.add_point(Nz, 'Nz', 'g')

		# 	u.add_circle_part(self.C, self.A, self.B)


		h = math.degrees( Py.signed_angle_to(Nz, Px) )
		d = M.angle_to(Px)

		return Px, t, h, d