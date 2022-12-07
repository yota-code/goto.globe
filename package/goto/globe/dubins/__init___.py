#!/usr/bin/env python3

import math

import geometrik.threed as g3d
import goto.globe

from goto.globe.plot import GlobePlotMpl

class Dubincz_CLC() :
	def __init__(self, Az: g3d.Vector, Ay: g3d.Vector, Ar: float, Aw: int, Bz: g3d.Vector, By: g3d.Vector, Br: float, Bw: int) :
		self.Az = Az # center of the initial circle
		self.Ay = Ay # element of the frame which points toward the entry point
		self.Ar = Ar # radius of the initial circle (in radians)
		self.Aw = Aw # 1 if turn right, -1 if turn left

		self.Bz = Bz # center of the final circle
		self.By = By # element of the frame which points toward the exit point
		self.Br = Br # radius of the final circle (in radians)
		self.Bw = Bw # 1 if turn right, -1 if turn left

		self.AB = self.Az.angle_to(self.Bz)

		# this frame describe the transition between A and B
		self.Cz = (self.Az @ self.Bz).normalized() # normal to the great circle which contains A and B, on the left
		self.Cx = self.Az
		self.Cy = self.Cz @ self.Cx

		print(self.Ar, self.Br, self.AB)

	def resolve(self) :
		if self.Bw * self.Aw > 0 :
			if self.AB < math.pi / 2 :
				theta = self.Aw * self.theta_direct()
				psi = math.asin(math.sin(self.Ar) / math.sin(theta)) + math.pi / 2

			print(math.degrees(theta), math.degrees(psi))

			Dy = self.Cx.deflect(self.Cy, psi)
			Dz = self.Cz.deflect(Dy, theta)


		with GlobePlotMpl() as gpl :
			#gpl.add_point(self.Az, 'Az', 'r')
			#gpl.add_point(self.Ay, 'Ay', 'r')
			gpl.add_circle(self.Az, self.Ar, 'r')
			#gpl.add_point(self.Bz, 'Bz', 'b')
			#gpl.add_point(self.By, 'By', 'b')
			gpl.add_circle(self.Bz, self.Br, 'b')
			gpl.add_line(self.Az, self.Bz, 'g')
			gpl.add_great_circle(Dz, 'magenta')

			gpl.add_point(self.Cx, 'Cx', 'cyan')
			gpl.add_point(self.Cy, 'Cy', 'cyan')
			gpl.add_point(self.Cz, 'Cz', 'cyan')

			#gpl.add_point(Dx, 'Dx', 'orange')
			gpl.add_point(Dy, 'Dy', 'orange')
			gpl.add_point(Dz, 'Dz', 'orange')

	def theta_direct(self) :
		Ar, Br, AB = self.Ar, self.Br, self.AB
		return math.asin(
			(math.sin(Ar)/math.sin(AB) - math.sin(Br)/math.tan(AB)) /
			math.sqrt(
				(-math.sin(Ar) + math.sin(Br)*math.cos(AB))**2 /
				(math.sin(Ar)**2 - 2*math.sin(Ar)*math.sin(Br)*math.cos(AB) + math.sin(Br)**2)
			)
		)

	def theta_crossed(self) :
		Ar, Br, AB = self.Ar, self.Br, self.AB
		return math.asin(
			(math.sin(Ar)/math.sin(AB) + math.sin(Br)/math.tan(AB)) / 
			math.sqrt(
				(math.sin(Ar) + math.sin(Br)*math.cos(AB))**2 /
				(math.sin(Ar)**2 + 2*math.sin(Ar)*math.sin(Br)*math.cos(AB) + math.sin(Br)**2)
			)
		)


class Dubincz() :
	def __init__(self, A:g3d.Vector, Ahdg:float, Arad: float, B:g3d.Vector) :
		self.A = A
		self.A


if __name__ == '__main__' :
	import goto.globe

	Az = goto.globe.Blip(0.0, -10.0).as_vector
	Ah = math.radians(45.0)
	Ar = 2000000 / goto.globe.earth_radius
	Aw = 1 # turn to the right
	Ax, Ay = Az.oriented_frame(Ah, -Aw)

	Bz = goto.globe.Blip(20.0, 20.0).as_vector
	Bh = math.radians(60.0)
	Br = 1500000 / goto.globe.earth_radius
	Bw = 1 # turn to the right
	Bx, By = Bz.oriented_frame(Bh, -Bw)

	Dubincz_CLC(Az, Ay, Ar, Aw, Bz, By, Br, Bw).resolve()

