#include <ctgmath>

#include "globe_common.hpp"
#include "globe_arc.hpp"

namespace globe {

	Line::Line(const Vec3 & A, const Vec3 & B) {
		this->Ax = A.normalized();
		this->Bx = B.normalized();

		this->angle = Ax.angle_to(Bx);
		this->length = this->angle * GLOBE_EARTH_RADIUS;

		this->Ay = (this->Bx @ this->Ax).normalized();
		this->Az = (this->Ax @ this->Ay)

		#ifdef GLOBE_VERBOSE

			std::cout << "Arc::Arc(" << this->Ax << ", " << this->Bx << ", " << this->aperture * GLOBE_EARTH_RADIUS << ", " << is_large_arc << ")";

		#endif
	}

	Vec3 Line::point_at(double t) {
		return this.Ax.deflect(this->Ay, t * this->angle);
	}

}
