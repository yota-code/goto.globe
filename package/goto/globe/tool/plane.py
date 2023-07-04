#!/usr/bin/env python3

import geometrik.threed as g3d

def intersection(A, B) :
	"""
	A and B are the normal vector of two planes, this function give their intersections
	"""
	A = A.normalized()
	B = B.normalized()

	return A @ B

if __name__ == '__main__' :

	pass
	# import sympy
	# Ax, Ay, Az, Bx, By, Bz, theta = sympy.symbols("Ax Ay Az Bx By Bz theta")

	# A = g3d.Vector(Ax, Ay, Az)
	# B = g3d.Vector(Bx, By, Bz)
	# U = (A + B)
	# V = (A @ B)
	# M = U.deflect(B, theta)

	# BM = (M * B).simplify()
	# print(BM)
	# sympy.pprint(BM)

	# # Z = [z.simplify() for z in sympy.solve(BM, theta)]
	# # print(Z)
	# # sympy.pprint(Z)

	# Ax, Ay, Az, Bx, By, Bz, theta = sympy.symbols("Ax Ay Az Bx By Bz theta")

	# k = 
	# 	2*Ax*Ay*Bx*By + 
	# 	2*Ax*Az*Bx*Bz +
	# 	2*Ay*Az*By*Bz +
		
	# 	2*Ax*Bx**3 +
	# 	2*Ay*By**3 +
	# 	2*Az*Bz**3 + 

	# 	2*Ay*Bx**2*By +  
	# 	2*Az*Bx**2*Bz + 
  	# 	2*Ax*Bx*By**2 +
 	# 	2*Az*By**2*Bz +
	# 	2*Ax*Bx*Bz**2 +
	# 	2*Ay*By*Bz**2 +
		
	# 	Ax**2*Bx**2 +
	# 	Ay**2*By**2 +
	# 	Az**2*Bz**2 +
		
	# 	4*Bx**2*By**2 +
	# 	4*Bx**2*Bz**2 +
	# 	4*By**2*Bz**2 +

	# 	2*By**4 +
	# 	2*Bx**4 +
	# 	2*Bz**4
	# print(k.collect(Bx).collect(By).collect(Bz))


	# z1 = 2*atan((1 - sqrt(Ax**2*Bx**2 + 2*Ax*Ay*Bx*By + 2*Ax*Az*Bx*Bz + 2*Ax*Bx**3 + 2*Ax*Bx*By**2 + 2*Ax*Bx*Bz**2 + Ay**2*By**2 + 2*Ay*Az*By*Bz + 2*Ay*Bx**2*By + 2*Ay*By**3 + 2*Ay*By*Bz**2 + Az**2*Bz**2 + 2*Az*Bx**2*Bz + 2*Az*By**2*Bz + 2*Az*Bz**3 + 2*Bx**4 + 4*Bx**2*By**2 + 4*Bx**2*Bz**2 + 2*By**4 + 4*By**2*Bz**2 + 2*Bz**4))/(Ax*Bx + Ay*By + Az*Bz + 1))
	# z2 = 2*atan((1 + sqrt(Ax**2*Bx**2 + 2*Ax*Ay*Bx*By + 2*Ax*Az*Bx*Bz + 2*Ax*Bx**3 + 2*Ax*Bx*By**2 + 2*Ax*Bx*Bz**2 + Ay**2*By**2 + 2*Ay*Az*By*Bz + 2*Ay*Bx**2*By + 2*Ay*By**3 + 2*Ay*By*Bz**2 + Az**2*Bz**2 + 2*Az*Bx**2*Bz + 2*Az*By**2*Bz + 2*Az*Bz**3 + 2*Bx**4 + 4*Bx**2*By**2 + 4*Bx**2*Bz**2 + 2*By**4 + 4*By**2*Bz**2 + 2*Bz**4))/(Ax*Bx + Ay*By + Az*Bz + 1))

# 	# BM = B.angle_to(M)

# 	# print(AM - BM)

# 	# AMB = sympy.acos(Ax*Mx + Ay*My + Az*Mz) - sympy.acos(Bx*Mx + By*My + Bz*Mz)

# 	# Z = g3d.Vector((-Ay*My - Az*Mz + By*My + Bz*Mz)/(Ax - Bx), My, Mz).normalized()

# 	# print(Z)
# 	# for i in Z.normalized() :
# 	# 	sympy.pprint(i.expand().simplify())


# 	# r = sympy.solve(AMB, [Mx, My, Mz])
# 	# print(r)

# Un = sqrt((Ax + Bx)**2 + (Ay + By)**2 + (Az + Bz)**2)
# (Ax*(Bx*Un*sin(theta) + (Ax + Bx)*cos(theta)) + Ay*(By*Un*sin(theta) + (Ay + By)*cos(theta)) + Az*(Bz*Un*sin(theta) + (Az + Bz)*cos(theta)))/(sqrt(((Bx*Un*sin(theta) + (Ax + Bx)*cos(theta))**2 + (By*Un*sin(theta) + (Ay + By)*cos(theta))**2 + (Bz*Un*sin(theta) + (Az + Bz)*cos(theta))**2)/((Ax + Bx)**2 + (Ay + By)**2 + (Az + Bz)**2))*sqrt(Ax**2 + Ay**2 + Az**2)*Un)
