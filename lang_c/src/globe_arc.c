#include "globe_arc.h"

// prefix is glb_arc_

glb_arc_T glb_arc__NEW__from_radius(g3d_vec_T A, g3d_vec_T B, double radius, bool is_large_arc) {

	g3d_vec_T Ax = g3d_normalize(A);
	G3D_print_vec(Ax);
	g3d_vec_T Bx = g3d_normalize(B);
	G3D_print_vec(Bx);

	double angle = g3d_angle(Ax, Bx);
	double aperture = G3D_BOUND(fabs(radius) / GLB_EARTH_RADIUS, angle / 2.0, M_PI / 2.0);

	double w = copysign(1.0, radius);
	double k = (is_large_arc) ? (-1.0) :(1.0);
	double d = (is_large_arc) ? (2.0 * M_PI) : (0.0);

	g3d_vec_T Qx = g3d_normalize(g3d_add(Ax, Bx));
	G3D_print_vec(Qx);
	g3d_vec_T Qy = g3d_normalize(g3d_cross_product(B, A));
	G3D_print_vec(Qy);

	double m = acos(G3D_BOUND(cos(aperture) / g3d_scalar_product(Ax, Qx), -1.0, 1.0));
	G3D_print_float(m);
	g3d_vec_T Cx = g3d_deflect(Qx, Qy, w * k * m);
	G3D_print_vec(Cx);

	G3D_print_angle(g3d_angle(Ax, Cx));
	G3D_print_angle(g3d_angle(Bx, Cx));
	G3D_print_angle(aperture);

	// vectors going forward, in A and B
	g3d_vec_T Az = g3d_lambda_product(g3d_normalize(g3d_cross_product(Ax, Cx)), w);
	g3d_vec_T Bz = g3d_lambda_product(g3d_normalize(g3d_cross_product(Bx, Cx)), w);

	double sector = -1.0 * k * w * (d - g3d_angle(Az, Bz));
	G3D_print_float(sector);
	double length = sector * sin(aperture) * GLB_EARTH_RADIUS;
	G3D_print_float(length);

	glb_arc_T u = {
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

g3d_vec_T glb_arc_project(glb_arc_T * this, g3d_vec_T Mx) {

	double w = copysign(1.0, this->sector);
	double k = (this->is_large_arc) ? (-1.0) :(1.0);

	g3d_vec_T Cz = g3d_lambda_product(g3d_normalize(g3d_cross_product(Mx, this->Cx)), k * w);
	g3d_vec_T Cy = g3d_cross_product(Cz, g3d_lambda_product(this->Cx, -w));

	G3D_print_vec(this->Cx);
	G3D_print_vec(Cy);
	G3D_print_vec(Cz);

	g3d_vec_T Px = g3d_deflect(this->Cx, Cy, k * this->aperture);

	G3D_print_vec(Px);

	return Px;

}

g3d_vec_T glb_arc_point_at(glb_arc_T * this, double t) {
	// t should be in [0.0, 1.0], if not, results will be on the circle but not on the arc

	double w = copysign(1.0, this->radius);

	g3d_vec_T Ay = g3d_lambda_product(g3d_cross_product(this->Cx, this->Az), w);
	g3d_vec_T Cy = g3d_deflect(Ay, this->Az, t * this->sector);

	g3d_vec_T Px = g3d_deflect(this->Cx, Cy, fabs(this->radius));

	G3D_print_vec(Px);

	return Px;
}