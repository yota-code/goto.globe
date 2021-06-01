#!/usr/bin/env python3

import math

import numpy as np
import matplotlib.pyplot as plt

import geometrik.threed as g3d

class GlobePlot__base__() :

	def add_circle(self, Cx, Px) :
		Cz = (Cx @ Px).normalized()
		Cy = Cz @ Cx

		d = Cx.angle_to(Px)

		p_lst = list()
		for t in np.linspace(0.0, math.tau, 128) :
			q = (Cy * math.cos(t) + Cz * math.sin(t))
			r = (Cx * math.cos(d) + q * math.sin(d))
			p_lst.append([r.x, r.y, r.z])

		return p_lst

	def add_line(self, Ax, Bx) :
		Az = (Ax @ Bx).normalized()
		Ay = Az @ Ax

		d = Ax.angle_to(Bx)

		p_lst = list()
		for t in np.linspace(0.0, d, 128) :
			q = Ax * math.cos(t) + Ay * math.sin(t)
			p_lst.append(q)

		return p_lst

	def add_arc(self, Ax, Bx, radius=0.0) :
		Cx = self._find_center(Ax, Bx, radius)

		Az = (Cx @ Ax).normalized()
		Ay = Az @ Cx

		Bz = (Cx @ Bx).normalized()
		By = Bz @ Cx

		z = By.signed_angle_to(Ay, Cx)

		d1 = Cx.angle_to(Ax)
		d2 = Cx.angle_to(Bx)

		d = (d1 + d2)/2

		p_lst = list()
		for t in np.linspace(0.0, z, 128) :
			q = (By * math.cos(t) + Bz * math.sin(t))
			r = (Cx * math.cos(d) + q * math.sin(d))
			p_lst.append(r)

		return p_lst

	def _find_center(self, Ax, Bx, radius) :
		""" the radius is signed, but only for the shortest arc
		"""
		A = Ax.normalized()
		B = Bx.normalized()

		angle_ab = A.angle_to(B)
		rad_mini = angle_ab / 2.0

		way = math.copysign(1.0, radius)
		rad = way * max(rad_mini, min(abs(radius), math.pi / 2))

		I = (A + B).normalized()
		Q = way * (B @ A).normalized()
		t = math.acos(math.cos(rad) / (A * I))

		C = I * math.cos(t) + Q * math.sin(t)

		return C