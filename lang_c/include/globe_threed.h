#ifndef INCLUDE_globe_threed_H
#define INCLUDE_globe_threed_H

#include <stdlib.h>
#include <stdio.h>

#include <stdint.h>
#include <stdbool.h>

typedef struct {
	double x;
	double y;
	double z;

	bool is_unit;
} g3d_vec_T;

typedef struct {
	double lat;
	double lon;
} g3d_blip_T;

#define G3D_TO_RADIANS(x) (M_PI_2 * (x) / 90.0)
#define G3D_TO_DEGREES(x) (90.0 * (x) / M_PI_2)

#define G3D_BOUND_UP(x, upper_bound) ( ((upper_bound < (x)) ? (upper_bound) : (x)) )
#define G3D_BOUND_LOW(x, lower_bound) ( (((x) < lower_bound) ? (lower_bound) : (x)) )

#define G3D_BOUND(x, lower_bound, upper_bound) ( \
	(lower_bound < upper_bound) ? ( \
		G3D_BOUND_LOW(G3D_BOUND_UP(x, upper_bound), lower_bound) \
	) : ((lower_bound + upper_bound) / 2.0) \
)

g3d_vec_T g3d_vec_from_coordinates(double latitude, double longitude) ;
g3d_vec_T g3d_blip_to_vec(g3d_blip_T b) ;
g3d_blip_T g3d_vec_to_blip(g3d_vec_T v) ;

g3d_vec_T g3d_cross_product(g3d_vec_T u, g3d_vec_T v) ;
double g3d_scalar_product(g3d_vec_T u, g3d_vec_T v) ;
g3d_vec_T g3d_lambda_product(g3d_vec_T u, double lambda) ;


double g3d_angle(g3d_vec_T u, g3d_vec_T v) ;
double g3d_angle_signed(g3d_vec_T u, g3d_vec_T v, g3d_vec_T w) ;

double g3d_norm_2(g3d_vec_T u) ;
double g3d_norm(g3d_vec_T u) ;

g3d_vec_T g3d_normalized(g3d_vec_T u) ;

g3d_vec_T g3d_composed(g3d_vec_T Ux, g3d_vec_T Uy, double angle) ;

g3d_vec_T g3d_add(g3d_vec_T u, g3d_vec_T v) ;

#ifdef NDEBUG
	#define G3D_print_vec(u)
	#define G3D_print_float(x)
#else
	#define G3D_print_vec(u) { \
		g3d_blip_T b = g3d_vec_to_blip(u); \
		printf(#u " = blip(lat=%f, lon=%f) vec(x=%f, y=%f, z=%f)\n", b.lat, b.lon, u.x, u.y, u.z); \
	}
	#define G3D_print_float(x) { \
		printf(#x " = %f\n", x); \
	}

#endif


#endif /* INCLUDE_globe_threed_H */