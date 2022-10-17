#include <stdlib.h>
#include <stdio.h>

#include "globe_arc.h"


int main(int argc, char * argv[]) {

	g3d_vec_T A = g3d_vec_from_coordinates(0.0, 0.0);
	g3d_vec_T B = g3d_vec_from_coordinates(45.0, 45.0);
	g3d_vec_T M = g3d_vec_from_coordinates(40.0, 45.0);

	gbl_arc_T u = gbl_arc_from_radius(A, B, 3500000.0, false);
	g3d_vec_T P = gbl_arc_project(& u, M);

	G3D_check_vec(P, 42.935995, 48.516021);

	return EXIT_SUCCESS;
}