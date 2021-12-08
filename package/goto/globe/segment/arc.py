#!/usr/bin:env python3

import math

import goto.globe
import geometrik.threed as g3d


class SegmentArc() :

	debug = True

	def __init__(self, Ax: g3d.Vector, Bx: g3d.Vector, radius: float, is_large_arc:bool=False) :

		self.Ax = Ax
		self.Bx = Bx
		self.radius = radius
		self.is_large_arc = is_large_arc

		self.aperture = self.bounded_aperture()

		self.Cx, self.Qz = self.compute_def()

	def bounded_aperture(self) :
		Ax, Bx, radius = self.Ax, self.Bx, self.radius

		a_mini = Ax.angle_to(Bx) / 2.0

		a_abs = abs(radius / goto.globe.earth_radius)
		a_maxi = math.pi / 2.0
		a_bounded = max(a_mini, min(a_abs, a_maxi))

		if self.debug :
			if a_abs != a_bounded :
				print(f"{a_mini} < ({a_abs} -> {a_bounded}) < {a_maxi}")
			else :
				print(f"{a_mini} < ({a_bounded}) < {a_maxi}")


		return math.copysign(a_bounded, radius)

	def compute_def(self) :
		Ax, Bx, radius, is_large_arc = self.Ax, self.Bx, self.radius, self.is_large_arc

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

		sector = Ay.angle_to(By)

		if self.debug :

			from goto.globe.plot import GlobePlotMpl

			with GlobePlotMpl() as plt :
				plt.add_point(Ax, "Ax", "orange")
				plt.add_point(Bx, "Bx", "cyan")
				plt.add_point(Qx, "Qx", "r")
				# plt.add_point(Qy, "Qy", "g")
				# plt.add_point(Qz, "Qz", "b")
				plt.add_point(Ay, "Ay", "r")
				plt.add_point(By, "By", "r")
				plt.add_point(Cx, "Cx", "magenta")
				plt.add_point(Cy, "Cy", "purple")
				plt.add_point(Cz, "Cz", "k")
				plt.add_signed_arc(Ax, Bx, Cx, w)

				print(f"sector = {sector}")
			
		return Cx, Qz

	def compute_sta(self, Mx) :
		pass



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

	u = SegmentArc(LIS, SVO, 3000000.0, False)
	u = SegmentArc(LIS, SVO, 3000000.0, True)
