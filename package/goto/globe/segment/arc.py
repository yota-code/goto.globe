#!/usr/bin/env python3

import math

import goto.globe
from goto.globe.blip import Blip

import geometrik.threed as g3d

e = 6371008.7714


DEPRECATED ?

class SegmentArc() :

	def __init__(self, A:Blip, B:Blip, radius:float, is_large_arc:bool=False, debug:bool=False) :

		self.debug = debug

		self.radius = radius
		self.is_large_arc = is_large_arc

		if self.debug :
			print(f"SegmentArc(A, B, {radius}, {is_large_arc})")

		self.Ax = A.as_vector
		self.Bx = B.as_vector

		self.aperture = self.bounded_aperture(radius)

		self.compute_def()

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

			print(f"radius={radius} -> aperture={a_bounded}")

		return a_bounded

	def compute_def(self) :
		Ax, Bx = self.Ax, self.Bx

		w = math.copysign(1.0, self.radius)
		k = -1.0 if self.is_large_arc else 1.0
		
		# la base Q est toujours directe
		Qx = (Ax + Bx).normalized() # Qx entre Ax et Bx (vers le haut)
		Qy = (Bx @ Ax).normalized() # Qy vers la droite
		Qz = Qx @ Qy # Qz vers l'avant (de Ax vers Bx)
		
		m = math.acos(min((math.cos(self.aperture) / (Ax * Qx)), math.pi / 2.0))
		
		Cx = g3d.Vector.compose(Qx, Qy, w * k * m)
		Cz = Qz
		Cy = w * Cx @ Cz

		Az = (Ax @ Cx).normalized()
		Ay = (Cx @ Az)

		Bz = (Bx @ Cx).normalized()
		By = (Cx @ Bz)

		# sector = ( math.tau - Ay.angle_to(By, Cx) ) if is_large_arc else ( Ay.angle_to(By, Cx) )
		# sector = k * ((math.tau if is_large_arc else 0.0) - Ay.angle_to(By))
		sector = -1.0 * k * w * ((math.tau if self.is_large_arc else 0.0) - Ay.angle_to(By))

		self.Cx, self.Qz, self.sector = Cx, Qz, sector

		if self.debug :
			print(f"Ax = {Blip.from_vector(self.Ax)}")
			print(f"Bx = {Blip.from_vector(self.Bx)}")
			print(f"Qx = {Blip.from_vector(Qx)}")
			print(f"Qy = {Blip.from_vector(Qy)}")
			print(f"Qz = {Blip.from_vector(Qz)}")
			print(f"Cx = {Blip.from_vector(Cx)}")
			print(f"m={m} k={k} w={w}")
			#self.plot_def()

	def plot_def(self, pth=None) :
		from goto.globe.plot import GlobePlotMpl

		w = math.copysign(1.0, self.sector)
		k = -1.0 if abs(self.sector) > math.pi else 1.0

		with GlobePlotMpl(pth) as plt :
			plt.add_point(self.Ax, "Ax", "orange")
			plt.add_point(self.Bx, "Bx", "cyan")
			plt.add_point(self.Cx, "Cx", "magenta")
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

	def compute_sta(self, M:Blip) :

		self.Mx = M.as_vector

		# print("sector:", math.degrees(self.sector))

		is_large_arc = abs(self.sector) > math.pi

		w = math.copysign(1.0, self.sector)
		k = -1.0 if is_large_arc else 1.0

		self.Cz_raw = w * (self.Mx @ self.Cx).normalized()
		self.Cz = k * w * (self.Mx @ self.Cx).normalized()
		self.Cy = (self.Cz @ (-w * self.Cx))

		Qy = (self.Qz @ (-1.0*w * self.Cx))
		self.Qy = Qy

		aperture_cur = self.Mx.angle_to(self.Cx, self.Qz)

		Px = g3d.Vector.compose(self.Cx, self.Cy, k * self.aperture)

		# dev_lat = Px.angle_to(self.Mx, self.Qz)
		dev_lat = k * Px.angle_to(self.Mx, self.Cz)
		self.dev_lat = dev_lat * e

		Ny, Nz = Px.frame(g3d.v_north)

		track = self.Cz.atan2(k * Ny, k * Nz)
		# print("trk:", trk, math.degrees(trk))

		# print(dev_lat * goto.globe.earth_radius)

		self.Ap = self.Ax.project(self.Cx).normalized()
		self.Bp = self.Bx.project(self.Cx).normalized()
		self.Pp = Px.project(self.Cx).normalized()

		Aa = k * self.Ap.atan2(self.Qz, Qy)
		Pa = k * self.Pp.atan2(self.Qz, Qy)
		Ba = k * self.Bp.atan2(self.Qz, Qy)

		self.Aa, self.Pa, self.Ba = math.degrees(Aa), math.degrees(Pa), math.degrees(Ba)

		self.advance = (Pa - Aa) / (Ba - Aa)

		self.track = track
		self.Px = Px

		self.Ny_blip = goto.globe.Blip.from_vector(k * Ny)
		self.Nz_blip = goto.globe.Blip.from_vector(k * Nz)
		self.Cz_blip = goto.globe.Blip.from_vector(self.Cz)
		self.k = k
		self.w = w

		if self.debug :
			print(f"w={w} k={k}")
			print(f"track = {math.degrees(track)}")
			print(f"Px = {Blip.from_vector(self.Px)}")
			print(f"Aa = {self.Aa} Ba = {self.Ba} ... Pa = {self.Pa}")
			print(f"advance = {self.advance}")
			print(f"dev_lat = {self.dev_lat}")

			self.plot_sta()

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

		return self

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
			plt.add_point(self.Cz_raw, "Cr", "purple")

			plt.add_point(self.Qy, "Qy", "magenta")
			plt.add_point(self.Qz, "Qz", "magenta")

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


	B = Blip(0.0, 0.0)
	# #A = Blip(43.43880325227894, 5.226326085217038)
	A = Blip(45.0, 45.0)
	# #B = Blip(43.43681649080234, 5.219997634114621)
	M = Blip(40.0, 45.0)
	# #M = Blip(43.43858630342856, 5.226460832953308)
	# # u = SegmentArc(A, B, -2500000.0, False)
	# # u = SegmentArc(A, B, 2500000.0, False)
	u = SegmentArc(B, A, -3500000.0, True, True).compute_sta(M)
	u = SegmentArc(B, A, -3500000.0, False, True).compute_sta(M)
	u = SegmentArc(B, A, 3500000.0, True, True).compute_sta(M)
	u = SegmentArc(B, A, 3500000.0, False, True).compute_sta(M)
	#u = SegmentArc(A, B, 308.5912, False).compute_sta(M)
	# u = SegmentArc(A, B, -2500000.0, True)
	# u

	#u = SegmentArc(LIS, SVO, 2500000.0, True)

	# A = Blip(43.43961707558193, 5.226917705594136)
	# B = Blip(43.43942536940763, 5.220000000001344)
	# M = Blip(43.43953301931469, 5.226843793105218)
	# u = SegmentArc(A, B, 280.42337, False).compute_sta(M)
