#include <stdlib.h>
#include <stdio.h>

#include "globe_arc.h"

int main(int argc, char * argv[]) {

	g3d_vec_T A = g3d_vec_from_coordinates(85.0, 0.0);
	g3d_vec_T B = g3d_vec_from_coordinates(85.0, 90.0);

	double radius = (M_PI * 5.0 / 180.0) * GLB_EARTH_RADIUS;

	glb_arc_T u = glb_arc__NEW__from_radius(A, B, radius, false);

	for (int i=0 ; i <= 16 ; i ++) {
		double p = ((double)(i)) / 16.0;
		glb_arc_point_at(& u, p);
	}

	return EXIT_SUCCESS;
	
}