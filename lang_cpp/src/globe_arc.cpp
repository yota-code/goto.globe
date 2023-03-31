#include <ctgmath>

#include "globe_common.hpp"
#include "globe_arc.hpp"

namespace globe {

	Arc::Arc(const Vec3 & A, const Vec3 & B, double radius, bool is_large_arc) {

		this->Ax = A.normalized();
		this->Bx = B.normalized();
		this->radius = radius;
		this->is_large_arc = is_large_arc;

		// distance between A and B in radians
		this->angle = Ax.angle_to(Bx);

		// the aperture of the circle, ie. the radius expressed as an angle
		this->aperture = GLOBE_BOUND( fabs(radius) / GLOBE_EARTH_RADIUS, angle / 2.0, 1.0 );

		double w = copysign(1.0, radius);
		double k = (is_large_arc) ? (-1.0) :(1.0);
		double d = (is_large_arc) ? (2.0 * M_PI) : (0.0);

		// Qx is in the middle between Ax and Bx
		Vec3 Qx = (this->Ax + this->Bx).normalized();
		// Qy is perpendicular to AB and goes to the right
		Vec3 Qy = (this->Ax ^ this->Bx).normalized();

		double m = acos(GLOBE_BOUND(cos(aperture) / (this->Ax * Qx), -1.0, 1.0));

		// Cx is the center of the circle
		this->Cx = Qx.deflect(Qy, w * k * m);

		this->Az = w * (this->Ax ^ this->Cx).normalized();
		this->Bz = w * (this->Bx ^ this->Cx).normalized();

		this->sector = -1.0 * k * w * (d - Az.angle_to(Bz));
		this->length = sector * sin(aperture) * GLOBE_EARTH_RADIUS;

		#ifdef GLOBE_VERBOSE
			std::cout << "Arc::Arc(" << this->Ax << ", " << this->Bx << ", " << this->aperture * GLOBE_EARTH_RADIUS << ", " << is_large_arc << ")";
		#endif
	}

	Vec3 Arc::point_at(double t) {
		double w = copysign(1.0, this->radius);

		vec3 Ay = w * (this->Cx ^ this->Az);
		vec3 Cy = Ay.deflect(this->Az, t * this->sector);

		return this->Cx.deflect(Cy, fabs(this->radius));
	}


}
