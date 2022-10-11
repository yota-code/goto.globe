#ifndef INCLUDE_globe_threed_H
#define INCLUDE_globe_threed_H

typdef struct {
	double x;
	double y;
	double z;

	bool is_unit;
} g3d_vec_T;

typedef struct {
	double lat;
	double lon;
} g3d_blip_T;

#define G3D_TO_RADIANS(x) (M_PI_2 * x / 90.0)
#define G3D_TO_DEGREES(x) (90.0 * x / M_PI_2)

#define G3D_BOUND_UP(x, upper_bound) ( ((upper_bound < x) ? (upper_bound) : (x)) )
#define G3D_BOUND_LOW(x, lower_bound) ( ((x < lower_bound) ? (lower_bound) : (x)) )

#define G3D_BOUND(x, lower_bound, upper_bound) ( \
	(lower_bound < upper_bound) ? ( \
		G3D_BOUND_LOW(G3D_BOUND_UP(x, upper_bound), lower_bound) \
	) : ((lower_bound + upper_bound) / 2.0) \
)

#endif /* INCLUDE_globe_threed_H */