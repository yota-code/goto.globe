#ifndef INCLUDE_globe_arc_H
#define INCLUDE_globe_arc_H

#include "globe_vec3.hpp"

namespace globe {

	class Arc {

		public:
			Vec3 Ax; // point at the beginning of the line
			Vec3 Bx; // point at the end of the line

			double radius; // radius of the circle in radians, negative if turn left
			bool is_large_arc; // true if the arc runs for more than half a turn

			Vec3 Cx; // point at the center of the circle
			Vec3 Az; // vector oriented forward at A, perpendicular to Ax and Cx
			Vec3 Bz; // vector oriented forward at B, perpendicular to Bx and Cx

			double angle;
			double aperture;
			double sector;
			double length;

			Arc(const Vec3 & A, const Vec3 & B, double radius, bool is_large_arc);
			Arc(const Vec3 & A, const Vec3 & B, const Vec3 & C, bool is_large_arc);

			Vec3 point_at(double t);

	};

}

#endif /* INCLUDE_globe_arc_H */
