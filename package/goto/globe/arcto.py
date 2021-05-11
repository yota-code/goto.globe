#!/usr/bin/env python3

import math
import sympy

import geometrik.threed as g3d

# import goto.globe.blip

class ArcTo() :

	""" plus de blip ici !!! que des vecteurs unitaires !!! """

	north = g3d.Vector(0.0, 0.0, 1.0, True)

	def __init__(self, A: g3d.Vector, B: g3d.Vector, radius: float) :

		self.A = A.normalized()
		self.B = B.normalized()

		self.angle_ab = self.A.angle_to(self.B) # angle/distance between a and b			

		self.radius = abs(radius)
		self.way = math.copysign(1.0, radius)

		# if self.angle_ab > 2 * self.radius :
		# 	self.radius = self.angle_ab / 2
		# 	print(f"error: radius to small {radius}, changed to {self.radius}")
		# else :
		# 	print(f"smallest radius allowed: {self.angle_ab / 2}")

		self.P = (self.A + self.B).normalized()
		self.Q = (self.A @ self.B).normalized() if self.way < 0.0 else (self.B @ self.A).normalized()

		k = (self.A + self.B).norm * math.cos(radius) / (1 + self.A * self.B)
		if not -1.0 <= k <= 1.0 :
			k = max(-1.0, min(k, 1.0))
			t = 0.0
			self.C = self.P
			self.radius = self.C.angle_to(self.A)
		else :
			t = math.acos(k)
			self.C = self.P * math.cos(t) + self.Q * math.sin(t)

