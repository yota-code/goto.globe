#!/usr/bin/env python3

import math

import geometrik.threed as g3d
import goto.globe

from goto.globe.plot import GlobePlotMpl

class Dubincc_CLC() :
	def __init__(self, Az: g3d.Vector, Ax: g3d.Vector, Ar: float, Aw: int, Bz: g3d.Vector, Bx: g3d.Vector, Br: float, Bw: int) :
		self.Az = Az # center of the initial circle
		self.Ax = Ax # element of the frame which points toward the entry point
		self.Ar = Ar # radius of the initial circle (in radians)
		self.Aw = Aw # 1 if turn right, -1 if turn left
		self.Ay = -self.Aw * (self.Az @ self.Ax).normalized()

		self.Bz = Bz # center of the final circle
		self.Bx = Bx # element of the frame which points toward the exit point
		self.Br = Br # radius of the final circle (in radians)
		self.Bw = Bw # 1 if turn right, -1 if turn left
		self.By = -self.Bw * (self.Bz @ self.Bx).normalized()

		self.AB = self.Az.angle_to(self.Bz)

		# this frame describe the transition between A and B
		self.Cz = (self.Az @ self.Bz).normalized() # normal to the great circle which contains A and B, on the left
		self.Cx = self.Az
		self.Cy = self.Cz @ self.Cx

		self.compute_points()
		self.distance = self.compute_distance()

	def compute_points(self) :
		if self.Bw * self.Aw > 0 :
			print("DIRECT", self.Bw, self.Aw)
			u = 1 if self.AB < math.pi / 4 else -1
			theta = self.Aw * self.theta_direct()
			# theta = self.Aw * self.theta()
			psi = u * (self.Aw *  math.asin(math.sin(self.Ar) / math.sin(theta)) + math.pi / 2)
		else :
			print("CROSSED", self.Bw, self.Aw)
			theta = self.Aw * self.theta_crossed()
			# theta = self.Aw * self.theta()
			psi = self.Aw *  math.asin(math.sin(self.Ar) / math.sin(theta)) + math.pi / 2

		print("direct", self.theta_direct(), "crossed", self.theta_crossed(), self.theta())

		Dy = self.Cx.deflect(self.Cy, psi)
		Dz = self.Cz.deflect(Dy, theta)

		self.E = self.Az.project_normal(Dz).normalized() # end of the first circle, start of the line
		self.F = self.Bz.project_normal(Dz).normalized() # start of the second circle, end of the line

		assert(abs(self.Az.angle_to(self.E) - self.Ar) < 0.25 / goto.globe.earth_radius)
		assert(abs(self.Bz.angle_to(self.F) - self.Br) < 0.25 / goto.globe.earth_radius)

	def compute_distance(self) :

		self.e = ( self.E.project_normal(self.Az).atan2(self.Ay, self.Ax)) % math.tau
		self.f = (-self.F.project_normal(self.Bz).atan2(self.By, self.Bx)) % math.tau
		self.d = self.E.angle_to(self.F)

		return math.sin(self.Ar) * self.e + self.d + math.cos(self.Br) * self.f

	def plot(self) :

		I = self.Az.deflect(self.Ax, self.Ar)
		O = self.Bz.deflect(self.Bx, self.Br)

		# with GlobePlotMpl(f"distance = {self.distance:.3g}", pth=f"save_{'L' if self.Aw < 0 else 'R'}S{'L' if self.Bw < 0 else 'R'}.png") as gpl :
		with GlobePlotMpl(f"distance = {self.distance:.3g}") as gpl :
			# gpl.add_point(self.Ax, 'Ax', 'r')
			# gpl.add_point(self.Ay, 'Ay', 'g')
			gpl.add_point(self.Az, 'Az', 'b')

			gpl.add_point(self.Bx, 'Bx', 'r')
			gpl.add_point(self.By, 'By', 'g')
			gpl.add_point(self.Bz, 'Bz', 'b')

			gpl.add_circle(self.Az, self.Ar, 'cyan')
			# #gpl.add_point(self.Bz, 'Bz', 'b')
			# #gpl.add_point(self.Bx, 'Bx', 'b')
			gpl.add_circle(self.Bz, self.Br, 'cyan')
			# gpl.add_line(self.Az, self.Bz, 'g')
			# gpl.add_great_circle(Dz, 'magenta')

			# gpl.add_point(self.Cx, 'Cx', 'cyan')
			# gpl.add_point(self.Cy, 'Cy', 'cyan')
			# gpl.add_point(self.Cz, 'Cz', 'cyan')

			# #gpl.add_point(Dx, 'Dx', 'orange')
			# gpl.add_point(Dy, 'Dy', 'orange')
			# gpl.add_point(Dz, 'Dz', 'orange')

			gpl.add_point(I, 'I', 'purple')
			gpl.add_point(O, 'O', 'purple')
			gpl.add_point(self.F, 'F', 'k')

			gpl.add_signed_arc(I, self.E, self.Az, self.Aw)
			gpl.add_line(self.E, self.F)
			gpl.add_signed_arc(self.F, O, self.Bz, self.Bw)

	# def plot(self) :

	# 	I = self.Az.deflect(self.Ax, self.Ar)
	# 	O = self.Bz.deflect(self.Bx, self.Br)

	# 	w = -1
	# 	Ax, Bx, Cx = self.F, O, self.Bz

	# 	Az = w * (Ax @ Cx).normalized()
	# 	Ay = w * (Cx @ Az)

	# 	Bz = w * (Bx @ Cx).normalized()
	# 	By = w * (Cx @ Bz)


	# 	with GlobePlotMpl(f"distance = {self.distance:.3g}") as gpl :
	# 		gpl.add_circle(Cx, self.Br, 'magenta')
	# 		gpl.add_point(Cx, 'Cx', 'orange')
	# 		gpl.add_point(Ax, 'Ax', 'r')
	# 		gpl.add_point(Ay, 'Ay', 'g')
	# 		gpl.add_point(Az, 'Az', 'b')
	# 		gpl.add_point(O, 'O', 'k')
			
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

	def theta(self) :
		Ar, Br, AB = self.Ar, self.Br, self.AB
		x = math.copysign(1.0, self.Bw * self.Aw)
		return math.asin(
			(math.sin(Ar)/math.sin(AB) - x*math.sin(Br)/math.tan(AB)) / 
			math.sqrt(
				(math.sin(Br)*math.cos(AB) - x*math.sin(Ar))**2 /
				(math.sin(Ar)**2 - x*2*math.sin(Ar)*math.sin(Br)*math.cos(AB) + math.sin(Br)**2)
			)
		)




def Dubincc(I:goto.globe.Blip, Ah:float, Av: float, O:goto.globe.Blip, Bh: float, Bv: float) :

	phi_max = 24.0

	Ar = Av**2 / ( goto.globe.earth_gravity * math.tan(math.radians(phi_max)) ) # TODO: on devrait calculer le véritable rayon géodésique du virage (cf scade)
	Br = Av**2 / ( goto.globe.earth_gravity * math.tan(math.radians(phi_max)) )
		
	for Aw in [-1, 1] :
		for Bw in [-1, 1] :
			Iz = I.as_vector
			Ix, Iy = Iz.oriented_frame(math.radians(Ah), Aw)
			Az = Iz.deflect(Iy, Ar)
			
			Oz = O.as_vector
			Ox, Oy = Oz.oriented_frame(math.radians(Bh), Bw)
			Bz = Oz.deflect(Oy, Br)



if __name__ == '__main__' :
	import goto.globe

	Az = goto.globe.Blip(-5.0, -10.0).as_vector
	Ah = math.radians(45.0)
	Ar = 2000000 / goto.globe.earth_radius
	# Aw = -1 # turn to the right

	Bz = goto.globe.Blip(10.0, 50.0).as_vector
	Bh = math.radians(60.0)
	Br = 1500000 / goto.globe.earth_radius
	# Bw = -1 # turn to the right

	for Aw in [-1, 1] :
		for Bw in [-1, 1] :
			Ax, Ax = Az.oriented_frame(Ah, -Aw)
			Bx, Bx = Bz.oriented_frame(Bh, -Bw)
			Dubincc_CLC(Az, Ax, Ar, Aw, Bz, Bx, Br, Bw).plot()

