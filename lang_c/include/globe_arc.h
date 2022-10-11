


typedef struct {

	g3d_vec_T Ax;
	g3d_vec_T Bx;

	double radius;
	bool is_large_arc;

	g3d_vec_T Vx; // center of the circle
	g3d_vec_T Ay;
	g3d_vec_T By;

	double _angle;
	double _aperture;

} gbl_arc_T;