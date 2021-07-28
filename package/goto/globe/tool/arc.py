#!/usr/bin/env python3

""" arcs are part of a cicle which are always inferior or equal to half of a circle (no large arc) """

import math

	def arc_find_center(A, B, radius, force=False) :

		DISABLED !! use ArcTo, directly

		A = A.normalized()
		B = B.normalized()

		angle_ab = A.angle_to(B)

		radius_min = angle_ab / 2
		radius_max = math.pi / 2

		w = math.copysign(1.0, radius)

		if force :
			radius = w * max(radius_min, min(abs(radius), radius_max))

		if radius_min <= radius <= radius_max :
			I = (A + B).normalized()
			Q = w * (B @ A).normalized()

			t = math.acos(math.cos(radius) / (A * I))

			C = I * math.cos(t) + Q * math.sin(t)

			return C
		else :
			raise ValueError(f"the radius does not fit the bounds: {radius_min} < {radius} < {radius_max}")
