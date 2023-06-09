#ifndef INCLUDE_globe_arc_H
#define INCLUDE_globe_arc_H

#include "globe_threed.h"

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

} glb_arc_T;

glb_arc_T glb_arc__NEW__from_radius(g3d_vec_T A, g3d_vec_T B, double radius, bool is_large_arc) ;

g3d_vec_T glb_arc_project(glb_arc_T * self, g3d_vec_T Mx) ;
g3d_vec_T glb_arc_point_at(glb_arc_T * this, double t) ;

#endif /* #define INCLUDE_globe_arc_H */