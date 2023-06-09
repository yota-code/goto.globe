#ifndef INCLUDE_globe_threed_H
#define INCLUDE_globe_threed_H

#include <stdlib.h>
#include <stdio.h>

#include <stdint.h>
#include <stdbool.h>

#include <tgmath.h>

#ifndef M_PI
	#define M_PI (0x3.243f6a8885a308d313198a2e03707344a4093822299f31d0082efa98ec4e6c89p0)
#endif

#define GLB_EARTH_RADIUS (6371008.7714)

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

#define G3D_REAL_IS_CLOSE(x, y, epsilon) ( fabs((x) - (y)) < ((fabs(x) + fabs(y)) * (epsilon)) )

#define G3D_TO_RADIANS(x) (M_PI * (x) / 180.0)
#define G3D_TO_DEGREES(x) (180.0 * (x) / M_PI)

#define G3D_BOUND_UP(x, upper_bound) ( ((upper_bound < (x)) ? (upper_bound) : (x)) )
#define G3D_BOUND_LOW(x, lower_bound) ( (((x) < lower_bound) ? (lower_bound) : (x)) )

#define G3D_BOUND(x, lower_bound, upper_bound) ( \
	(lower_bound < upper_bound) ? ( \
		G3D_BOUND_LOW(G3D_BOUND_UP(x, upper_bound), lower_bound) \
	) : ((lower_bound + upper_bound) / 2.0) \
)

#define G3D_BLIP_IS_CLOSE(a, b) ( \
	G3D_REAL_IS_CLOSE((a).lat, (b).lat, 1e-5) && \
	G3D_REAL_IS_CLOSE((a).lon, (b).lon, 1e-5) \
)

#define G3D_VEC_IS_CLOSE(u, v) ( \
	G3D_REAL_IS_CLOSE((u).x, (v).x, 1e-8) && \
	G3D_REAL_IS_CLOSE((u).y, (v).y, 1e-8) && \
	G3D_REAL_IS_CLOSE((u).z, (v).z, 1e-8) \
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

g3d_vec_T g3d_normalize(g3d_vec_T u) ;

g3d_vec_T g3d_deflect(g3d_vec_T Ux, g3d_vec_T Uy, double angle) ;

g3d_vec_T g3d_project_tangent(g3d_vec_T u, g3d_vec_T n) ;
g3d_vec_T g3d_project_normal(g3d_vec_T u, g3d_vec_T n) ;

g3d_vec_T g3d_add(g3d_vec_T u, g3d_vec_T v) ;

#ifdef NDEBUG
	#define G3D_print_vec(u)
	#define G3D_check_vec(u, lat, lon)
	#define G3D_print_float(x)
#else
	#define G3D_print_vec(u) { \
		g3d_blip_T b = g3d_vec_to_blip(u); \
		printf(#u " = blip(lat=%f, lon=%f) vec(x=%f, y=%f, z=%f)\n", b.lat, b.lon, u.x, u.y, u.z); \
	}
	#define G3D_print_float(x) { \
		printf(#x " = %f\n", x); \
	}
	#define G3D_print_angle(x) { \
		printf(#x " = %f rad / %f° / %e m\n", (x), 180.0 * (x) / M_PI, (x) * GLB_EARTH_RADIUS); \
	}
	#define G3D_check_vec(u, c_lat, c_lon) { \
		g3d_blip_T b = g3d_vec_to_blip(u); \
		g3d_blip_T c = {c_lat, c_lon}; \
		printf(#u " = blip(lat=%f, lon=%f) vec(x=%f, y=%f, z=%f) %s\x1b[0m blip(lat=%f, lon=%f)\n", b.lat, b.lon, u.x, u.y, u.z, (G3D_BLIP_IS_CLOSE(b, c)) ? ("\x1b[32mOK") : ("\x1b[31mKO"), c.lat, c.lon); \
	}
	#define G3D_check_vec_is_close(u, v) { \
		printf(#u " = vec(x=%f, y=%f, z=%f)" #v " = vec(x=%f, y=%f, z=%f) %s\n", u.x, u.y, u.z, v.x, v.y, v.z, (G3D_VEC_IS_CLOSE(u, v)) ? ("\x1b[32mOK") : ("\x1b[31mKO")); \
	}
#endif

#endif /* INCLUDE_globe_threed_H */