#include "globe_line.h"

// prefix is glb_line_

glb_line_T gb_line__NEW__(g3d_vec_T A, g3d_vec_T B) {

	g3d_vec_T Ax = g3d_normalize(A);
	G3D_print_vec(Ax);
	g3d_vec_T Bx = g3d_normalize(B);
	G3D_print_vec(Bx);

	double angle = g3d_angle(Ax, Bx);
	double length = angle * GLB_EARTH_RADIUS;

	g3d_vec_T Cx = g3d_normalize(g3d_cross_product(Bx, Ax));
	g3d_vec_T Az = g3d_cross_product(Ax, Cx);

	glb_line_T segment = {
		Ax,
		Bx,
		Cx,
		Az,
		angle,
		length
	};

	return segment;
	
}

g3d_vec_T glb_line_project(glb_line_T * this, g3d_vec_T Mx) {

	g3d_vec_T Px = g3d_normalize(g3d_project_normal(Mx, this->Cx));

	return Px;

}

g3d_vec_T glb_line_point_at(glb_line_T * this, double t) {
	// t should be in [0.0, 1.0], if not, results will be on the circle but not on the line

	g3d_vec_T Px = g3d_deflect(this->Ax, this->Az, this->angle * t);

	G3D_print_vec(Px);

	return Px;
	
}