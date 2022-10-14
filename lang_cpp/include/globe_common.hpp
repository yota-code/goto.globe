#ifndef INCLUDE_globe_common_H
#define INCLUDE_globe_common_H

#define GLOBE_EARTH_RADIUS (6371008.7714)

#define GLOBE_TO_RADIANS(x) (M_PI_2 * (x) / 90.0)
#define GLOBE_TO_DEGREES(x) (90.0 * (x) / M_PI_2)

#define GLOBE_BOUND_UP(x, upper_bound) ( ((upper_bound < (x)) ? (upper_bound) : (x)) )
#define GLOBE_BOUND_LOW(x, lower_bound) ( (((x) < lower_bound) ? (lower_bound) : (x)) )

#define GLOBE_BOUND(x, lower_bound, upper_bound) ( \
	(lower_bound < upper_bound) ? ( \
		GLOBE_BOUND_LOW(GLOBE_BOUND_UP(x, upper_bound), lower_bound) \
	) : ((lower_bound + upper_bound) / 2.0) \
)

#endif /* INCLUDE_globe_common_H */
