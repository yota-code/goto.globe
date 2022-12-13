#!/usr/bin/env python3

import math

import goto.globe
from goto.globe.blip import Blip

import geometrik.threed as g3d

class SegmentLine() :

	debug = True

	def __init__(self, A:Blip, B:Blip) :

		self.Ax = A.as_vector
		self.Bx = B.as_vector

		assert(1.0 <= self.Ax.angle_to(self.Bx) * goto.globe.earth_radius, "no line segment when length is less than one meter")

		self.compute_def()

	def compute_def(self) :

		# oriented rightward, perpendicular to the trajectory
		self.Ay = (self.Bx @ self.Ax).normalized()

		# oriented forward, perpendicular to Ax
		self.Az = (self.Ax @ self.Ay)

		self.sector = self.Ax.angle_to(self.Bx)
		self.length = self.sector * goto.globe.earth_radius

	def compute_sta(self, M) :
		self.Mx = M.as_vector
		self.Px = self.Mx.project(self.Ay).normalized()
		self.Pz = self.Px @ self.Ay
		self.dev_lat = self.Px.angle_to(self.Mx, self.Pz)
		Fe, Fn = self.Px.frame(g3d.v_north)
		self.Fe, self.Fn = Fe, Fn
		self.track = self.Pz.atan2(Fe, Fn)
		# self.angle = self.Px.angle_to(self.Ax, self.Ay)
		self.advance = self.Px.atan2(self.Az, self.Ax) / self.sector

	def plot_sta(self) :
		from goto.globe.plot import GlobePlotMpl

		P = Blip.from_vector(self.Px)

		print(f"P = {P}")
		print(f"dev_la = {self.dev_lat} ({math.degrees(self.dev_lat)}°)")
		print(f"advance = {self.advance}")
		print(f"track = {self.track} ({math.degrees(self.track)}°)")

		with GlobePlotMpl() as plt :
			plt.add_point(self.Ax, "Ax", "orange")
			plt.add_point(self.Bx, "Bx", "orange")

			plt.add_line(self.Ax, self.Bx)

			plt.add_point(self.Mx, "Mx", "magenta")
			plt.add_point(self.Px, "Px", 'r')
			plt.add_point(self.Ay, "Py", 'g')
			plt.add_point(self.Pz, "Pz", 'b')

def test(A_lat, A_lon, B_lat, B_lon, M_lat, M_lon, tst_map) :
	A = Blip(A_lat, A_lon)
	B = Blip(B_lat, B_lon)
	M = Blip(M_lat, M_lon)

	u = SegmentLine(A, B)
	u.compute_def()
	u.compute_sta(M)

	ref_map = dict()
	for key in tst_map :
		ref_map[key] = getattr(u, key)
		if math.isclose(ref_map[key], tst_map[key]) :
			print(f"\x1b[32m{key}\x1b[0m = {tst_map[key]}")
		else :
			print(f"\x1b[31m{key}\x1b[0m = {tst_map[key]} vs {ref_map[key]}")

if __name__ == '__main__' :

	test(-20.0, 0.0, 20.0, 0.0, 0.0, 1.0, {'advance': 0.5, 'track': 0.0})

	# A = Blip(0.0, 0.0)
	# B = Blip(50.0, 50.0)
	# M = Blip(25.0, 10.0)

	# u = SegmentLine(A, B)
	# u.compute_def()
	# u.compute_sta(M)
	# u.plot_sta()
	
