#!/usr/bin/env python3

import math

import goto.globe
from goto.globe.blip import Blip

import geometrik.threed as g3d


class SegmentArc() :

	debug = False

	def __init__(self, A:Blip, B:Blip, radius: float, is_large_arc:bool=False) :
		if self.debug :
			print(f"SegmentArc(A, B, {radius}, {is_large_arc})")

		self.Ax = A.as_vector
		self.Bx = B.as_vector

		self.aperture = self.bounded_aperture(radius)

		self.compute_def(radius, is_large_arc)

	def bounded_aperture(self, radius) :
		a_mini = self.Ax.angle_to(self.Bx) / 2.0

		a_abs = abs(radius / goto.globe.earth_radius)
		a_maxi = math.pi / 2.0
		a_bounded = max(a_mini, min(a_abs, a_maxi))

		if self.debug :
			if a_abs != a_bounded :
				print(f"{a_mini} < ({a_abs} -> {a_bounded}) < {a_maxi}")
			else :
				print(f"{a_mini} < ({a_bounded}) < {a_maxi}")

		return a_bounded

	def compute_def(self, radius, is_large_arc) :
		Ax, Bx = self.Ax, self.Bx

		w = math.copysign(1.0, radius)
		k = -1.0 if is_large_arc else 1.0
		
		# la base Q est toujours directe
		Qx = (Ax + Bx).normalized() # Qx entre Ax et Bx (vers le haut)
		Qy = (Bx @ Ax).normalized() # Qy vers la droite
		Qz = Qx @ Qy # Qz vers l'avant (de Ax vers Bx)
		
		res = w * k * math.acos(min((math.cos(self.aperture) / (Ax * Qx)), math.pi / 2.0))
		
		Cx = g3d.Vector.compose(Qx, Qy, res)
		Cz = Qz
		Cy = w * Cx @ Cz

		Az = (Ax @ Cx).normalized()
		Ay = (Cx @ Az)

		Bz = (Bx @ Cx).normalized()
		By = (Cx @ Bz)

		# sector = ( math.tau - Ay.angle_to(By, Cx) ) if is_large_arc else ( Ay.angle_to(By, Cx) )
		# sector = k * ((math.tau if is_large_arc else 0.0) - Ay.angle_to(By))
		sector = -k * w * ((math.tau if is_large_arc else 0.0) - Ay.angle_to(By))

		self.Cx, self.Qz, self.sector = Cx, Qz, sector

	def plot_def(self, pth=None) :
		from goto.globe.plot import GlobePlotMpl

		w = math.copysign(1.0, self.sector)
		k = -1.0 if abs(self.sector) > math.pi else 1.0

		with GlobePlotMpl(pth) as plt :
			plt.add_point(self.Ax, "Ax", "orange")
			plt.add_point(self.Bx, "Bx", "cyan")
			plt.add_point(self.Cx, "Cx", "magenta")
			plt.add_point(self.Qz, "Qz", "magenta")
			plt.add_circle(self.Cx, self.Ax, "yellow")
			plt.add_signed_arc(self.Ax, self.Bx, self.Cx, w)


		# print(f"sector: {math.degrees(sector)} w={w} k={k}", "turn right" if w > 0.0 else "turn left")

		# if self.debug :

		# 	from goto.globe.plot import GlobePlotMpl

		# 	with GlobePlotMpl() as plt :
		# 		plt.add_point(Ax, "Ax", "orange")
		# 		plt.add_point(Bx, "Bx", "cyan")
		# 		plt.add_point(Qx, "Qx", "r")
		# 		plt.add_point(Ay, "Ay", "r")
		# 		plt.add_point(By, "By", "r")
		# 		plt.add_point(Cx, "Cx", "magenta")
		# 		plt.add_point(Cy, "Cy", "purple")
		# 		plt.add_point(Cz, "Cz", "k")
		# 		plt.add_signed_arc(Ax, Bx, Cx, w)

		# 		print(f"sector = {sector}")
			

	def compute_advance(self, Ap, Pp) :
		Cx, sector = self.Cx, self.sector

	def compute_sta(self, M) :

		self.Mx = M.as_vector

		# print("sector:", math.degrees(self.sector))

		is_large_arc = abs(self.sector) > math.pi

		w = math.copysign(1.0, self.sector)
		k = -1.0 if is_large_arc else 1.0

		# print(f"w={w} k={k}")

		self.Cz = k * w * (self.Mx @ self.Cx).normalized()
		self.Cy = (self.Cz @ (-w * self.Cx))

		Qy = (self.Qz @ (-w * self.Cx))

		aperture_cur = self.Mx.angle_to(self.Cx, self.Qz)

		Px = g3d.Vector.compose(self.Cx, self.Cy, k * self.aperture)

		dev_lat = Px.angle_to(self.Mx, self.Qz)

		Ny, Nz = Px.frame(g3d.v_north)

		track = self.Cz.atan2(Nz, Ny)
		# print("trk:", trk, math.degrees(trk))

		# print(dev_lat * goto.globe.earth_radius)

		self.Ap = self.Ax.project(self.Cx).normalized()
		self.Bp = self.Bx.project(self.Cx).normalized()
		self.Pp = Px.project(self.Cx).normalized()

		Aa = self.Ap.atan2(Qy, self.Qz)
		Pa = self.Pp.atan2(Qy, self.Qz)
		Ba = self.Bp.atan2(Qy, self.Qz)

		self.advance = (Pa - Aa) / (Ba - Aa)

		self.track = track
		self.Px = Px

		# print("advance:", advance)
		# print("aperture:", self.aperture)
		# print("angle Ax/Cx:", self.Ax.angle_to(self.Cx))
		# print(Px.angle_to(self.Cx))

		# if self.debug :
		# 	from goto.globe.plot import GlobePlotMpl

		# 	with GlobePlotMpl() as plt :
		# 		plt.add_point(self.Ax, "Ax", "orange")
		# 		plt.add_point(self.Bx, "Bx", "cyan")
		# 		# plt.add_point(Qy, "Qy", "b")
		# 		# plt.add_point(self.Qz, "Qz", "yellow")
		# 		# plt.add_point(Qy, "Qy", "b")
		# 		plt.add_signed_arc(self.Ax, self.Bx, self.Cx, w)

		# 		# plt.add_point(Mx, "Mx")

		# 		plt.add_point(self.Cx, "Cx", "r")
		# 		plt.add_point(Cy, "Cy", "g")
		# 		plt.add_point(Cz, "Cz", "b")

		# 		# plt.add_point(Px, "Px", "pink")

		# 		# plt.add_point(Ny, "Ny")
		# 		# plt.add_point(Nz, "Nz")

		# 		plt.add_point(self.Ap, "self.Ap", "magenta")
		# 		plt.add_point(self.Bp, "self.Bp", "magenta")
		# 		plt.add_point(Pp, "Pp", "magenta")

	def plot_sta(self, pth=None) :
		from goto.globe.plot import GlobePlotMpl

		w = math.copysign(1.0, self.sector)
		k = -1.0 if abs(self.sector) > math.pi else 1.0

		with GlobePlotMpl(pth) as plt :
			plt.add_point(self.Ax, "Ax", "orange")
			plt.add_point(self.Ap, "Ap", "r")
			plt.add_point(self.Bx, "Bx", "cyan")
			plt.add_point(self.Bp, "Bp", "b")
			
			plt.add_point(self.Cx, "Cx", "lime")
			plt.add_point(self.Cz, "Cz", "purple")

			plt.add_point(self.Mx, "Mx", "magenta")
			plt.add_point(self.Px, "Px", "r")
			plt.add_circle(self.Cx, self.Ax, "yellow")
			plt.add_signed_arc(self.Ax, self.Bx, self.Cx, w)



if __name__ == '__main__' :
	from goto.globe.blip import Blip

	BOD = Blip(44.828333, -0.715556).as_vector
	MXP = Blip(45.63, 8.723056).as_vector
	MRS = Blip(43.436667, 5.215).as_vector
	LHR = Blip(51.4775, -0.461389).as_vector
	LIS = Blip(38.774167, -9.134167).as_vector
	RKV = Blip(64.13, -21.940556).as_vector
	SYD = Blip(-33.946111, 151.177222).as_vector
	PRY = Blip(-25.653611, 28.224167).as_vector
	SVO = Blip(55.972778, 37.414722).as_vector
	SIN = Blip(1.359167, 103.989444).as_vector

	A = Blip(0.0, 0.0).as_vector
	B = Blip(30.0, 0.0).as_vector
	M = Blip(5.0, 10.0).as_vector

	u = SegmentArc(A, B, -2500000.0, False)
	u = SegmentArc(A, B, 2500000.0, False)
	u = SegmentArc(A, B, 2500000.0, True).compute_sta(M)
	u = SegmentArc(A, B, -2500000.0, True)
	# u

	#u = SegmentArc(LIS, SVO, 2500000.0, True)
