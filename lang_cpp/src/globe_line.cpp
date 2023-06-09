#include <ctgmath>
#include <cassert>

#include "globe_common.hpp"
#include "globe_line.hpp"

namespace globe {

	Line::Line(const Vec3 & A, const Vec3 & B) {
		this->Ax = A.normalized();
		this->Bx = B.normalized();

		this->angle = Ax.angle_to(Bx);

		assert(1e-8 < this->angle); // no distance lower than 40cm between the two points
		assert(this->angle < (M_PI - 1e-7)); // no point at the exact antipode, with a margin of 4m

		this->Ay = (this->Bx ^ this->Ax).normalized();
		this->Az = (this->Ax ^ this->Ay);

		#ifdef GLOBE_VERBOSE
			std::cout << "Line::Line(" << this->Ax << ", " << this->Bx << ")";
		#endif
	}

	Vec3 Line::point_at(double t) {
		return this->Ax.deflect(this->Ay, t * this->angle);
	}

	Vec3 Line::projected(const Vec3 & M) {
		// return the point M projected onto the segment
		return M.project_normal(this->Ay).normalized();
	}

	double Line::length() {
		// distance between A and B in meters
		return this->angle * GLOBE_EARTH_RADIUS;
	}

}
