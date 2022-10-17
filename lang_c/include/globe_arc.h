#ifndef INCLUDE_globe_arc_H
#define INCLUDE_globe_arc_H

#include "globe_threed.h"

#define GLB_EARTH_RADIUS (6371008.7714)

typedef struct {

	g3d_vec_T Ax;
	g3d_vec_T Bx;

	double radius;
	bool is_large_arc;

	g3d_vec_T Cx; // center of the circle
	g3d_vec_T Az;
	g3d_vec_T Bz;

	double angle;
	double aperture;
	double sector;
	double length;

} gbl_arc_T;

gbl_arc_T gbl_arc_from_radius(g3d_vec_T A, g3d_vec_T B, double radius, bool is_large_arc) ;

g3d_vec_T gbl_arc_project(gbl_arc_T * self, g3d_vec_T Mx) ;


#endif /* #define INCLUDE_globe_arc_H */