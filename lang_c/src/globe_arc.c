#include "globe_arc.h"

gbl_arc_T gbl_arc_from_radius(gbl_arc_T * self, g3d_vec_T * A, g3d_vec_T * B, double radius, bool is_large_arc) {

	g3d_vec_T Ax = g3d_normalized(A);
	g3d_vec_T Bx = g3d_normalized(B);

	double angle_ab = g3d_angle(Ax, Bx);

	float way = copysign(1.0, radius);
	double radius_eff = G3D_BOUND(fabs(radius), angle_ab / 2, M_PI_2); // effective radius, once bounded, absolute value

	g3d_vec_T Qx = g3d_normalized(g3d_add(A, B));
	g3d_vec_T Qy = g3d_lambda_product(g3d_normalzed(g3d_cross_product(B, A)), way);

	double p = acos(G3D_BOUND(cos(radius_eff) / g3d_scalar_product(Ax, Qx), -1.0, 1.0));

	g3d_vec_T Vx = g3d_composed(Qx, Qy, p);

	gbl_arc_T u = {
		
		g3d_normalized(B),
		radius_eff,
		is_large_arc,

	}


}