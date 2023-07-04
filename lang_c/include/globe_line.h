#ifndef INCLUDE_globe_line_H
#define INCLUDE_globe_line_H

#include "globe_threed.h"

typedef struct {

	g3d_vec_T Ax; // starting point
	g3d_vec_T Bx; // ending point

	g3d_vec_T Cx; // rightward, perpendicular to Ax and Bx
	g3d_vec_T Az; // forward, in A

	double angle; // distance between A and B in radians
	double length; // distance between A and B in meters

} glb_line_T;

glb_line_T gb_line__NEW__(g3d_vec_T A, g3d_vec_T B) ;

g3d_vec_T glb_line_project(glb_line_T * self, g3d_vec_T Mx) ;


#endif /* #define INCLUDE_globe_line_H */