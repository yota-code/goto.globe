#ifndef INCLUDE_globe_line_H
#define INCLUDE_globe_line_H

#include <iostream>

#include "globe_vec3.hpp"

namespace globe {

	class Line {

		public:

			Vec3 Ax; // point at the beginning of the line
			Vec3 Bx; // point at the end of the line

			Vec3 Ay; // vector oriented rightward, perpendicular to the trajectory
			Vec3 Az; // vector oriented forward, perpendicular to Ax and Ay

			double angle; // distance between A and B in radians

			Line(const Vec3 & A, const Vec3 & B);
			Line(const Blip & A, const Blip & B);

			Vec3 point_at(double t);
			Vec3 projected(const Vec3 & M);

			double length();

	};

}

#endif /* INCLUDE_globe_line_H */
