#include <stdlib.h>
#include <stdio.h>

#include <tgmath.h>

#include "globe_threed.h"

/* contains the definitions for both vec3 and blip */

g3d_vec_T g3d_vec_from_coordinates(double latitude, double longitude) {

	g3d_blip_T b = {
		latitude,
		longitude
	};

	return g3d_blip_to_vec(b);
	
}

g3d_vec_T g3d_blip_to_vec(g3d_blip_T b) {

	double theta = (M_PI / 2) - G3D_TO_RADIANS(b.lat);
	double phi = G3D_TO_RADIANS(b.lon);

	double sin_theta = sin(theta);
	double cos_theta = cos(theta);

	double sin_phi = sin(phi);
	double cos_phi = cos(phi);

	g3d_vec_T u = {
		sin_theta * cos_phi,
		sin_theta * sin_phi,
		cos_theta,
		true
	};

	return u;

}

g3d_blip_T g3d_vec_to_blip(g3d_vec_T v) {

	double theta = acos(v.z);
	double phi = atan2(v.y, v.x);

	g3d_blip_T b = {
		G3D_TO_DEGREES(M_PI_2 - theta),
		G3D_TO_DEGREES(phi)
	};

	return b;

}

g3d_vec_T g3d_cross_product(g3d_vec_T u, g3d_vec_T v) {

	g3d_vec_T w = {
		(u.y * v.z) - (u.z * v.y),
		(u.z * v.x) - (u.x * v.z),
		(u.x * v.y) - (u.y * v.x),
		false
	};

	return w;

}

g3d_vec_T g3d_lambda_product(g3d_vec_T u, double lambda) {

	g3d_vec_T w = {
		u.x * lambda,
		u.y * lambda,
		u.z * lambda,
		false
	};

	return w;

}

double g3d_angle(g3d_vec_T u, g3d_vec_T v) {
	
	double c = g3d_scalar_product(u, v) / (g3d_norm(u) * g3d_norm(v));
	return acos(G3D_BOUND(c, -1.0, 1.0));
	
}

double g3d_angle_signed(g3d_vec_T u, g3d_vec_T v, g3d_vec_T w) {
	
	double c = g3d_scalar_product(u, v) / (g3d_norm(u) * g3d_norm(v));
	double s = g3d_scalar_product(g3d_cross_product(u, v), w);
	return copysign(acos(G3D_BOUND(c, -1.0, 1.0)), s);
	
}


double g3d_scalar_product(g3d_vec_T u, g3d_vec_T v) {

	return (u.x * v.x) + (u.y * v.y) + (u.z * v.z);

}

double g3d_norm_2(g3d_vec_T u) {

	return g3d_scalar_product(u, u);

}

double g3d_norm(g3d_vec_T u) {

	return (u.is_unit) ? (1.0) : (sqrt(g3d_norm_2(u)));

}

g3d_vec_T g3d_add(g3d_vec_T u, g3d_vec_T v) {

	g3d_vec_T w = {
		u.x + v.x,
		u.y + v.y,
		u.z + v.z,
		false
	};

	return w;

}

g3d_vec_T g3d_composed(g3d_vec_T Ux, g3d_vec_T Uy, double angle) {

	return g3d_add(
		g3d_lambda_product(Ux, cos(angle)),
		g3d_lambda_product(Uy, sin(angle))
	);

}


g3d_vec_T g3d_normalized(g3d_vec_T u) {

	if (u.is_unit) {
		return u;
	}

	double n = g3d_norm(u);

	g3d_vec_T w = {
		u.x / n,
		u.y / n,
		u.z / n,
		true
	};

	return w;

}
