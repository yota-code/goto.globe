#!/usr/bin/env python3

import math
import typing

import numpy as np
import matplotlib.pyplot as plt

import geometrik.threed as g3d

class GlobePlot__base__() :

	def add_circle(self, Cx, radius) :

		if isinstance(radius, float) :
			Py, Pz = g3d.Plane.frame_optimal(Cx)
			Px = g3d.Vector.compose(Cx, Py, radius)
		else :
			Px = radius
		
		Cz = (Cx @ Px).normalized()
		Cy = Cz @ Cx

		d = Cx.angle_to(Px)

		p_lst = list()
		for t in np.linspace(0.0, math.tau, 128) :
			q = (Cy * math.cos(t) + Cz * math.sin(t))
			r = (Cx * math.cos(d) + q * math.sin(d))
			p_lst.append(r)

		return p_lst

	def add_line(self, Ax, Bx) :
		Az = (Ax @ Bx).normalized()
		Ay = Az @ Ax

		d = Ax.angle_to(Bx)

		p_lst = list()
		for t in np.linspace(0.0, d, 128) :
			p_lst.append( Ax * math.cos(t) + Ay * math.sin(t) )

		return p_lst

	def add_segment(self, u, n=64) :
		p_lst = list()
		for i in range(n) :
			t = i / (n - 1)
			p_lst.append( u.progress_point(t) )
		return p_lst

	def add_border(self, u, n=64) :
		p_lst = list()
		for i in range(n) :
			t = i / (n - 1)
			p_lst.append( u.border_point(t, 1) )
		for i in range(n) :
			d = i / (n - 1)
			p_lst.append( u._border_tip(1.0, d, 1) )
		for i in range(n) :
			t = 1 - (i / (n - 1))
			p_lst.append( u.border_point(t, -1) )
		for i in range(n) :
			d = 1 - (i / (n - 1))
			p_lst.append( u._border_tip(0.0, d, -1) )
		p_lst.append(p_lst[0])
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