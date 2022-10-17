#include <tgmath.h>

#include "globe_arc.h"

// prefix is gbl_arc_

gbl_arc_T gbl_arc_from_radius(g3d_vec_T A, g3d_vec_T B, double radius, bool is_large_arc) {

	g3d_vec_T Ax = g3d_normalized(A);
	G3D_print_vec(Ax);
	g3d_vec_T Bx = g3d_normalized(B);
	G3D_print_vec(Bx);

	double angle = g3d_angle(Ax, Bx);
	double aperture = G3D_BOUND(fabs(radius) / GLB_EARTH_RADIUS, angle / 2.0, M_PI_2);
	G3D_print_float(aperture);

	double w = copysign(1.0, radius);
	double k = (is_large_arc) ? (-1.0) :(1.0);

	g3d_vec_T Qx = g3d_normalized(g3d_add(Ax, Bx));
	G3D_print_vec(Qx);
	g3d_vec_T Qy = g3d_normalized(g3d_cross_product(B, A));
	G3D_print_vec(Qy);

	double m = acos(G3D_BOUND(cos(aperture) / g3d_scalar_product(Ax, Qx), -1.0, 1.0));
	G3D_print_float(m);
	g3d_vec_T Cx = g3d_composed(Qx, Qy, w * k * m);
	G3D_print_vec(Cx);

	g3d_vec_T Az = g3d_normalized(g3d_cross_product(Ax, Cx));
	g3d_vec_T Bz = g3d_normalized(g3d_cross_product(Bx, Cx));

	double sector = -1.0 * k * w * ( ((is_large_arc) ? (M_PI * 2.0) : (0.0)) - g3d_angle(Az, Bz) );
	G3D_print_float(sector);
	double length = sector * sin(aperture) * GLB_EARTH_RADIUS;
	G3D_print_float(length);

	gbl_arc_T u = {
		Ax,
		Bx,
		radius,
		is_large_arc,
		Cx,
		Az,
		Bz,
		angle,
		aperture,
		sector,
		length
	};

	return u;
	
}

g3d_vec_T gbl_arc_project(gbl_arc_T * self, g3d_vec_T Mx) {

	double w = copysign(1.0, self->sector);
	double k = (self->is_large_arc) ? (-1.0) :(1.0);

	g3d_vec_T Cz = g3d_lambda_product(g3d_normalized(g3d_cross_product(Mx, self->Cx)), k * w);
	g3d_vec_T Cy = g3d_cross_product(Cz, g3d_lambda_product(self->Cx, -w));
	G3D_print_vec(self->Cx);
	G3D_print_vec(Cy);
	G3D_print_vec(Cz);

	g3d_vec_T Px = g3d_composed(self->Cx, Cy, k * self->aperture);

	G3D_print_vec(Px);

	return Px;

}