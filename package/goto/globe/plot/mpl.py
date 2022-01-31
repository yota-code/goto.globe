#!/usr/bin/env python3

import math

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as plt3

import matplotlib.patches

from mpl_toolkits.mplot3d import Axes3D, proj3d
from matplotlib.patches import FancyArrowPatch

import geometrik.threed as g3d

from .base import GlobePlot__base__

class arrow_3d(matplotlib.patches.FancyArrowPatch):
	def __init__(self, xs, ys, zs, *args, **kwargs):
		matplotlib.patches.FancyArrowPatch.__init__(self, (0,0), (0,0), * args, ** kwargs)
		self._verts3d = xs, ys, zs

	def draw(self, renderer):
		xs3d, ys3d, zs3d = self._verts3d
		xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
		self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
		matplotlib.patches.FancyArrowPatch.draw(self, renderer)

class GlobePlotMpl(GlobePlot__base__) :
	def __init__(self, pth=None) :
		self.pth = pth

	def __enter__(self) :

		u = np.linspace(0, 2 * np.pi, 100)
		v = np.linspace(0, np.pi, 100)

		sphere_x = np.outer(np.cos(u), np.sin(v))
		sphere_y = np.outer(np.sin(u), np.sin(v))
		sphere_z = np.outer(np.ones(np.size(u)), np.cos(v))

		if self.pth is None :
			self.fig = plt.figure()
		else :
			self.fig = plt.figure(figsize=(16, 16))

		self.axe = self.fig.add_subplot(1, 1, 1, projection='3d')
		self.axe.plot_surface(sphere_x, sphere_y, sphere_z, color='b', alpha=0.05)
		self.axe.plot(np.cos(u), np.sin(u), np.zeros_like(u), color='r', alpha=0.2)

		color_map = { 0: 'g', 2: 'b' }
		for i in range(8) :
			color = color_map.get(i, 'black')
			self.axe.plot(
				np.sin(v) * np.cos(i * math.tau / 8),
				np.sin(v) * np.sin(i * math.tau / 8),
				np.cos(v),
				color=color, alpha=0.2
			)

		return self

	def _plot_lst(self, p_lst, color) :
		self.axe.plot(
			[p.x for p in p_lst],
			[p.y for p in p_lst],
			[p.z for p in p_lst], color=color
		)

	def add_arc_from_radius(self, Ax, Bx, radius, color='k') :

		A = Ax.normalized()
		B = Bx.normalized()

		angle_ab = A.angle_to(B)
		rad_mini = angle_ab / 2.0

		way = math.copysign(1.0, radius)
		rad = way * max(rad_mini, min(abs(radius), math.pi / 2))

		I = (A + B).normalized()
		Q = way * (B @ A).normalized()
		t = math.acos(math.cos(radius) / (A * I))

		C = I * math.cos(t) + Q * math.sin(t)

		return C

	def __exit__(self, exc_type, exc_value, traceback) :
		self.axe.view_init(elev=20.0, azim=0.0)
		if self.pth is None :
			plt.show()
		else :
			plt.savefig(str(self.pth))
		

	def add_point(self, Ax, name, color='k') :		
		self.axe.add_artist(arrow_3d(
			[0.0, Ax.x],
			[0.0, Ax.y],
			[0.0, Ax.z],
			mutation_scale=15, arrowstyle='-|>', color=color, shrinkA=0, shrinkB=0
		))
		self.axe.text(
			2 * Ax.x / 3,
			2 * Ax.y / 3,
			2 * Ax.z / 3,
			name,
			horizontalalignment='center', verticalalignment='center', fontsize=10, color=color
		)

	def add_line(self, point_a, point_b, color='k') :
		x = point_a
		z = (point_a @ point_b).normalized()
		y = z @ x

		d = point_a.angle_to(point_b)

		p_lst = list()
		for t in np.linspace(0.0, d, 100) :
			q = x * math.cos(t) + y * math.sin(t)
			p_lst.append([q.x, q.y, q.z])

		self.axe.plot(
			[i[0] for i in p_lst],
			[i[1] for i in p_lst],
			[i[2] for i in p_lst], color=color
		)
	
	def add_segment(self, u, color='k') :
		self._plot_lst(GlobePlot__base__.add_segment(self, u), color)

	def add_border(self, u, color='k') :
		self._plot_lst(GlobePlot__base__.add_border(self, u), color)

	def add_great_circle(self, Nx, color='k'):
		p = g3d.Plane(Nx)
		Ny, Nz = p.frame()
		print(Ny, Nz)
		p_lst = list()
		for t in np.linspace(0.0, math.tau, 100) :
			v = g3d.Vector.compose(Ny, Nz, t)
			p_lst.append(v.as_tuple)

		self.axe.plot(
			[i[0] for i in p_lst],
			[i[1] for i in p_lst],
			[i[2] for i in p_lst], color=color
		)

	def add_circle(self, center, other, color='k') :
		x = center
		if isinstance(other, float) :
			d = other
			y, z = g3d.Plane(center).frame()
		else :
			z = (center @ other).normalized()
			y = z @ x
			d = center.angle_to(other)

		p_lst = list()
		for t in np.linspace(0.0, math.tau, 100) :
			q = (y * math.cos(t) + z * math.sin(t))
			r = (x * math.cos(d) + q * math.sin(d))
			p_lst.append([r.x, r.y, r.z])

		self.axe.plot(
			[i[0] for i in p_lst],
			[i[1] for i in p_lst],
			[i[2] for i in p_lst], color=color
		)

	def add_arc_from_center(self, Ax, Bx, Cx, color='k') :
		Az = (Cx @ Ax).normalized()
		Ay = Az @ Cx

		Bz = (Cx @ Bx).normalized()
		By = Bz @ Cx

		z = By.angle_to(Ay, Cx)

		d1 = Cx.angle_to(Ax)
		d2 = Cx.angle_to(Bx)

		d = (d1 + d2)/2

		p_lst = list()
		for t in np.linspace(0.0, z, 100) :
			q = (By * math.cos(t) + Bz * math.sin(t))
			r = (Cx * math.cos(d) + q * math.sin(d))
			p_lst.append([r.x, r.y, r.z])

		self.axe.plot(
			[i[0] for i in p_lst],
			[i[1] for i in p_lst],
			[i[2] for i in p_lst], color=color
		)

	def add_signed_arc(self, Ax, Bx, Cx, w, color='k') :
		Az = w * (Ax @ Cx).normalized()
		Ay = w * (Cx @ Az)

		Bz = w * (Bx @ Cx).normalized()
		By = w * (Cx @ Bz)

		a_tmp = w * By.angle_to(Ay, Cx)
		a_ref = (a_tmp) if (a_tmp >= 0) else (math.tau + a_tmp)

		# print(math.degrees(a_tmp))
		# print(math.degrees(a_ref))

		d1 = Cx.angle_to(Ax)
		d2 = Cx.angle_to(Bx)

		d = (d1 + d2)/2

		p_lst = list()
		for t in np.linspace(0.0, a_ref, 100) :
			q = (Ay * math.cos(t) + Az * math.sin(t))
			r = (Cx * math.cos(d) + q * math.sin(d))
			p_lst.append([r.x, r.y, r.z])

		self.axe.plot(
			[i[0] for i in p_lst],
			[i[1] for i in p_lst],
			[i[2] for i in p_lst], color=color
		)

	def add_arc_from_radius(self, Ax, Bx, radius, color='k') :
		A = Ax.normalized()
		B = Bx.normalized()

		angle_ab = A.angle_to(B)
		rad_mini = angle_ab / 2.0

		way = math.copysign(1.0, radius)
		rad = way * max(rad_mini, min(abs(radius), math.pi / 2))

		I = (A + B).normalized()
		Q = way * (B @ A).normalized()
		t = math.acos(math.cos(radius) / (A * I))

		C = I * math.cos(t) + Q * math.sin(t)

		self.add_arc_from_center(A, B, C)